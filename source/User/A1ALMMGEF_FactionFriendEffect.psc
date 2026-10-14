Scriptname A1ALMMGEF_FactionFriendEffect extends ActiveMagicEffect
{CLM 2.1 Hello Neighbour! (stephen4000): while it is worn, FriendlyFaction is no longer the player's enemy; taking it
off makes them enemies again. Runs from a perk's ability, so wearing several pieces with it still gives one effect.}

Faction Property FriendlyFaction const auto mandatory

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Log("friends with " + FriendlyFaction)
	FriendlyFaction.SetPlayerEnemy(false)
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	Log("enemies again with " + FriendlyFaction)
	FriendlyFaction.SetPlayerEnemy(true)
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
