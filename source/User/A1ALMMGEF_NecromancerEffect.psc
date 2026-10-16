Scriptname A1ALMMGEF_NecromancerEffect extends ActiveMagicEffect
{CLM 2.1 Necromancer's: Delay seconds after the wielder kills someone, the body turns to ash (its loot stays in the
ash pile, as with a laser kill) and a fresh copy of it rises in its place: RisenSpell (A1ALMMGEF_RisenEffect) makes
the copy fight for the player for a while, then it crumbles to an empty ash pile. A copy, not the body itself:
resurrected actors came back with their combat AI not working and stood still (2.1 testing).
Unique and essential characters and the wielder's companions are left alone, so quests are not affected. At most
MaxRisen at once (the game counts teammates' kills as the player's, so the risen raising their own victims would
otherwise snowball), and each body or copy rises once.}

Spell        Property RisenSpell         const auto mandatory
Activator    Property AshPile            const auto mandatory
EffectShader Property AshShader          const auto
float        Property Delay      = 1.0   const auto
int          Property MaxRisen   = 3     const auto
Actor[] risen         ; the copies fighting now
Actor[] used          ; every body raised and every copy: each rises once

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
	if (akVictim.IsEssential() || akVictim.IsPlayerTeammate() || !base || base.IsUnique())
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
	if (!akVictim.IsDead() || !akVictim.Is3DLoaded() || akVictim.IsDisabled())
		Log("killed " + akVictim + ": body gone, not raised")
		return
	endif
	Actor copy = akVictim.PlaceActorAtMe(base)
	Remember(akVictim)
	Remember(copy)
	Ash(akVictim)
	if (copy)
		RisenSpell.Cast(akSender, copy)
		risen.Add(copy)
		Log("raised " + akVictim + " as " + copy)
	endif
EndEvent

; the body crumbles as with a laser kill: its inventory stays lootable in the ash pile
Function Ash(Actor akBody)
	akBody.SetCriticalStage(akBody.CritStage_DisintegrateStart)
	if (AshShader)
		AshShader.Play(akBody, 1.0)
	endif
	Utility.Wait(0.6)
	akBody.AttachAshPile(AshPile)
	Utility.Wait(1.0)
	akBody.SetAlpha(0.0, true)
	akBody.SetCriticalStage(akBody.CritStage_DisintegrateEnd)
EndFunction

Function Remember(Actor akActor)
	if (!akActor)
		return
	endif
	if (!used)
		used = new Actor[0]
	endif
	if (used.Length >= 120)
		used.Remove(0)
	endif
	used.Add(akActor)
EndFunction

; how many copies are still up (alive and on the player's side); forgets the rest
int Function Standing()
	if (!risen)
		risen = new Actor[0]
	endif
	int i = risen.Length - 1
	while (i >= 0)
		if (!risen[i] || risen[i].IsDead() || risen[i].IsDisabled() || !risen[i].IsPlayerTeammate())
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
