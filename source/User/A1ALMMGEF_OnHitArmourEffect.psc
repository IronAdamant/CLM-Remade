Scriptname A1ALMMGEF_OnHitArmourEffect extends ActiveMagicEffect
{CLM 2.1 armour (Phoenix, Static Charged, Jumper's): reacts when the wearer is hit by anything, melee, ranged or
explosion (or, with OnlyOwnAttacks, only by their own attacks, such as their own explosions).
Only at or below LowHealthPercentage health (1.0 = any health), with a ChanceToCast roll, then waits Cooldown seconds:
heals the wearer RestoreHealthPercent of their health and casts SelfSpell on the wearer and AttackerSpell on the
attacker (each optional). Runs from a perk's ability, so wearing several pieces with it still gives one effect.}

ActorValue Property Health                         const auto mandatory
Spell      Property SelfSpell                      const auto
Spell      Property AttackerSpell                  const auto
float      Property ChanceToCast         = 1.0     const auto
float      Property LowHealthPercentage  = 1.0     const auto
float      Property RestoreHealthPercent = 0.0     const auto
float      Property Cooldown             = 5.0     const auto
bool       Property OnlyOwnAttacks       = false   const auto
int                 TimerID              = 1       const
bool                OnCooldown           = false

Event OnEffectStart(Actor akTarget, Actor akCaster)
	RegisterForHitEvent(akTarget)
	Log("started")
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	Log("finished")
EndEvent

Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string apMaterial)
	Actor wearer = akTarget as Actor
	bool ready = !OnCooldown && wearer && (akAggressor == akTarget) == OnlyOwnAttacks && wearer.GetValuePercentage(Health) <= LowHealthPercentage
	bool lucky = ready && ChanceToCast >= Utility.RandomFloat(0.0, 1.0)
	if (ready && !lucky)
		Log("hit by " + akAggressor + " with " + akSource + ": " + ChanceToCast * 100.0 + "% roll failed")
	endif
	if (lucky)
		Log("hit by " + akAggressor + " with " + akSource + " at " + wearer.GetValuePercentage(Health) * 100.0 + "% health: heals " + RestoreHealthPercent * 100.0 + "%, casts " + SelfSpell + " on self, " + AttackerSpell + " on attacker")
		if (RestoreHealthPercent > 0.0)
			wearer.RestoreValue(Health, wearer.GetBaseValue(Health) * RestoreHealthPercent)
		endif
		if (SelfSpell)
			SelfSpell.Cast(wearer, wearer)
		endif
		Actor attacker = akAggressor as Actor
		if (AttackerSpell && attacker && !attacker.IsDead())
			AttackerSpell.Cast(wearer, attacker)
		endif
		OnCooldown = true
		StartTimer(Cooldown, TimerID)
	endif
	RegisterForHitEvent(akTarget)
EndEvent

Event OnTimer(int aiTimerID)
	If aiTimerID == TimerID
		OnCooldown = false
	EndIf
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
