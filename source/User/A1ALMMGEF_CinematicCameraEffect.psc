Scriptname A1ALMMGEF_CinematicCameraEffect extends ActiveMagicEffect
{CLM 2.1 Cinematic Excellence (Tjonbrown24): switches to the third-person camera for the effect's duration, then back
to first person. The spell only applies it when the player is in first person (IsPC1stPerson), so third-person
players are left alone. Fallout 4 has no way to start a kill camera outside V.A.T.S.; this and a slow-time effect
in the same spell stand in for it.}

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Game.ForceThirdPerson()
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	Game.ForceFirstPerson()
EndEvent
