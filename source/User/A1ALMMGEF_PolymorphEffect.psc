Scriptname A1ALMMGEF_PolymorphEffect extends ActiveMagicEffect
{CLM 2.1 Radroachin': turns the target into a Critter (a radroach). Everything it carried goes to the critter, so
killing the critter gets the loot back. Unique and essential characters and companions are left alone, so quests are
not affected.}

ActorBase Property Critter const auto mandatory

Event OnEffectStart(Actor akTarget, Actor akCaster)
	if (!akTarget || akTarget.IsDead() || akTarget.IsEssential() || akTarget.IsPlayerTeammate() || akTarget == Game.GetPlayer())
		return
	endif
	ActorBase base = akTarget.GetLeveledActorBase()
	if (base && base.IsUnique())
		Log("unique, left alone")
		return
	endif
	Actor beast = akTarget.PlaceActorAtMe(Critter)
	akTarget.RemoveAllItems(beast)
	akTarget.KillSilent(akCaster)
	akTarget.Disable()
	Log("became " + beast)
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
