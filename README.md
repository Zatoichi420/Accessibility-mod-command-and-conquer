# Command & Conquer Accessibility Mod

Screen reader and voice-control accessibility for classic Command & Conquer games, aimed at
blind and low-vision players. Same accessibility-layer approach used on the Comanche and
Civ-V-Access projects: expose game state as speech and audio cues instead of requiring visual
confirmation of sidebar, unit, and combat information.

## Scope and status

| Title | Access | Approach | Status |
|---|---|---|---|
| Red Alert (1996) | Full GPLv3 source (EA CnC Remastered Collection) | Engine-level DLL mod (`ra1-accessmod/`) | Built and deployed 4x; in-game speech **not yet confirmed** — see `ra1-accessmod/README.md` |
| Red Alert 2 / Yuri's Revenge | No official source | OpenRA-RA2 (separate repo — C# open-source engine fork) | Build system verified working; accessibility integration not yet started |
| Red Alert 3 / Uprising | No full source, official Mod SDK exists | Data-driven modding via Mod SDK (WorldBuilder, XML/W3D) | Scoping only |
| Tiberian Dawn | Full GPLv3 source | — | Under discussion — see scope note below |

**Scope note:** `docs/implementation_plan.md` is the current authoritative plan — it includes
Tiberian Dawn and proposes a DLL-injection approach for RA3 rather than the official Mod SDK.

## Getting started / testing

**Red Alert (1996) is the only title with a build you can currently test.** Full prerequisites,
build steps, and mod-activation instructions (including the two most common gotchas — the
exact Visual Studio toolset flags needed, and Windows' Documents folder frequently being
OneDrive-redirected) are in **[`ra1-accessmod/README.md`](ra1-accessmod/README.md)**. Read its
"Status" section too — in-game speech isn't confirmed working yet, so a tester's first useful
report is simply whether AccessMod shows up and activates under Options → Mods at all.

There's no prebuilt release yet — see "Not included here" below for why, and testers currently
need the prerequisites in that README (Steam copy of the game, VS2022 Build Tools) to build it
themselves.

## Layout

- `docs/` — planning documents: a full reconnaissance of RA1's DLL export layer
  (`red-alert-accessibility-recon-inventory.md`), a voice-control command grammar and
  architecture design (`red-alert-voice-blueprint.md`), and the current plan/task/walkthrough
  set (`implementation_plan.md`, `task.md`, `walkthrough.md`).
- `ra1-accessmod/` — the Red Alert (1996) engine-level mod source: the new files this project
  adds on top of EA's released source, plus the vendored Tolk screen-reader library it depends
  on. See `ra1-accessmod/README.md` for full build/deploy steps and current blocker status.
- `vendor/NVDAControllerClient/` — the official NVDA Controller Client (DLLs, headers, and
  NV Access's own C# wrapper), staged for the OpenRA-RA2 C# accessibility work. See
  `vendor/NVDAControllerClient/INTEGRATION-NOTES.md` for why this was chosen over Tolk for
  that side of the project, and exact drop-in steps.

## Not included here

- **OpenRA-RA2** itself is a separate, already-independent git repository (a fork of the
  OpenRA engine) — too large and already version-controlled on its own to merge in here.
- Build artifacts (compiled `RedAlert.dll`, `.pdb`, `.lib`, `.exp`) — rebuild from
  `ra1-accessmod/` plus the base game source instead of relying on a committed binary.

## Distribution note

EA's community mod policy permits this work provided it stays non-commercial and includes the
disclaimer: "EA has not endorsed and does not support this product."
