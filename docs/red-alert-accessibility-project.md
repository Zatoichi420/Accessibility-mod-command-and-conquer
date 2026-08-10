# Red Alert Accessibility Mod Project

## Project Scope

This project focuses exclusively on the Red Alert branch of the Command and Conquer franchise: Red Alert (1996), Red Alert 2 and Yuri's Revenge, and Red Alert 3 and Uprising. Tiberian Dawn, Generals, and other Command and Conquer titles are out of scope for now.

The goal is to add screen reader and spatial audio accessibility to these games, following the same accessibility layer approach already used on the Comanche and Civ-V-Access projects: expose game state as speech and audio cues rather than requiring visual confirmation of sidebar, unit, and combat information.

## Current Status (as of 2026-07-08)

Phase 1 is past the first working build and the first speech hook is implemented, but end-to-end in-game speech is **still not confirmed working** after three test launches and two rounds of fixes (ccmod.json version range, then relocating the mod folder to the correct OneDrive-redirected Documents path under `Mods\Red_Alert\`). Paused here to resume later — see "Open questions" at the bottom of the Blocker notes below.

- Build environment on this machine is VS2022 Build Tools, not VS2017/2019 as originally planned. Three fixes were needed to get `RedAlert.dll` building (see updated Setup Steps below): retarget to toolset v143 / Windows SDK 10.0.22621.0, define `WINDOWS_IGNORE_PACKING_MISMATCH`, and a two-line `afxres.h` shim next to `RedAlert.rc` instead of installing full MFC.
- Reconnaissance pass complete: full function inventory (sidebar/build-queue/selection/power-funds state, event-driven vs. per-frame) saved to `red-alert-accessibility-recon-inventory.md` in this same folder. Key finding: target the GlyphX DLL export layer (`DLLInterface.cpp`), not the legacy renderer — `DLLExportClass::On_Speech` is the best hook since every relevant voice line already funnels through it, already rate-limited per-player.
- First hook implemented: `SOURCECODE\RedAlert\AccessMod\AccessMod.{h,cpp}`, called from `DLLExportClass::On_Speech`, speaks ~16 sidebar/build-queue/power/funds `VOX_*` events via Tolk (vendored from the existing Civ-V-Access project's `third_party/tolk`, not rebuilt from source). SAPI fallback is enabled (`Tolk_TrySAPI(true)`, kept lowest priority) so speech works even without a dedicated screen reader running, though a real screen reader always wins if active.
- `RedAlert.dll` rebuilds clean and is deployed to `Documents\CnCRemastered\Mods\AccessMod\Data\` along with all Tolk runtime DLLs.
- **Blocker found 2026-07-07**: a test launch produced no speech. Diagnosis: dropping the mod into the `Mods` folder is not enough — per EA's modding FAQ, the mod must be activated in-game via **Options → Mods** (press **Refresh** if it doesn't show up) before the game will actually load the modded `RedAlert.dll` instead of the base install's. NVDA was confirmed running at the time, so the screen reader side isn't suspected.
- **Second test launch, same day (2026-07-07)**: still no speech. `InstanceServerLog_Client0.txt`'s `LAUNCH_FROM_CLIENT=` field (which should carry the active mod's path) came back empty on both launches. Suspected: `ccmod.json` had `"version_low": 2, "version_high": 1"` — an inverted, near-zero range against a game build number of `#745903` (confirmed in the instance-server log's startup banner). Fixed to `"version_low": 0, "version_high": 999999999` regardless (correct either way), but this turned out not to be the real blocker — see below.
- **Third test launch, 2026-07-08**: after the version-range fix, user confirmed directly that **AccessMod did not appear at all** in Options → Mods, even after Refresh. This ruled out version_low/high as the cause and prompted checking where the game actually resolves "Documents" to. `[Environment]::GetFolderPath("MyDocuments")` on this machine returns `C:\Users\vegas\OneDrive\Documentos` — Documents is redirected to OneDrive (and uses the Spanish/Portuguese folder name). The mod had been built at the plain `C:\Users\vegas\Documents\...` path, which the game never reads. The real, game-managed folder at `C:\Users\vegas\OneDrive\Documentos\CnCRemastered\` already had `Mods\Red_Alert\` and `Mods\Tiberian_Dawn\` subfolders auto-created by the game — mods are namespaced per game type, not flat under `Mods\`. Copied the whole `AccessMod` folder to `C:\Users\vegas\OneDrive\Documentos\CnCRemastered\Mods\Red_Alert\AccessMod\`.
- **Fourth test launch, same day (2026-07-08)**: relaunched after the path fix — still no speech, and `LAUNCH_FROM_CLIENT=` is still empty in the instance server log. Whether AccessMod now appears in the Options → Mods list was not confirmed before this session paused. **Open questions for next session:**
  1. Does AccessMod now show up in Options → Mods (Red Alert list) after the relocation? This is the first thing to check.
  2. If it shows up and gets activated but `LAUNCH_FROM_CLIENT` still stays empty, that field may not actually be the right signal for mod activation at all — needs re-deriving, possibly by process-of-elimination (e.g. compare `LogFile_0.txt`'s `ModuleList:` dump, or add distinctive startup behavior to the mod itself, see next point).
  3. Consider making verification independent of any specific in-game VOX trigger: add a startup-only `Tolk_Output` call very early (e.g. in a DLL init path) so *any* successful load of the modded `RedAlert.dll` speaks something immediately, rather than depending on triggering a sidebar/build-queue event correctly in a live match.

## Access Level Per Title

| Title | Source Access | Modding Path |
|---|---|---|
| Red Alert (1996) | Full official source code, released by EA as RedAlert.dll under GPLv3, part of the CnC_Remastered_Collection repository | Direct engine-level DLL modification |
| Red Alert 2 and Yuri's Revenge | No official source released | INI-file configuration only, plus a memory-reading overlay for anything INI cannot expose |
| Red Alert 3 and Uprising | No full source, but an official Mod SDK exists (WorldBuilder, XML and W3D data-driven modding, SAGE engine) | Data-driven modding through the Mod SDK, similar in tier to OpenRA's trait and YAML system |

## Phase 1: Red Alert (1996), Engine-Level DLL Mod

This is the current active phase and the deepest, most reliable access point in the entire Red Alert family, since it is real released source code rather than reverse-engineered material.

### Prerequisites

- Command and Conquer Remastered Collection owned and installed via Steam
- Visual Studio Build Tools 2017 or 2019, Desktop development with C++ workload only
- Git

### Setup Steps

1. Confirm the Steam install path — on this machine, `F:\SteamLibrary\steamapps\common\CnCRemastered`
2. The GPLv3 source ships bundled with the Steam install itself, under `CnCRemastered\SOURCECODE\` — no `git clone` needed.
3. Build only `RedAlert\RedAlert.vcxproj` directly (not the full `.sln`, which also tries to build the out-of-scope, separately-broken TiberianDawn project). On a machine with VS2022 Build Tools (v143 toolset, Windows 10 SDK 10.0.22621.0) instead of the VS2017/v141/SDK8.1 the project originally assumed, three flags/fixes are needed:
   ```
   cd SOURCECODE
   CL=/DWINDOWS_IGNORE_PACKING_MISMATCH msbuild RedAlert/RedAlert.vcxproj -p:Configuration=Release -p:PlatformToolset=v143 -p:WindowsTargetPlatformVersion=10.0.22621.0
   ```
   - `WINDOWS_IGNORE_PACKING_MISMATCH` works around the codebase's global 1-byte struct packing conflicting with a `static_assert` in modern Windows SDK headers (this is what the "VS2019 fork has patched header mismatches" note below was getting at).
   - `RedAlert.rc` includes the MFC header `afxres.h` purely for resource-script boilerplate. Rather than installing the full MFC/ATL component, a two-line shim (`#pragma once` + `#include <winres.h>`) placed at `SOURCECODE\RedAlert\Resource\afxres.h` (same folder as `RedAlert.rc`, since `rc.exe` resolves quoted includes relative to the including file first) satisfies it.
4. If VS2017 packing errors appear on a VS2017/2019 machine instead, switch to the community VS2019 fork (alexlk42/CnC_Remastered_Collection), which has already patched the header mismatches
5. Confirm `RedAlert.dll` appears in `SOURCECODE\bin\Win32\` before making any code changes

### Mod Folder Setup

**Important:** the actual path is wherever Windows resolves the "Documents" special folder to for this user — check with PowerShell `[Environment]::GetFolderPath("MyDocuments")` before assuming `C:\Users\<user>\Documents`. On this machine, Documents is redirected to OneDrive: `C:\Users\vegas\OneDrive\Documentos` (note the Spanish/Portuguese folder name). The plain `C:\Users\vegas\Documents\...` path exists but is **not** read by the game.

Mods are also namespaced by game type — the game auto-creates `Mods\Red_Alert\` and `Mods\Tiberian_Dawn\` subfolders inside `CnCRemastered\`, and a mod must live inside the matching one, not flat under `Mods\`.

Create the mod directory:
```
<resolved Documents path>\CnCRemastered\Mods\Red_Alert\AccessMod\
```
e.g. on this machine: `C:\Users\vegas\OneDrive\Documentos\CnCRemastered\Mods\Red_Alert\AccessMod\`

With a `ccmod.json`:
```json
{
  "name": "AccessMod",
  "description": "Screen reader accessibility layer",
  "author": "Orlando Johnson",
  "load_order": 1,
  "version_low": 0,
  "version_high": 999999999,
  "game_type": "RA"
}
```

A `Data` subfolder inside `AccessMod` holds the compiled, modified DLL for testing. Redeploy step after every rebuild: copy `SOURCECODE\bin\Win32\RedAlert.dll` **and** every file from the vendored Tolk folder (see First Hook Target below) into this `Data` folder — `Tolk.dll` and its driver DLLs must sit next to `RedAlert.dll` for Windows' DLL search order to find them at runtime.

**Activating the mod (easy to miss):** dropping files into `Mods\AccessMod\` is not enough by itself. Launch the game, go to **Options → Mods**, and activate AccessMod from the list (press **Refresh** first if it doesn't appear). Only then does the game load the modded `RedAlert.dll` instead of the base install's. A quick way to confirm which one actually loaded: `CnCRemastered\log\LogFile_0.txt` has a `ModuleList:` dump near startup listing every loaded DLL with its path.

### Reconnaissance Session (Before Writing Any Accessibility Code)

Done — full inventory in `red-alert-accessibility-recon-inventory.md` (same folder as this file). Headline finding: the codebase has two parallel UI paths, a legacy renderer and a GlyphX DLL export layer added for the Remastered Collection (`DLLInterface.cpp`, `SIDEBARGlyphx.CPP`). Since the mod bolts onto the DLL, the GlyphX layer is the right integration point — `DLLExportClass::On_Speech` in particular already funnels every relevant voice line through one place, already rate-limited per-player, event-driven rather than per-frame.

### First Hook Target — Implemented

Sidebar and build-queue state, wired to Tolk, matching the speech pipeline already used in the Civ-V-Access project. This keeps the speech layer consistent across projects rather than introducing a second TTS integration to maintain.

Implementation:
- `SOURCECODE\RedAlert\AccessMod\AccessMod.{h,cpp}` — `AccessMod_Speak_Vox(int speech_index)` hand-maps ~16 sidebar/build-queue/power/funds `VOX_*` events (new construction options, building, training, construction complete, unit ready, canceled, on hold, low power, insufficient funds, silos needed, etc.) to English phrases and speaks them via `Tolk_Output`. Everything outside that set is left unmapped (no-op) rather than guessed at — combat/mission-briefing voice lines are out of scope for this pass.
- Hooked into `DLLExportClass::On_Speech` in `DLLInterface.cpp`, called before the `EventCallback == NULL` early-return so it fires in both the legacy/skirmish and GlyphX-multiplayer paths.
- Tolk is vendored, not built from source — copied from the already-built `Civ-V-Access\third_party\tolk\dist\x86\` into `SOURCECODE\RedAlert\AccessMod\ThirdParty\Tolk\` (Tolk.h/.lib/.dll plus its screen-reader driver DLLs for NVDA, System Access, ZoomText, Dolphin). `RedAlert.vcxproj` was hand-edited (both Debug and Release configs) to add the include/lib paths and link `Tolk.lib`.
- SAPI fallback enabled: `Tolk_TrySAPI(true)` + `Tolk_PreferSAPI(false)` before `Tolk_Load()`, so speech works via Windows' default synthesizer even with no dedicated screen reader running, while a real screen reader still takes priority when active.
- **Not yet confirmed working end-to-end in-game** — see Current Status above.

### Distribution Note

EA's community mod policy permits this work provided it stays non-commercial and includes a disclaimer: "EA has not endorsed and does not support this product." Add this to the repository README before any public release.

## Phase 2: Red Alert 2 and Yuri's Revenge, Memory-Overlay Accessibility

No official source exists for RA2 or Yuri's Revenge, so this phase uses a different technique: reading live game state directly from process memory rather than modifying engine code.

### Approach

- Use a RAM-watch style tool (Cheat Engine or similar) to locate memory addresses for unit selection, sidebar contents, resources, and power level
- RA2's INI system (rules.ini, art.ini, ai.ini) can help identify unit and building names and IDs, which makes building the memory map easier, even though the INI files cannot expose real-time UI state on their own
- Feed located memory addresses into a Tolk and spatial audio bridge, consistent with the approach already validated on the Comanche and TIE Fighter accessibility concepts

### Status

Scoping only. Detailed technical work begins after Phase 1 produces a working, validated Tolk pipeline.

## Phase 3: Red Alert 3 and Uprising, Mod SDK Data-Driven Accessibility

RA3 and Uprising run on the SAGE engine and have no full released source, but do have an official Mod SDK (WorldBuilder plus XML and W3D data-driven modding).

### Approach

- Hook into the same scripting and data-definition layer that existing RA3 modders use for units and abilities
- This is a more constrained surface than the Phase 2 memory-reading approach, but it is officially supported tooling rather than reverse engineering

### Status

Scoping only. Detailed technical work begins after Phase 1 and Phase 2 validate the accessibility pipeline on simpler targets.

## Build Order Summary

1. Red Alert (1996) — engine-level DLL mod, in progress
2. Red Alert 2 and Yuri's Revenge — memory-overlay accessibility, scoped
3. Red Alert 3 and Uprising — Mod SDK data-driven accessibility, scoped

## Reference Links

- Official source: https://github.com/electronicarts/CnC_Remastered_Collection
- Community VS2019 build fork: https://github.com/alexlk42/CnC_Remastered_Collection
- EA modding guidelines: https://www.ea.com/games/command-and-conquer/news/modding-faq
- Accessibility modding community and workflow reference: https://github.com/AccessMods
