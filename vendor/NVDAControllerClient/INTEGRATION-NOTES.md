# NVDA Controller Client — vendored for the C&C accessibility project

Sourced 2026-08-10 from the official NV Access distribution: `nvda_2026.1.1_controllerClient.zip`
(https://download.nvaccess.org/releases/stable/). LGPL-2.1, see `license.txt`.

## Why this instead of Tolk?

The implementation plan (`implementation_plan.md`, produced by Antigravity) proposes Tolk as a
multi-screen-reader abstraction layer. Two things changed that:

1. **Tolk publishes no pre-built binaries.** The upstream repo (github.com/dkager/tolk) ships
   source only and states "this project is not currently being developed" — getting a working
   64-bit `Tolk.dll` means compiling it yourself (needs Visual C++, Windows SDK, JDK, Python,
   Pandoc — VS2022 is installed on this machine so it's *possible*, just heavier than
   necessary for a first working version).
2. **The plan's own stated goal is NVDA support specifically** (see `implementation_plan.md`'s
   title: "...accessible to blind and visually impaired players using the NVDA screen reader").
   Tolk's JAWS/Narrator/SAPI fallback support is a nice-to-have the plan doesn't actually
   require. Going straight to NVDA's own Controller Client is a smaller, official, directly
   supported dependency that unblocks real work today.

**This is a scope decision worth confirming, not a unilateral change** — if JAWS/Narrator
support turns out to matter, building Tolk from source (or reconsidering CrossSpeak, a NuGet
wrapper that layers on Tolk — see below) is still on the table.

## What's here

- `x64/`, `x86/` — `nvdaControllerClient.dll` + `.lib` + `nvdaController.h` for both
  architectures. **OpenRA-RA2 targets `net6.0`/`AnyCPU`, which runs 64-bit on this machine —
  use `x64/nvdaControllerClient.dll`.** The `x86/` copy is for the CnCRemastered C++ side if
  useful (that project already has a 32-bit `Tolk.dll` + `nvdaControllerClient32.dll` in
  `Documents\CnCRemastered\Mods\AccessMod\Data\`, so it may not need this at all).
- `csharp/NVDA.cs`, `SpeechPriority.cs`, `SymbolLevel.cs` — the **official** C# wrapper from
  NV Access's own example project, unmodified. Static class `NVAccess.NVDA.NVDA` with
  `Speak(text, interrupt)`, `CancelSpeech()`, `IsRunning`, `Braille(message)`,
  `SpeakSsml(...)`, `GetProcessId()`.

## Why it's staged here and not dropped into OpenRA-RA2 directly

Antigravity is actively building/committing in that repo right now. Adding files mid-task
risked confusing its view of the working tree. Once it's between steps, drop-in is:

1. Copy `x64/nvdaControllerClient.dll` to `OpenRA.Mods.RA2/`'s output directory (or add an
   MSBuild `<Content Include="..." CopyToOutputDirectory="PreserveNewest" />` item so it
   ships with builds).
2. Copy the three `csharp/*.cs` files into `OpenRA.Mods.RA2/Accessibility/` (or wherever the
   plan's proposed `AccessibilityManager.cs` is going to live) and adjust the namespace if
   OpenRA's conventions expect `OpenRA.Mods.RA2.*` rather than `NVAccess.NVDA`.
3. Call `NVDA.Speak(text)` from the tactical-cursor/sidebar hooks described in the plan.

## Security note from NV Access's own docs

> NVDA runs on the lock screen and secure screens. Before speaking anything, check whether
> Windows is locked or on a secure screen to avoid leaking information there.

Not directly relevant to a single-player RTS, but worth keeping in mind if any narration ever
touches sensitive text.

## If broader screen-reader support (JAWS, Narrator, SAPI) turns out to matter

Two options, neither pursued here:
- Build Tolk from source (toolchain is present: VS2022 found under
  `C:\Program Files (x86)\Microsoft Visual Studio\2022`).
- `TOWK.Utility.CrossSpeak` NuGet package — cross-platform wrapper that uses Tolk internally
  on Windows, but still requires manually supplying the native DLLs (same sourcing problem,
  just via a different C# API surface).
