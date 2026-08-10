# Red Alert Accessibility Mod — Phase 1 Reconnaissance Inventory

Generated 2026-07-06 by a read-only pass over `F:\SteamLibrary\steamapps\common\CnCRemastered\SOURCECODE\RedAlert`. No code was modified during this pass. This is the companion inventory referenced by `red-alert-accessibility-project.md`'s "Reconnaissance Session" step.

## Architectural note

This codebase has two parallel UI code paths that both matter:

1. **Legacy/classic renderer** (`SIDEBAR.CPP`, `TAB.CPP`, `POWER.CPP`, `RADAR.CPP`) — the original DOS/Win95-era UI classes, still compiled in and used for `GAME_NORMAL` (single player/skirmish through the legacy renderer).
2. **GlyphX DLL export layer** (`DLLInterface.cpp`, `SIDEBARGlyphx.CPP`) — added for the Remastered Collection. This is a C-style API (`DLLExportClass::*`, `Sidebar_Glyphx_*`) that the external GlyphX/UE4 renderer polls and calls into. Since the mod bolts onto the DLL itself, this layer is almost certainly the best integration point — it already aggregates sidebar/queue/power/funds/selection state into single structs once per frame, and already funnels all sidebar-equivalent player actions through a small number of entry points (`Start_Construction`, `Hold_Construction`, `Cancel_Construction`, `Place`, `Select_Next_Unit`, etc.).

---

## 1. Sidebar State (buildable list / panel contents)

### Legacy renderer — `SIDEBAR.CPP`
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `SidebarClass::Which_Column(RTTIType)` | Pure lookup — no state. Determines which of the 2 columns (buildings vs. everything else) an object type belongs in. | N/A (helper) |
| `SidebarClass::Add(RTTIType type, int id, bool via_capture)` | Writes: adds a buildable entry to `Column[column]`'s list; sets `IsToRedraw`. | Event-driven (called when a factory-capable building is completed/captured) |
| `SidebarClass::Factory_Link(int factory, RTTIType, int id)` | Writes: attaches a `FactoryClass` index to the matching sidebar entry so progress can be shown. | Event-driven (called from `HouseClass::Begin_Production`) |
| `SidebarClass::Recalc(void)` | Reads/writes: sweeps all sidebar entries and removes any whose factory type no longer exists (base destroyed etc). Delegates to `StripClass::Recalc`. | Event-driven, explicitly "call rarely" (only after a factory building is lost) — not a per-tick poll |
| `SidebarClass::Activate(int control)` / `Activate_Repair` / `Activate_Upgrade` / `Activate_Demolish` | Writes: on/off state of sidebar button toggles (repair/sell/demolish mode flags). | Event-driven (button press) |
| `SidebarClass::Scroll(bool up, int column)` | Writes: scroll offset of a sidebar column. | Event-driven (scroll button click) |
| `SidebarClass::Draw_It(bool complete)` | Reads sidebar state to render it; sets `IsToRedraw=false`. | Per-frame (main draw loop), internally gated on `IsToRedraw` — good throttling model to imitate |
| `SidebarClass::AI(KeyNumType &input, int x, int y)` | Reads mouse/keyboard input; writes button toggle state (repair, zoom, sell); delegates to both columns' `AI()`. | Per-frame (called every tick from the main input/AI loop) — but only acts on discrete input values, so effectively an event dispatcher riding a per-frame call |
| `SidebarClass::StripClass::Add` | Writes: appends to `Buildables[]` array for one column/strip; speaks `VOX_NEW_CONSTRUCT`. | Event-driven |
| `SidebarClass::StripClass::AI(KeyNumType&, int, int)` | Reads factory completion state (`Has_Changed()`, `Has_Completed()`, `Is_Blocked()`) for every buildable in the strip; on completion, queues `PLACE` events and speaks `VOX_UNIT_READY`/`VOX_CONSTRUCTION`. | Per-frame poll — iterates `BuildableCount` entries every tick. **Needs throttling/edge-detection before wiring to a screen reader**, though it already only *acts* on state transitions via `Has_Changed()`. |
| `SidebarClass::StripClass::Recalc(void)` | Reads/writes: removes stale entries from one strip's `Buildables[]`. | Event-driven (called from `SidebarClass::Recalc`, not every tick) |
| `SidebarClass::StripClass::Draw_It(bool complete)` | Renders one column/strip; reads `Buildables[]`, redraw flags. | Per-frame, gated by `IsToRedraw` |
| `SidebarClass::StripClass::SelectClass::Action(unsigned flags, KeyNumType &key)` | **The actual cameo click handler.** Reads which buildable was clicked, its factory state (`Is_Building`, `Has_Completed`); writes: queues `PRODUCE`/`ABANDON`/`SUSPEND`/`PLACE` events; speaks voice feedback (`VOX_BUILDING`, `VOX_TRAINING`, `VOX_CANCELED`, `VOX_SUSPENDED`, `VOX_NO_FACTORY`). | Event-driven (mouse click on a cameo) — richest event hook for "player interacted with build queue" |
| `SidebarClass::SBGadgetClass::Action` | Resets mouse cursor/help text when hovering sidebar. | Event-driven (mouse-over) |
| `SidebarClass::Abandon_Production` / `StripClass::Abandon_Production` | Writes: clears factory link from a buildable slot; calls `FactoryClass::Abandon()`. | Event-driven |
| `SidebarClass::Zoom_Mode_Control` | Writes: toggles radar zoom/player-status/spy-view mode. Sidebar's map button handler. | Event-driven (button press) |

### GlyphX DLL layer — `SIDEBARGlyphx.CPP`
Same shape as above but stripped of rendering (mirrors sidebar production data out to the external GlyphX client, one instance per multiplayer player):
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `SidebarGlyphxClass::Add` | Writes: appends to a strip's `Buildables[]`. | Event-driven |
| `SidebarGlyphxClass::Factory_Link` | Writes: links factory index to a buildable entry. | Event-driven |
| `SidebarGlyphxClass::AI` | Delegates to both columns' `StripClass::AI`. | Per-frame (via `Sidebar_Glyphx_AI` wrapper) |
| `SidebarGlyphxClass::StripClass::AI` | Reads factory completion per buildable slot; queues `PLACE` events; speaks unit-ready/construction voice lines. | Per-frame poll, same throttling caveat as legacy version |
| `SidebarGlyphxClass::Recalc` / `StripClass::Recalc` | Reads/writes: prunes stale buildable entries. | Event-driven (destroyed factory) by design — **not verified** how often the GlyphX side actually calls this |
| `SidebarGlyphxClass::Abandon_Production` / `StripClass::Abandon_Production` | Writes: clears factory link, calls `Abandon()`. | Event-driven |
| `SidebarGlyphxClass::Code_Pointers` / `Decode_Pointers` / `Load` / `Save` | Save-game (de)serialization of sidebar state. | Event-driven (save/load only) |
| Free functions `Sidebar_Glyphx_Init_Clear/Init_IO/Abandon_Production/Add/Recalc/AI/Factory_Link/Save/Load/Code_Pointers/Decode_Pointers` | Thin C-style wrappers around the above, looked up via `Get_Current_Context_Sidebar(player_ptr)` — **the actual DLL-facing entry points** for sidebar state. | Mixed — mirrors whatever's wrapped |

### GlyphX DLL layer — `DLLInterface.cpp`
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `DLLExportClass::Get_Sidebar_State(uint64 player_id, unsigned char* buffer_in, unsigned int buffer_size)` | Reads everything at once: `PlayerPtr->Credits`, `VisibleCredits.Current`, `Tiberium`/`Capacity`, `Power`/`Drain`, repair/sell button enabled state, radar-active flag, kill/loss stats, and the full sidebar column contents (`Map.Column[c].Buildables[]` or, in multiplayer, `context_sidebar->Column[c].Buildables[]`), each entry's cost, build time, busy/constructing/completed/on-hold flags, and production `Progress` fraction from `FactoryClass::Completion()`. Writes it all into a `CNCSidebarStruct` output buffer for the external client. | **Per-frame poll** — the richest single function for sidebar+queue+power+funds data, but designed for continuous polling, not discrete events. Diff against the previous frame before speaking anything. |
| `DLLExportClass::Fill_Sidebar_Entry_From_Special_Weapon` | Reads a super-weapon's recharge/ready state into a sidebar entry struct. | Called from within `Get_Sidebar_State` — same caveat |
| `DLLExportClass::Reset_Sidebars(void)` | Writes: re-initializes all per-player `MultiplayerSidebars[]` instances. | Event-driven (match start / scenario reset) |

---

## 2. Build Queue Contents (production progress/completion)

### `FACTORY.CPP` (per-building production/queue engine — one `FactoryClass` per active production slot)
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `FactoryClass::Set(TechnoTypeClass const&, HouseClass&)` | Writes: creates the object-in-limbo, sets `Balance`/`OriginalBalance` (cost), resets stage/rate to suspended. | Event-driven (production start request) |
| `FactoryClass::Start(void)` | Writes: un-suspends, computes and sets per-tick production rate from `Time_To_Build()`. | Event-driven |
| `FactoryClass::Suspend(void)` | Writes: pauses production (`IsSuspended=true`, rate 0). | Event-driven |
| `FactoryClass::Abandon(void)` | Writes: refunds money via `House->Refund_Money`, deletes the limbo object, resets factory to idle. | Event-driven |
| `FactoryClass::AI(void)` | Reads/writes every tick: checks `Graphic_Logic()` (a `StageClass` timer) for elapsed production step; computes `Cost_Per_Tick()`, deducts from `House` money (or rolls back a step if insufficient funds), marks `IsSuspended=true` + refunds leftover balance at `STEP_COUNT` (54 steps). | Per-frame poll, once per tick per active `FactoryClass`. Source-of-truth "progress advanced" event, fires unconditionally each tick — use `Has_Changed()` for the edge-triggered version. |
| `FactoryClass::Has_Changed(void)` | Reads+clears `IsDifferent` flag — the built-in edge-detector the game itself uses to avoid redrawing/announcing every tick. **Screen-reader logic should key off this same flag** (or the DLL equivalent) rather than re-polling `Completion()` unconditionally. | Event-driven wrapper around per-frame state |
| `FactoryClass::Has_Completed(void)` | Reads: `Object && Fetch_Stage()==STEP_COUNT`. Pure query. | Queried both per-frame (`StripClass::AI`) and on-demand (click handlers) |
| `FactoryClass::Completion(void)` | Reads: current stage (0..54) — build queue progress percentage. | Queried per-frame by `Get_Sidebar_State` and `StripClass::AI`/`Draw_It` |
| `FactoryClass::Completed(void)` | Writes: clears `Object`/`SpecialItem`, resets stage/rate — called once the finished unit/building has been handed off/placed. | Event-driven (after successful placement/exit) |
| `FactoryClass::Force_Complete(void)` | Writes: debug hook that jumps a factory straight to complete. | Event-driven (debug command only) |
| `FactoryClass::Get_Object` / `Get_Special_Item` | Pure reads of what's currently in the queue slot. | On-demand |
| `FactoryClass::Cost_Per_Tick` | Reads `Balance`/stage to compute per-tick cost. Internal helper for `AI()`. | Per-frame (from `AI()`) |

### Event dispatch that drives the queue — `EVENT.CPP`
| Function/case | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `EventClass::Execute` — `case PRODUCE` | Calls `HouseClass::Begin_Production(type, id)` | Event-driven (once per queued `PRODUCE` event) |
| `EventClass::Execute` — `case SUSPEND` | Calls `HouseClass::Suspend_Production(type)` | Event-driven |
| `EventClass::Execute` — `case ABANDON` | Calls `HouseClass::Abandon_Production(type)` | Event-driven |
| `EventClass::Execute` — `case PLACE` | Calls `HouseClass::Place_Object(type, cell)` — removes a completed unit/building from the queue and drops it in the world. | Event-driven |

Note: `Execute_DoList`/`Queue_AI` (`QUEUE.CPP`) and `DLLExportClass::Glyphx_Queue_AI` (below) *pump* these events out of the queue every frame — but each individual event fires only once.

### `HOUSE.CPP` — production request handlers (called by the dispatcher above)
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `HouseClass::Begin_Production(RTTIType type, int id)` | Writes: allocates/reuses a `FactoryClass`, calls `Set()`+`Start()`, links it to the sidebar (`Sidebar_Glyphx_Factory_Link` in multiplayer, or `Map.Factory_Link` in legacy/skirmish). | Event-driven |
| `HouseClass::Suspend_Production(RTTIType type)` | Writes: suspends the matching factory; flags `Map.SidebarClass::IsToRedraw`. | Event-driven |
| `HouseClass::Abandon_Production(RTTIType type)` | Writes: abandons the matching factory; multiplayer calls `Sidebar_Glyphx_Abandon_Production`, else `Map.Abandon_Production`; clears pending building-placement state. | Event-driven |
| `HouseClass::Place_Object(RTTIType type, CELL cell)` | Writes: removes the completed object from its factory and places it in the world (or into placement mode for buildings). | Event-driven |

### GlyphX DLL layer — `DLLInterface.cpp`
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `DLLExportClass::Start_Construction` / `Hold_Construction` / `Cancel_Construction` | Thin wrappers calling `Construction_Action`/`MP_Construction_Action` with the right `SidebarRequestEnum`. External API's equivalent of clicking a sidebar cameo. | Event-driven (once per player command from the external client) |
| `DLLExportClass::Construction_Action(SidebarRequestEnum, uint64 player_id, int buildable_type, int buildable_id)` | Reads factory/build state for the requested slot; writes: queues `PRODUCE`/`SUSPEND`/`ABANDON` events, speaks voice feedback via `On_Speech`. Ported from `SidebarClass::StripClass::SelectClass::Action`. Single-player/skirmish path. | Event-driven |
| `DLLExportClass::MP_Construction_Action(...)` | Same as above for `GAME_GLYPHX_MULTIPLAYER`; operates on per-player `SidebarGlyphxClass` context instead of `Map`. | Event-driven |
| `DLLExportClass::Start_Placement` / `Cancel_Placement` / `Place` | Writes: moves a completed building from "in factory" into "placement mode," places it at a cell, or cancels placement. Reads `Get_Pending_Placement_Object`. | Event-driven |
| `DLLExportClass::Get_Placement_State` | Reads current pending-placement object/cursor state for client rendering (placement ghosting). | Likely per-frame poll (parallel to `Get_Sidebar_State`) — **call frequency not fully verified** |
| `DLLExportClass::Calculate_Placement_Distances` / `Recalculate_Placement_Distances` | Computes proximity-to-existing-building distances used to validate placement legality. | Called from placement-related event handlers, not obviously per-frame |
| `DLLExportClass::Glyphx_Queue_AI(void)` | Moves events from `OutList` to `DoList` and executes any due events (`DoList[j].Execute()`), then prunes the list — the pump that turns queued `PRODUCE`/`SUSPEND`/`ABANDON`/`PLACE` requests into real state changes. | Per-frame (must run every tick to drain the queue), each individual event executes once |

---

## 3. Unit/Object Selection

### `OBJECT.CPP` (base selection mechanism, per-player selection masks)
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `ObjectClass::Select(bool allow_mixed)` | Writes: adds this object to `CurrentObject` list for the owning player, sets `IsSelectedMask`/`IsSelected`; may cascade to `Unselect_All()` if mixing incompatible ownership types. | Event-driven (click/drag-select) |
| `ObjectClass::Unselect(void)` | Writes: removes from `Is_Selected_By_Player()` state, clears `Set_Unselected_By_Player()`. | Event-driven |
| `ObjectClass::Unselect_All_Players(void)` | Writes: removes this object from `CurrentObject` for every house, clears `IsSelectedMask`. Called when an object is destroyed/stunned. | Event-driven (object destruction) |
| `ObjectClass::Unselect_All_Players_Except_Owner(void)` | Writes: same but preserves owner's selection — used when an object cloaks. | Event-driven (cloak transition) |
| `ObjectClass::Set_Selected_By_Player(HouseClass* player)` / `Set_Unselected_By_Player` | Writes: the actual `CurrentObject` list mutation + `IsSelectedMask` bit twiddling, per-player. | Event-driven, called from `Select`/`Unselect` |
| `ObjectClass::Is_Selected_By_Player(HouseClass* player) const` | Pure read of `IsSelectedMask` bit for a house. | On-demand (queried constantly, no side effects) |

### `TECHNO.CPP`
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `TechnoClass::Select(bool allow_mixed)` | Reads discovery/fog state; calls base `Select()`; writes: speaks a unit voice acknowledgment (`Response_Select()`) if the object belongs to the human player. **This voice-on-select is the exact kind of hook an accessibility layer should piggyback on** — fires once per selection change, not per frame. | Event-driven |
| `TechnoClass::Stun(void)` | Writes: calls `Unselect_All_Players()` as part of disabling the object (EMP etc). | Event-driven |

### `CONQUER.CPP` (free functions, global selection helpers)
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `Unselect_All(void)` | Writes: iterates `CurrentObject` and calls `Unselect()` on each until empty. | Event-driven (deselect-all: empty-space click, escape, entering placement mode, etc. — many call sites across `CONQUER.CPP`, `DISPLAY.CPP`, `SIDEBAR.CPP`, `HOUSE.CPP`, `DLLInterface.cpp`) |
| `Unselect_All_Except(ObjectClass* object)` | Writes: same but keeps one object selected. | Event-driven |

### `DISPLAY.CPP`
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `DisplayClass::Select_These(COORDINATE coord1, COORDINATE coord2, bool additive)` | Writes: rubber-band drag-select handler — iterates ground layer + aircraft, calls `Select(true)` on everything inside the box (respecting selectability/ownership/cloak rules); calls `Unselect_All()` first unless `additive`. | Event-driven (mouse-drag release) |

### `RADAR.CPP`
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `RadarClass::RTacticalClass::Action(unsigned flags, KeyNumType &key)` | Reads `CurrentObject[0]->What_Action(...)` to determine cursor/action when hovering the radar minimap; reads `Is_Selected_By_Player()` to special-case cursor over own units. | Event-driven (mouse-over/click on radar), invoked from `RadarClass::AI` which runs per-frame — the read only matters when mouse position/input changes |

### GlyphX DLL layer — `DLLInterface.cpp`
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `DLLExportClass::Get_Player_Info_State(uint64 player_id, ...)` | Reads `CurrentObject` (first selected object → `SelectedID`/`SelectedType`), computes per-cell `ActionWithSelected[]` array (what action would occur clicking each visible cell with current selection), plus ally power/money spy visibility, screen-shake, radar-jam state. Writes into `CNCPlayerInfoStruct`. | Per-frame poll (parallel to `Get_Sidebar_State`) — primary hook for "what does the player currently have selected," but poll-shaped, not event-shaped. |
| `DLLExportClass::Scatter_Selected` | Reads `CurrentObject`; writes: queues a `SCATTER` event for each selected mobile object. | Event-driven (hotkey/command) |
| `DLLExportClass::Select_Next_Unit` / `Select_Previous_Unit` | Writes: calls `Unselect_All()` then selects next/previous object via `Map.Next_Object`/`Prev_Object`; recenters camera. | Event-driven (hotkey) |
| `DLLExportClass::Selected_Guard_Mode` | Reads `CurrentObject`; writes: queues `MISSION_GUARD`/`MISSION_GUARD_AREA` events. | Event-driven |
| `DLLExportClass::Selected_Stop` | Reads `CurrentObject`; writes: queues `IDLE` events. | Event-driven |
| `DLLExportClass::Units_Queued_Movement_Toggle` | Writes: `PlayerPtr->IsQueuedMovementToggle`. Not selection itself, but a per-selection-group behavior toggle. | Event-driven |
| `DLLExportClass::Team_Units_Formation_Toggle_On` | Reads/writes selected-units formation flag (`FormationEvent`). | Event-driven |
| `DLLExportClass::Create_Control_Group` / `Add_To_Control_Group` / `Toggle_Control_Group_Selection` | All delegate to `Handle_Team(control_group_index, mode)` (not traced — see Follow-ups). Writes: control-group membership/selection state. | Event-driven (hotkey, e.g. Ctrl+1..9 / 1..9) |

---

## 4. Low-Power / Low-Funds Warnings

### `HOUSE.CPP` — the actual warning logic, inside `HouseClass::AI(void)` (~line 1034-1119, within the function starting at line 912)
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `HouseClass::AI(void)` | This single per-tick function contains essentially all low-power/low-funds warning logic: reads `Power_Fraction() < 1` → damages above-half-health power-drawing buildings, gated by a `DamageTime` countdown (once per `Rule.DamageDelay` minutes); reads `Available_Money() < 100` and factory count `> 0` → speaks `VOX_NEED_MO_MONEY`, calls `Map.Flash_Money()`, posts EVA text `TXT_INSUFFICIENT_FUNDS`, gated by `SpeakMaxedDelay` (re-fires only after `Rule.SpeakDelay` minutes); reads `IsMaxedOut` + tiberium capacity → speaks `VOX_NEED_MO_CAPACITY`; reads `Power_Fraction() < 1` + `ActiveBScan & STRUCTF_CONST` → speaks `VOX_LOW_POWER`, calls `Map.Flash_Power()`, posts EVA text (`TXT_LOW_POWER`/`TXT_POWER_AAGUN`/`TXT_POWER_TESLA`), gated by `SpeakPowerDelay`. | Per-frame poll, but the warnings are **already edge/rate-limited by the original game** via `SpeakPowerDelay`/`SpeakMaxedDelay`/`DamageTime` — solid model to hook into directly (trigger the screen-reader announcement at the same point the game calls `Speak(VOX_LOW_POWER)`/`Speak(VOX_NEED_MO_MONEY)`, rather than re-deriving edge detection from `Power_Fraction()`). |
| `HouseClass::Power_Fraction(void) const` | Pure read: `Power/Drain` as fixed-point fraction (1.0 = fully powered). No side effects. | On-demand, called from many places every tick |
| `HouseClass::Available_Money(void) const` | Pure read: `Tiberium + Credits`. | On-demand |
| `HouseClass::Spend_Money(unsigned money)` | Writes: deducts from `Tiberium` then `Credits`; calls `Silo_Redraw_Check`. | Event-driven (from `FactoryClass::AI` per production tick when money is spent, plus other spend sites) |
| `HouseClass::Refund_Money(unsigned money)` | Writes: adds to `Credits`. | Event-driven (production abandon/refund) |
| `HouseClass::Adjust_Power(int adjust)` | Writes: `Power += adjust`; calls `Update_Spied_Power_Plants()`. | Event-driven (building built/destroyed/sold/powered-down) |
| `HouseClass::Adjust_Drain(int adjust)` | Writes: `Drain += adjust`. | Event-driven (same triggers) |
| `HouseClass::Silo_Redraw_Check(long oldtib, long oldcap)` | Reads old vs. new tiberium/capacity to decide if silo graphics need a redraw. | Called from `Spend_Money`/other mutators — event-driven, not a per-tick poll |

### `POWER.CPP` (legacy sidebar power-bar widget)
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `PowerClass::AI(KeyNumType&, int, int)` | Reads `PlayerPtr->Power`/`Drain` every tick, compares to cached `RecordedPower`/`RecordedDrain`, animates the power-bar height toward the new value if changed (with easing); sets `IsToRedraw`. | Per-frame poll — pure UI animation; the actual "power changed" edge is `PlayerPtr->Power != RecordedPower`, fires once per real change. About display height, not the low-power *warning* itself (that's in `HouseClass::AI`). |
| `PowerClass::Flash_Power(void)` | Writes: sets `FlashTimer = TICKS_PER_SECOND` for a visual flash. Called from `HouseClass::AI` when power is low. | Event-driven (once when the low-power condition is newly re-announced) |
| `PowerClass::PowerButtonClass::Action(unsigned flags, KeyNumType &key)` | Reads `PlayerPtr->Power_Fraction()` to choose help text (`TXT_POWER_OUTPUT_LOW` vs `TXT_POWER_OUTPUT`) on mouse hover. | Event-driven (mouse hover) |

### `TAB.CPP` (legacy top-bar credits/timer widget)
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `TabClass::Flash_Money(void)` | Writes: sets `MoneyFlashTimer = 7` to flash the credits display. Called from `HouseClass::AI` when funds are low. | Event-driven |
| `TabClass::AI(KeyNumType&, int, int)` | Reads `MoneyFlashTimer`; calls `Credits.AI()` and `SidebarClass::AI()`. | Per-frame |
| `TabClass::Draw_Credits_Tab(void)` | Renders credits/timer display based on `Map.MoneyFlashTimer`, `Scen.MissionTimer`. | Per-frame, visually gated |

### `CREDITS.CPP`
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `CreditClass::AI(bool forced, HouseClass* player_ptr, bool logic_only)` | Reads `player_ptr->Available_Money()`; writes: animates the displayed `Current` counter toward the true `Credits` value over several ticks (with an audible "money up/down" tick flagged via `IsAudible`). Called from `HouseClass::AI` every tick for the local player. | Per-frame poll — the true value change happens instantly, but the display counter (and `IsAudible`) animates gradually across many frames. **Do not hook `IsAudible` directly** — it fires repeatedly as the counter ticks toward target; hook the underlying `Available_Money()` change instead (already used by `HouseClass::AI`'s low-funds logic, gated by `SpeakMaxedDelay`). |
| `CreditClass::Graphic_Logic(bool forced)` | Renders the animated counter; plays `VOC_MONEY_UP`/`VOC_MONEY_DOWN` sound effects when `IsAudible`. | Per-frame, gated on `IsToRedraw` |

### GlyphX DLL layer — `DLLInterface.cpp`
| Function | What it reads/writes | Event-driven or per-frame |
|---|---|---|
| `DLLExportClass::Get_Sidebar_State` (see section 1) | Also carries `Credits`, `CreditsCounter` (animated display value), `PowerProduced`, `PowerDrained` per call. | Per-frame poll |
| `DLLExportClass::Get_Player_Info_State` (see section 3) | Also carries `SpiedInfo[house].Power/Drain/Money` for allied/spied houses — low-power/low-funds visibility into *other* players' economies, not just your own. | Per-frame poll |
| `DLLExportClass::On_Speech(const HouseClass* player_ptr, int speech_index)` | The DLL-side wrapper the game calls in place of the legacy `Speak()` function (used by `HouseClass::AI`'s low-power/low-funds branches, and `Construction_Action`'s voice feedback). **Very likely the single best hook point** — every `VOX_LOW_POWER`, `VOX_NEED_MO_MONEY`, `VOX_BUILDING`, `VOX_CANCELED`, etc. call in the DLL-multiplayer path already funnels through here, already rate-limited by the game's own per-player delay timers, already scoped to a specific player/house. | Event-driven — fires once per voice-line trigger, not per tick |

---

## Summary: Recommended integration points

1. **`DLLExportClass::On_Speech`** (`DLLInterface.cpp`, ~line 2456) — intercept this and get low-power, low-funds, low-capacity, and most build-queue voice events (unit ready, construction complete, suspended, canceled, no-factory) for free, already rate-limited by the game's own per-player delay timers. Event-driven, not per-frame.
2. **`DLLExportClass::Get_Sidebar_State`** and **`Get_Player_Info_State`** (`DLLInterface.cpp`) — per-frame poll functions exposing the full sidebar/queue/power/funds/selection snapshot each tick. Hooking these requires building diff-against-previous-frame edge detection before feeding anything to Tolk.
3. Player-action entry points (`Start_Construction`, `Cancel_Construction`, `Select_Next_Unit`, etc., section 2/3) are already event-driven one-shot calls — safe to hook directly without additional throttling.

## Follow-ups not fully traced this pass

- `Handle_Team` (control groups) — likely in `CONQUER.CPP` or `TEAM.CPP`, not traced.
- `Get_Placement_State`'s actual call frequency from the external client — not verified.
- Whether `SidebarGlyphxClass::Recalc` is invoked every frame or only on factory-loss events — not verified.
