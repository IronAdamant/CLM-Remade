Scriptname A1ALMMGEF_ShrinkEffect extends ActiveMagicEffect
{CLM 2.1 Shrinkin': the target shrinks to Scale of its size for the effect's duration, then grows back. The
enchantment only applies it to targets not already shrunk, so sizes never compound.}

float Property Scale = 0.5 const auto
float Original = 1.0

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Original = akTarget.GetScale()
	akTarget.SetScale(Original * Scale)
	Log("shrunk from " + Original)
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	akTarget.SetScale(Original)
	Log("grown back to " + Original)
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
