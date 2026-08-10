# Red Alert — Voice Control Blueprint

## Read This First: Sequencing

Your Phase 1 output pipeline is not confirmed working yet. Four test launches, no in-game speech, and the open question of whether AccessMod even appears in Options → Mods after the OneDrive path relocation.

Do not start voice input work until that is resolved. Voice input is a strictly harder problem layered on top of the same DLL, and debugging "did my voice command register" while you still cannot confirm the DLL loaded at all would be miserable. Your own open question three is the right next move: put a `Tolk_Output` call in the earliest DLL init path you can reach, so any successful load of the modded `RedAlert.dll` speaks immediately without needing a live match or a correctly triggered VOX event. That single change turns your loading question into a one-second test.

Everything below assumes that blocker is cleared first.

## The Key Finding From Your Own Recon

Your reconnaissance inventory already documents a complete voice command API without calling it that. Section 2 and 3 list the DLL export layer's player-action entry points, and your own note says they are "already event-driven one-shot calls, safe to hook directly without additional throttling."

That list is the command vocabulary:

- `Start_Construction`, `Hold_Construction`, `Cancel_Construction`
- `Start_Placement`, `Place`, `Cancel_Placement`
- `Select_Next_Unit`, `Select_Previous_Unit`
- `Selected_Guard_Mode`, `Selected_Stop`, `Scatter_Selected`
- `Create_Control_Group`, `Add_To_Control_Group`, `Toggle_Control_Group_Selection`
- `Units_Queued_Movement_Toggle`, `Team_Units_Formation_Toggle_On`

These functions take player ID and simple integer parameters. They are exactly the shape an intent parser produces. The voice layer's job is turning a spoken sentence into one of these calls, and nothing more. You do not need to touch game logic at all.

This is the same principle as the Realms of Westeros port: voice becomes a second input path feeding the handlers that already exist. Mouse and keyboard keep working throughout.

## Architecture: Out-of-Process Helper

Do not put speech recognition inside `RedAlert.dll`. The DLL is loaded by the GlyphX renderer, runs on the game's tick, and adding a microphone thread plus a recognition engine inside it invites audio device conflicts, stalls on the game loop, and a build you cannot debug.

Use a separate helper process, which is the same pattern your Civ-V-Access project already established with file-based IPC and a Python helper:

```
Microphone
   |
Python helper process  (STT + intent parsing)
   |  writes intent as a small structured record
IPC channel  (named pipe, or a file poll if you want to reuse Civ-V-Access code as-is)
   |
AccessMod inside RedAlert.dll  (reads pending intents on the game tick, calls the DLL export functions)
   |
Game state changes  ->  On_Speech  ->  Tolk  ->  speech out
```

Named pipes are the better long-term choice over file polling — lower latency, no filesystem churn during a match. But if reusing the Civ-V-Access file IPC gets you to a working prototype faster, take that; latency at the scale of a few hundred milliseconds is tolerable for a first build.

The critical rule: **the DLL side only reads and dispatches.** It should drain a queue of pending intents once per tick, translate each into an export-layer call, and never block waiting for the helper.

## The Real-Time Problem, and How to Solve It

This is the hard part, and it is why RTS ranks well below RPG in difficulty.

Speaking a command takes roughly two to four seconds end to end: recognition, parsing, IPC, dispatch. In a genre where a competent player issues several commands per second with a mouse, that gap is not something clever engineering closes. You have to change the pacing rather than fight it.

Three mechanisms, in order of how much they help:

**1. Pause-and-queue mode.** Let the player pause the simulation, speak a batch of commands, then unpause and let them all execute. This converts real-time into what other accessible strategy designs call active-time. It is the single most important accommodation, and it is the difference between the game being playable and being a stress test. Skirmish against AI is where this lands best; it does not translate to multiplayer, and that is fine.

**2. Control groups as the primary unit of command.** Your recon already found `Create_Control_Group`, `Add_To_Control_Group`, and `Toggle_Control_Group_Selection`. One spoken command controlling nine units is nine times the value per second of speech. Design the whole grammar around groups, not individual units. "Group two, attack" should be the normal way to play, and per-unit micromanagement the exception.

**3. Standing orders over moment-to-moment orders.** `Selected_Guard_Mode` and guard-area exist in the export layer already. Voice players should lean heavily on setting behavior once and letting units act autonomously, rather than re-issuing orders. Frame this in the command grammar: "group three, guard the ore field" is far more voice-efficient than repeatedly redirecting.

## The Targeting Problem

The other hard part. `Place` takes a cell. Movement and attack orders need a destination. A mouse gives you that for free; a voice does not.

Three complementary schemes, all of which should exist:

- **Named landmarks.** Register a small set of speakable locations at match start and as the game develops: my base, my ore field, the north entrance, enemy base once scouted. "Group one, move to the ore field." This is the most natural and should be the primary method.
- **Relative bearing and distance.** "Move north east," "move north east far." Coarse, but always available and needs no setup.
- **Spoken grid.** Overlay a lettered and numbered grid on the map, cells sized generously (not the engine's native cell size, which is far too fine for speech). "Move to D seven." Precise, and necessary for building placement, but requires the player to build a mental map — so it is a supplement, not the default.

Building placement specifically will need the grid, plus spoken feedback on legality, since `Calculate_Placement_Distances` already validates proximity to existing structures. "D seven is too far from your base" is a required announcement, not a nice-to-have.

## Command Grammar Sketch

Keep the same global verbs you established in the other two blueprints so the vocabulary carries across your projects: repeat, status, help, what can I say.

**Economy and production**

- "Build [structure or unit name]" — `Start_Construction`
- "Hold [name]" / "Cancel [name]" — `Hold_Construction`, `Cancel_Construction`
- "Place [name] at [grid or landmark]" — `Start_Placement` then `Place`
- "Credits" / "Power" — read from the `Get_Sidebar_State` snapshot
- "What can I build" — read the sidebar buildables list

**Selection**

- "Next unit" / "Previous unit" — `Select_Next_Unit`, `Select_Previous_Unit`
- "Select group [n]" — `Toggle_Control_Group_Selection`
- "Make group [n]" — `Create_Control_Group`
- "Add to group [n]" — `Add_To_Control_Group`
- "What is selected" — read from `Get_Player_Info_State`

**Orders**

- "Move to [landmark or grid]"
- "Attack [landmark or grid]"
- "Guard" / "Guard here" — `Selected_Guard_Mode`
- "Stop" — `Selected_Stop`
- "Scatter" — `Scatter_Selected`

**Meta**

- "Pause" / "Resume"
- "Repeat" / "Status" / "Help"

Parse with keyword matching, not a language model. The vocabulary is closed, unit and structure names come straight out of the game's own type tables, and deterministic parsing keeps latency down — which matters more here than in any of your other projects.

## Output: What Needs Diffing

Your recon flags this correctly. `On_Speech` is event-driven and free; `Get_Sidebar_State` and `Get_Player_Info_State` are per-frame polls that need diff-against-previous-frame edge detection before anything reaches Tolk.

For voice play specifically, the polled state that matters most and needs diffing:

- Selection changed — announce what is now selected and how many
- Credits crossing thresholds, not every tick
- Power transitioning between sufficient and insufficient
- A queue item completing (though `On_Speech` largely covers this already)
- Unit count in a control group dropping, which is the audio substitute for watching your army die on screen

Do not announce everything. A voice RTS that narrates continuously is unplayable, because the player cannot speak a command while the game is talking, and the microphone should be muted during narration anyway. Terseness is a functional requirement here, not a style preference.

## Build Order

1. **Clear the Phase 1 blocker.** Early-init `Tolk_Output` so DLL load is self-verifying. Nothing else proceeds until speech is confirmed in-game.
2. **Finish the output layer.** The ~16 VOX events you already mapped, plus diffed selection and credits announcements. Play the game with mouse and keyboard, listening. This alone is a shippable accessibility improvement independent of any voice input.
3. **IPC skeleton.** Helper process writes a hardcoded test intent, DLL reads it on tick and speaks "intent received." No microphone yet. Proves the channel and measures latency.
4. **Recognition into the helper.** Speak, helper transcribes and echoes back. Still no game action.
5. **Three commands only.** "Next unit," "credits," "stop." No targeting, no placement. Smallest possible slice that proves speech reaches the export layer.
6. **Pause-and-queue.** Add before expanding the vocabulary, because it changes how everything else feels and you want to design the rest around it.
7. **Landmarks and orders.** Movement and attack with named landmarks. Grid after.
8. **Production and placement.** Last, because placement is the most demanding on the targeting scheme.

## Scope Honesty

Phases 2 and 3 in your project document — RA2 memory overlay, RA3 Mod SDK — should stay output-only for now. Voice input needs a clean, documented command API to call into, which is exactly what Phase 1 has and what a memory-reading overlay does not. Injecting synthesized input into RA2 through memory writes is a substantially different and riskier engineering problem, and it is not worth opening until the RA1 voice layer is proven.

Also worth being direct: voice-controlled RTS will not play like RTS. Even with everything above working well, it will feel like a slower, more deliberate strategy game — closer to a turn-based wargame with real-time pressure than to competitive Red Alert. That is a legitimate and worthwhile thing to build. It is just not the same game, and setting that expectation in your own documentation early will save frustration when the pacing turns out the way it turns out.
