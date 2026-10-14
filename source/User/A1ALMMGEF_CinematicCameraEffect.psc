Scriptname A1ALMMGEF_CinematicCameraEffect extends ActiveMagicEffect
{CLM 2.1 Cinematic Excellence (Tjonbrown24): switches to the third-person camera for the effect's duration, then back
to first person. The spell only applies it when the player is in first person (IsPC1stPerson), so third-person
players are left alone. Fallout 4 has no way to start a kill camera outside V.A.T.S.; this and a slow-time effect
in the same spell stand in for it.}

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Log("third person")
	Game.ForceThirdPerson()
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	Log("back to first person")
	Game.ForceFirstPerson()
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
