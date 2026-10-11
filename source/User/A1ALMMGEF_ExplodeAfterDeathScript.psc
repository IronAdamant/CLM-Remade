Scriptname A1ALMMGEF_ExplodeAfterDeathScript extends ActiveMagicEffect
{CLM (2.0): when the effect ends, blows the target apart if it is dead (Face Bustin': "they'll explode after
death"). Replaces vanilla's ExplodeOnContactScript, which killed the target on every hit.}

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	If akTarget && akTarget.IsDead()
		akTarget.Dismember("Torso", true, true, true)
	EndIf
EndEvent
