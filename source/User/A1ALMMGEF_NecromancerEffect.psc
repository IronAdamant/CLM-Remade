Scriptname A1ALMMGEF_NecromancerEffect extends ActiveMagicEffect
{CLM 2.1 Necromancer's: Delay seconds after the wielder kills someone, the body rises and RisenSpell (which makes it
an ally for a while, A1ALMMGEF_RisenEffect) is cast on it. Unique and essential characters and the wielder's
companions are left alone, so quests are not affected.}

Spell Property RisenSpell         const auto mandatory
float Property Delay      = 1.5   const auto

Event OnEffectStart(Actor akTarget, Actor akCaster)
	RegisterForRemoteEvent(akTarget, "OnKill")
	Log("started")
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	UnregisterForRemoteEvent(akTarget, "OnKill")
	Log("finished")
EndEvent

Event Actor.OnKill(Actor akSender, Actor akVictim)
	ActorBase base = akVictim.GetLeveledActorBase()
	if (akVictim.IsEssential() || akVictim.IsPlayerTeammate() || (base && base.IsUnique()))
		Log("killed " + akVictim + ": unique, essential or a companion, left alone")
		return
	endif
	Utility.Wait(Delay)
	if (akVictim.IsDead() && akVictim.Is3DLoaded() && !akVictim.IsDisabled())
		akVictim.Resurrect()
		RisenSpell.Cast(akSender, akVictim)
		Log("raised " + akVictim)
	else
		Log("killed " + akVictim + ": body gone, not raised")
	endif
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
