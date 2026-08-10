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

## To build

1. Drop this folder's contents into `SOURCECODE\RedAlert\AccessMod\` next to `DLLInterface.cpp`.
2. Add the include + call above to `DLLInterface.cpp`.
3. Build `RedAlert\RedAlert.vcxproj` (not the full `.sln`). See `../docs/red-alert-accessibility-project.md`
   for the exact toolset flags this machine needed (VS2022/v143/SDK 10.0.22621.0).
4. Deploy the built `RedAlert.dll` plus everything in `ThirdParty/Tolk/` to
   `<Documents>\CnCRemastered\Mods\Red_Alert\AccessMod\Data\` (resolve the real Documents path
   first — it may be OneDrive-redirected).
5. Activate the mod in-game: Options → Mods → AccessMod → Refresh if needed.

## Status (as of 2026-08-10)

**Not yet confirmed working end-to-end.** Deployed and rebuilt four times; no in-game speech
confirmed. `AccessMod.cpp` only calls `Tolk_Load()` lazily, the first time a mapped VOX event
fires — so a silent test run doesn't distinguish "DLL never loaded," "loaded but no VOX event
happened to fire," and "Tolk failed to initialize." The recommended next debugging step (not
yet done) is an early, load-confirming speak call — see `../docs/red-alert-accessibility-project.md`'s
"Open questions" and `../docs/red-alert-voice-blueprint.md`'s "Read This First."

## `ThirdParty/Tolk/`

Vendored, not built from source — copied from the Civ-V-Access project's own Tolk build.
32-bit only (matches this game's architecture). LGPLv3. Includes driver DLLs for NVDA, System
Access, ZoomText, and Dolphin screen readers, plus Windows SAPI fallback.
