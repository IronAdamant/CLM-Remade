Scriptname A1ALMMGEF_RisenEffect extends ActiveMagicEffect
{CLM 2.1 Necromancer's: for the effect's duration the target fights for the player (it leaves its factions, joins
AllyFaction and becomes a teammate); when the effect ends it falls dead again. Killed before then, it stays dead.}

Faction Property AllyFaction const auto mandatory

Event OnEffectStart(Actor akTarget, Actor akCaster)
	akTarget.RemoveFromAllFactions()
	akTarget.AddToFaction(AllyFaction)
	akTarget.StopCombat()
	akTarget.SetPlayerTeammate(true, false)
	akTarget.EvaluatePackage()
	Log("risen")
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	akTarget.SetPlayerTeammate(false)
	if (!akTarget.IsDead())
		akTarget.Kill()
		Log("fell again")
	endif
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
