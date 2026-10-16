Scriptname A1ALMMGEF_RisenEffect extends ActiveMagicEffect
{CLM 2.1 Necromancer's: on the risen copy of a killed body (A1ALMMGEF_NecromancerEffect). For the effect's duration it
fights for the player: it leaves its factions, joins AllyFaction (the player's faction, so its old allies turn on it),
turns aggressive and foolhardy, becomes a teammate and goes for the nearest enemy every few seconds. When the effect
ends, or it dies first, its inventory is emptied (the original body's ash pile holds the real loot) and it crumbles to
an empty ash pile.}

Faction    Property AllyFaction            const auto mandatory
ActorValue Property Aggression             const auto mandatory
ActorValue Property Confidence             const auto mandatory
Activator  Property AshPile                const auto mandatory
EffectShader Property AshShader            const auto
Keyword[]  Property ActorTypes             const auto mandatory
{Actor type keywords searched for enemies to attack.}
float      Property HuntRadius    = 4000.0 const auto
float      Property HuntInterval  = 3.0    const auto
int                 TimerID       = 1      const
Actor Body

Event OnEffectStart(Actor akTarget, Actor akCaster)
	akTarget.RemoveFromAllFactions()
	akTarget.AddToFaction(AllyFaction)
	akTarget.SetValue(Aggression, 1)          ; aggressive: attacks the player's enemies on sight
	akTarget.SetValue(Confidence, 4)          ; foolhardy: charges in instead of holding its spot
	akTarget.StopCombat()
	akTarget.SetPlayerTeammate(true, false)
	akTarget.EvaluatePackage()
	Body = akTarget
	Log("risen")
	StartTimer(1.0, TimerID)
EndEvent

; risen bodies have no package that moves them: every few seconds each one goes for the nearest enemy of the player
Event OnTimer(int aiTimerID)
	if (aiTimerID != TimerID || !Body || Body.IsDead())
		return
	endif
	Actor player = Game.GetPlayer()
	Actor best = None
	float bestDistance = HuntRadius
	int k = 0
	while (k < ActorTypes.Length)
		ObjectReference[] near = Body.FindAllReferencesWithKeyword(ActorTypes[k], HuntRadius)
		int i = 0
		while (i < near.Length)
			Actor a = near[i] as Actor
			if (a && a != Body && !a.IsDead() && a.IsHostileToActor(player))
				float d = Body.GetDistance(a)
				if (d < bestDistance)
					best = a
					bestDistance = d
				endif
			endif
			i += 1
		endwhile
		k += 1
	endwhile
	if (best)
		if (bestDistance > 800.0)
			Body.PathToReference(best, 1.0)    ; walk there first: combat alone left them standing
		endif
		if (Body && !Body.IsDead() && !best.IsDead())
			Body.StartCombat(best)
			Log("hunting " + best)
		endif
	endif
	StartTimer(HuntInterval, TimerID)
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	CancelTimer(TimerID)
	akTarget.SetPlayerTeammate(false)
	akTarget.RemoveAllItems()                 ; no second set of loot: the copy's gear goes with it
	if (!akTarget.IsDead())
		akTarget.KillSilent()
	endif
	akTarget.SetCriticalStage(akTarget.CritStage_DisintegrateStart)
	if (AshShader)
		AshShader.Play(akTarget, 1.0)
	endif
	Utility.Wait(0.6)
	akTarget.AttachAshPile(AshPile)
	Utility.Wait(1.0)
	akTarget.SetAlpha(0.0, true)
	akTarget.SetCriticalStage(akTarget.CritStage_DisintegrateEnd)
	Log("crumbled to ash")
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
