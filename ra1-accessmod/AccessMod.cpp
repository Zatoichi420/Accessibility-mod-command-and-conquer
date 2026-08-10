//
// AccessMod - screen reader accessibility layer for Red Alert (1996).
//
// Exception handling isn't enabled
#pragma warning (disable : 4530)

#include "../function.h"
#include "../defines.h"
#include "AccessMod.h"
#include "ThirdParty/Tolk/Tolk.h"

namespace {

bool TolkReady = false;

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

	if (!TolkReady) {
		// Fall back to SAPI (system default synthesizer) when no dedicated
		// screen reader is detected, so speech works during testing without
		// NVDA/JAWS/etc. running. Kept last in the detection order so a real
		// screen reader always wins when one is active.
		Tolk_TrySAPI(true);
		Tolk_PreferSAPI(false);
		Tolk_Load();
		TolkReady = true;
	}

	Tolk_Output(text, false);
}
