Scriptname A1ALMMGEF_ExplodeAfterDeathScript extends ActiveMagicEffect
{CLM (2.0): when the effect ends, blows the target apart if it is dead (Face Bustin': "they'll explode after
death"). Replaces vanilla's ExplodeOnContactScript, which killed the target on every hit.}

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	Log("ended, target dead: " + (akTarget && akTarget.IsDead()))
	If akTarget && akTarget.IsDead()
		akTarget.Dismember("Torso", true, true, true)
	EndIf
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
