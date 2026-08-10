# C&C Screen Reader Accessibility Analysis Walkthrough

This walkthrough summarizes the analysis and actionable plan for adding NVDA screen reader accessibility to the Command & Conquer games found on your system.

---

## 1. Game Installations & Tech Stacks

We located your game files and determined their engine architectures:

| Game | Path | Tech Stack | Modding Pathway |
| :--- | :--- | :--- | :--- |
| **C&C: Tiberian Dawn** | [CnCRemastered](file:///F:/SteamLibrary/steamapps/common/CnCRemastered) | C++ (GPL Source Available) | Modify `TiberianDawn.dll` in source files. |
| **C&C: Red Alert 1** | [CnCRemastered](file:///F:/SteamLibrary/steamapps/common/CnCRemastered) | C++ (GPL Source Available) | Modify `RedAlert.dll` in source files. |
| **C&C: Red Alert 2** | [OpenRA-RA2](file:///C:/Users/vegas/OneDrive/Desktop/Games/OpenRA-RA2) | C# (Mono/.NET, Open Source) | Edit `OpenRA.Mods.RA2` classes and UI system. |
| **C&C: Red Alert 3** | [Red Alert 3](file:///F:/SteamLibrary/steamapps/common/Command%20and%20Conquer%20Red%20Alert%203) | C++ (Closed Source Sage Engine) | Process memory reading or DLL hooking via SageMetaTool. |

---

## 2. Key Screen Reader Design Proposals

Since RTS games rely on spatial mouse navigation and complex visual UIs, we recommend implementing the following mechanics:

### The Tolk Interface (`tolk.dll`)
We will use the **Tolk** library to route spoken narration directly to the user's active screen reader (NVDA, JAWS, or Windows Narrator). Tolk serves as a unified abstraction layer, making it easy to call `Tolk_Speak("Text")` in both C++ and C# without worrying about low-level COM interfaces or screen reader specific APIs.

### The "Tactical Cursor" Grid
To replace mouse interactions, we propose a keyboard-based navigation system:
1. **Grid Navigation:** Arrow keys or Numpad keys move a virtual selection cursor from tile to tile on the map.
2. **Audio Feedback:** Upon moving to a tile, the screen reader announces:
   * Terrain type (e.g., "Ore", "Water", "Bridge").
   * Object presence (e.g., "Enemy Power Plant", "Allied Harvester").
   * Object health (e.g., "Red Alert, 25% health").
3. **Sound Beacons:** Pressing a hotkey plays a directional sound at the cursor's map position, allowing players to hear where the action is relative to their viewport.

### Hotkey Queries
Quick keystroke combinations to fetch essential game statistics instantly:
* `Ctrl + Shift + R`: Speaks credits/ore amount and power status (e.g., "Credits: 1500, Power: Surplus").
* `Ctrl + Shift + Q`: Speaks sidebar queue status (e.g., "Structures: Barracks 60%, Vehicles: None").
* `Ctrl + Shift + S`: Speaks selected unit summary (e.g., "3 Grenadiers, 1 Medic").

---

## 3. Recommended Next Steps

Here is the roadmap for initiating development of these accessibility features:

### Step 1: Set up the Tolk Libraries
1. Download the latest version of `Tolk` from GitHub.
2. Copy `tolk.dll` and `tolk.lib` to your project directories.

### Step 2: C&C Remastered C++ Modification
1. Open the solution in `CnCRemastered\SOURCECODE\CnCRemastered.sln` using Visual Studio.
2. Modify the keyboard handler in `TIBERIANDAWN\INPUT.CPP` to intercept arrow keys.
3. Call `Tolk_Speak` within `SidebarClass` updates.
4. Compile the custom DLLs and replace them in the Steam game directory.

### Step 3: OpenRA-RA2 C# Mod Modification
1. Load `OpenRA.Mods.RA2.sln` in Visual Studio or VS Code.
2. Write a custom P/Invoke wrapper for `tolk.dll` or use the C# `cytolk` bindings.
3. Hook the engine viewport controls to introduce the keyboard Tactical Cursor.
