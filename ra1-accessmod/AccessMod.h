//
// AccessMod - screen reader accessibility layer for Red Alert (1996).
//
// Bolts a Tolk-based speech hook onto the existing EVA voice-line pipeline
// (DLLExportClass::On_Speech) so sidebar, build-queue, and power/funds
// warnings reach a screen reader without requiring visual confirmation.
//
#pragma once

// Speaks the screen-reader phrase for a VoxType speech index, if one is
// mapped. No-ops (does not touch Tolk at all) for indices we haven't mapped
// yet, and safely no-ops if no screen reader is running.
void AccessMod_Speak_Vox(int speech_index);
void AccessMod_Init();
