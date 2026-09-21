# RA1 AccessMod (Red Alert 1996, C++ engine-level mod)

Screen-reader accessibility layer for the C&C Remastered Collection's Red Alert (1996), built
against the official GPLv3 source EA released
(https://github.com/electronicarts/CnC_Remastered_Collection).

This folder contains only the new files this project adds — not the base game source, which
you get from Steam (`<Steam library>\steamapps\common\CnCRemastered\SOURCECODE\`) or EA's
GitHub repo.

## How it's wired in

Everything here bolts onto `DLLExportClass::On_Speech` in the base source's
`SOURCECODE\RedAlert\DLLInterface.cpp`, since every relevant voice line already funnels
through that one function, event-driven and already rate-limited per-player. The only edit to
base-game source is:

```cpp
// near the top of DLLInterface.cpp
#include "AccessMod/AccessMod.h"

// inside DLLExportClass::On_Speech(...)
void DLLExportClass::On_Speech(const HouseClass* player_ptr, int speech_index)
{
    AccessMod_Speak_Vox(speech_index);   // <-- the only line added

    if (EventCallback == NULL) {
        return;
    }
    // ...
}
```

## Prerequisites

- Command & Conquer Remastered Collection, owned and installed via Steam
- Visual Studio 2022 Build Tools, Desktop development with C++ workload (the project
  originally assumed VS2017/2019/v141/SDK 8.1 — if you're on an older toolset and hit
  packing/header errors instead of the ones below, try the community VS2019 fork
  [alexlk42/CnC_Remastered_Collection](https://github.com/alexlk42/CnC_Remastered_Collection),
  which has already patched those header mismatches)
- Git

## To build

1. Confirm your Steam install path for `CnCRemastered` — the GPLv3 source ships bundled with
   the install itself, under `CnCRemastered\SOURCECODE\`. No separate `git clone` needed for
   the base game.
2. Drop this folder's contents into `SOURCECODE\RedAlert\AccessMod\`, next to `DLLInterface.cpp`.
3. Add the include + call shown above to `DLLInterface.cpp`.
4. Build **only** `RedAlert\RedAlert.vcxproj` directly, not the full `.sln` (which also tries
   to build the separately-broken, out-of-scope TiberianDawn project). On VS2022 Build Tools
   (v143 toolset, Windows 10 SDK 10.0.22621.0), three things are needed beyond a plain build:
   ```
   cd SOURCECODE
   CL=/DWINDOWS_IGNORE_PACKING_MISMATCH msbuild RedAlert/RedAlert.vcxproj -p:Configuration=Release -p:PlatformToolset=v143 -p:WindowsTargetPlatformVersion=10.0.22621.0
   ```
   - `WINDOWS_IGNORE_PACKING_MISMATCH` works around the codebase's global 1-byte struct
     packing conflicting with a `static_assert` in modern Windows SDK headers.
   - `RedAlert.rc` includes the MFC header `afxres.h` purely for resource-script boilerplate.
     Rather than installing the full MFC/ATL component, drop a two-line shim
     (`#pragma once` + `#include <winres.h>`) at `SOURCECODE\RedAlert\Resource\afxres.h`
     (same folder as `RedAlert.rc`, since `rc.exe` resolves quoted includes relative to the
     including file first).
   - Confirm `RedAlert.dll` appears in `SOURCECODE\bin\Win32\` before making any code changes,
     so you know a clean build works before layering the mod on top.
5. **Find your real Documents folder before deploying anything.** Don't assume
   `C:\Users\<user>\Documents` — check with PowerShell:
   `[Environment]::GetFolderPath("MyDocuments")`. Documents is commonly OneDrive-redirected
   (e.g. `C:\Users\<user>\OneDrive\Documentos`, note it may even use a non-English folder
   name) — the plain path can exist but silently not be the one the game reads.
6. Mods are namespaced per game type: the game auto-creates `Mods\Red_Alert\` and
   `Mods\Tiberian_Dawn\` subfolders inside `CnCRemastered\`. A mod must live inside the
   matching one, not flat under `Mods\`. Create:
   `<resolved Documents path>\CnCRemastered\Mods\Red_Alert\AccessMod\`, with a `ccmod.json`
   inside it:
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
7. Deploy the built `RedAlert.dll` plus everything in `ThirdParty/Tolk/` to
   `<resolved Documents path>\CnCRemastered\Mods\Red_Alert\AccessMod\Data\` — `Tolk.dll` and
   its driver DLLs must sit next to `RedAlert.dll` for Windows' DLL search order to find them
   at runtime. Redeploy this `Data` folder after every rebuild.
8. **Activate the mod in-game (easy to miss)** — dropping files into the Mods folder is not
   enough by itself. Launch the game, go to **Options → Mods**, and activate AccessMod from
   the list (press **Refresh** first if it doesn't appear). Only then does the game load the
   modded `RedAlert.dll` instead of the base install's. To confirm which one actually loaded,
   check `CnCRemastered\log\LogFile_0.txt` for its `ModuleList:` dump near startup, which
   lists every loaded DLL with its path.

## Status (as of 2026-08-10)

**Not yet confirmed working end-to-end.** Deployed and rebuilt four times; no in-game speech
confirmed. `AccessMod.cpp` only calls `Tolk_Load()` lazily, the first time a mapped VOX event
fires — so a silent test run doesn't distinguish "DLL never loaded," "loaded but no VOX event
happened to fire," and "Tolk failed to initialize."

**Open questions for whoever picks this up next:**
1. Does AccessMod actually show up in Options → Mods (Red Alert list) after being placed in
   the correct, resolved Documents path? Check this first.
2. If it shows up and gets activated but the instance server log's `LAUNCH_FROM_CLIENT=` field
   stays empty, that field may not be the right signal for mod activation at all — try
   comparing `LogFile_0.txt`'s `ModuleList:` dump instead, or add distinctive startup behavior
   to the mod itself (see next point).
3. Make verification independent of any specific in-game VOX trigger: add a startup-only
   `Tolk_Output` call very early (e.g. in a DLL init path) so *any* successful load of the
   modded `RedAlert.dll` speaks something immediately, rather than depending on correctly
   triggering a sidebar/build-queue event in a live match. This is the recommended next step
   and hasn't been done yet.

See also `../docs/red-alert-voice-blueprint.md`'s "Read This First" section.

## `ThirdParty/Tolk/`

Vendored, not built from source — copied from the Civ-V-Access project's own Tolk build.
32-bit only (matches this game's architecture). LGPLv3. Includes driver DLLs for NVDA, System
Access, ZoomText, and Dolphin screen readers, plus Windows SAPI fallback.
