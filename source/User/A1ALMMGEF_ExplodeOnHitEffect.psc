Scriptname A1ALMMGEF_ExplodeOnHitEffect extends ActiveMagicEffect
{CLM 2.1 (BioReactive rounds, Singularity): sets off Blast at the target on every hit, alive or dead. They used
vanilla's FortuneFinderCapsScript, which only explodes targets already dead when the effect ends, so BioReactive
exploded on killing hits only (since 1.09; reported on Nexus). The PlayStation build puts that vanilla script back.}

Explosion Property Blast const auto mandatory

Event OnEffectStart(Actor akTarget, Actor akCaster)
	if (akTarget)
		akTarget.PlaceAtMe(Blast)
		Log("exploded")
	endif
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
