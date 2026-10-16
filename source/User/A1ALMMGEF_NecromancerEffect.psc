Scriptname A1ALMMGEF_NecromancerEffect extends ActiveMagicEffect
{CLM 2.1 Necromancer's: Delay seconds after the wielder kills someone, the body turns to ash (its loot stays in the
ash pile, as with a laser kill) and a fresh copy of it rises in its place: RisenSpell (A1ALMMGEF_RisenEffect) makes
the copy fight for the player for a while, then it crumbles to an empty ash pile. A copy, not the body itself:
resurrected actors came back with their combat AI not working and stood still (2.1 testing).
Unique and essential characters and the wielder's companions are left alone, so quests are not affected. Each body
or copy rises once. No limit on how many stand at once (author's decision: it is an OP legendary); the game counts
teammates' kills as the player's, so the risen raise their own victims too.}

Spell        Property RisenSpell         const auto mandatory
Faction      Property AllyFaction        const auto mandatory
{The player's faction: the copy joins it before it appears, so it is never hostile, not even for a moment.}
Activator    Property AshPile            const auto mandatory
EffectShader Property AshShader          const auto
float        Property Delay      = 1.0   const auto
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
	Utility.Wait(Delay)
	if (!akVictim.IsDead() || !akVictim.Is3DLoaded() || akVictim.IsDisabled())
		Log("killed " + akVictim + ": body gone, not raised")
		return
	endif
	; spawned disabled and switched to the player's side while invisible, then faded in (2.1 testing: an enabled
	; copy was hostile for the moment until RisenSpell took hold)
	Actor copy = akVictim.PlaceAtMe(base, 1, false, true) as Actor
	Remember(akVictim)
	Remember(copy)
	if (copy)
		copy.RemoveFromAllFactions()
		copy.AddToFaction(AllyFaction)
		copy.SetPlayerTeammate(true, false)
	endif
	Ash(akVictim)
	if (copy)
		copy.Enable(true)
		RisenSpell.Cast(akSender, copy)
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

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
