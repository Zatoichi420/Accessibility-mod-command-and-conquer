//
// AccessMod - screen reader accessibility layer for Red Alert (1996).
//
// Exception handling isn't enabled
#pragma warning (disable : 4530)

#include <cstdio>
#include <cstdlib>
#include <windows.h>

#include "../function.h"
#include "../defines.h"
#include "AccessMod.h"
#include "ThirdParty/Tolk/Tolk.h"

namespace {

bool TolkReady = false;

// Appends a line to %TEMP%\AccessMod_RedAlert.log so a "loaded but silent"
// report can be diagnosed without attaching a debugger. Best-effort: a
// logging failure here is never allowed to affect speech output.
void AccessMod_Log(const char* message)
{
	char path[MAX_PATH];
	DWORD len = GetTempPathA(MAX_PATH, path);
	if (len == 0 || len >= MAX_PATH) {
		return;
	}
	strncat(path, "AccessMod_RedAlert.log", MAX_PATH - strlen(path) - 1);

	FILE* file = fopen(path, "a");
	if (file == NULL) {
		return;
	}
	fprintf(file, "%s\n", message);
	fclose(file);
}

// Loads Tolk on first use (idempotent) and logs what it actually found, so a
// silent-speech report can distinguish "no screen reader/SAPI detected" from
// "detected but Tolk_Output itself failed" from "this code never ran at all".
void Ensure_Tolk_Loaded()
{
	if (TolkReady) {
		return;
	}

	// Fall back to SAPI (system default synthesizer) when no dedicated
	// screen reader is detected, so speech works during testing without
	// NVDA/JAWS/etc. running. Kept last in the detection order so a real
	// screen reader always wins when one is active.
	Tolk_TrySAPI(true);
	Tolk_PreferSAPI(false);
	Tolk_Load();
	TolkReady = true;

	if (!Tolk_IsLoaded()) {
		AccessMod_Log("Tolk_Load failed: Tolk did not initialize.");
		return;
	}

	const wchar_t* driver = Tolk_DetectScreenReader();
	if (driver != NULL) {
		char narrow[128];
		wcstombs(narrow, driver, sizeof(narrow) - 1);
		narrow[sizeof(narrow) - 1] = '\0';
		char line[192];
		sprintf(line, "Tolk loaded. Driver: %s. Has speech: %s.", narrow, Tolk_HasSpeech() ? "yes" : "no");
		AccessMod_Log(line);
	} else {
		AccessMod_Log("Tolk loaded but detected no active screen reader or SAPI voice.");
	}
}

// Human-readable phrases for the VOX_ events that matter to the sidebar,
// build queue, and power/funds warnings (the project's first hook target).
// Anything not listed here is left to a later pass rather than guessed at.
const wchar_t* Vox_Text(int speech_index)
{
	switch (speech_index)
	{
	case VOX_NEW_CONSTRUCT:      return L"New construction options";
	case VOX_BUILDING:           return L"Building";
	case VOX_TRAINING:           return L"Training";
	case VOX_CONSTRUCTION:       return L"Construction complete";
	case VOX_UNIT_READY:         return L"Unit ready";
	case VOX_CANCELED:           return L"Canceled";
	case VOX_SUSPENDED:          return L"On hold";
	case VOX_NO_FACTORY:         return L"Cannot comply, still building";
	case VOX_REPAIRING:          return L"Repairing";
	case VOX_UNABLE_TO_BUILD:    return L"Unable to build more";
	case VOX_PRIMARY_SELECTED:   return L"Primary building selected";
	case VOX_LOW_POWER:          return L"Low power";
	case VOX_INSUFFICIENT_POWER: return L"Insufficient power";
	case VOX_NEED_MO_MONEY:      return L"Insufficient funds";
	case VOX_NO_CASH:            return L"Insufficient funds";
	case VOX_NEED_MO_CAPACITY:   return L"Silos needed";
	default:                     return NULL;
	}
}

} // namespace

void AccessMod_Speak_Vox(int speech_index)
{
	const wchar_t* text = Vox_Text(speech_index);
	if (text == NULL) {
		return;
	}

	Ensure_Tolk_Loaded();
	if (!Tolk_Output(text, false)) {
		AccessMod_Log("Tolk_Output failed for a VOX event.");
	}
}

void AccessMod_Init()
{
	Ensure_Tolk_Loaded();
	AccessMod_Log("AccessMod_Init reached: RedAlert.dll loaded and ran this code.");
	if (!Tolk_Output(L"Red Alert Accessibility Mod Loaded Successfully", false)) {
		AccessMod_Log("Tolk_Output failed for the startup announcement.");
	}
}
