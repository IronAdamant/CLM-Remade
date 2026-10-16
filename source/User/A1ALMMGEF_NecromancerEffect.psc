Scriptname A1ALMMGEF_NecromancerEffect extends ActiveMagicEffect
{CLM 2.1 Necromancer's: Delay seconds after the wielder kills someone, the body rises and RisenSpell (which makes it
an ally for a while, A1ALMMGEF_RisenEffect) is cast on it. Unique and essential characters and the wielder's
companions are left alone, so quests are not affected. At most MaxRisen at once: the game counts teammates' kills as
the player's, so the risen raising their own victims would otherwise snowball.}

Spell Property RisenSpell         const auto mandatory
float Property Delay      = 1.5   const auto
int   Property MaxRisen   = 3     const auto
Actor[] risen
Actor[] used          ; every body raised so far: each rises once

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
	if (used && used.Find(akVictim) >= 0)
		Log("killed " + akVictim + ": already raised once, stays dead")
		return
	endif
	if (Standing() >= MaxRisen)
		Log("killed " + akVictim + ": " + MaxRisen + " already risen, left alone")
		return
	endif
	Utility.Wait(Delay)
	if (akVictim.IsDead() && akVictim.Is3DLoaded() && !akVictim.IsDisabled())
		akVictim.Resurrect()
		RisenSpell.Cast(akSender, akVictim)
		risen.Add(akVictim)
		if (!used)
			used = new Actor[0]
		endif
		if (used.Length >= 120)
			used.Remove(0)
		endif
		used.Add(akVictim)
		Log("raised " + akVictim)
	else
		Log("killed " + akVictim + ": body gone, not raised")
	endif
EndEvent

; how many of the raised are still up (alive and on the player's side); forgets the rest
int Function Standing()
	if (!risen)
		risen = new Actor[0]
	endif
	int i = risen.Length - 1
	while (i >= 0)
		if (!risen[i] || risen[i].IsDead() || !risen[i].IsPlayerTeammate())
			risen.Remove(i)
		endif
		i -= 1
	endwhile
	return risen.Length
EndFunction

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
