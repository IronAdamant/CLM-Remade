Scriptname A1ALMMGEF_OnKillArmourEffect extends ActiveMagicEffect
{CLM 2.1 (Bloodthirsty, Momentum, Cinematic Excellence): every time the wearer kills someone (with a ChanceToCast
roll), heals them RestoreHealthPercent of their health and casts SelfSpell on them (each optional). Runs from a perk's ability, so wearing several pieces with
it still gives one effect.
SelfAbility (optional) is added to the wearer for AbilitySeconds instead: a timed spell cast on oneself did not
change jump height or speed in game (2.1 testing), an ability does.}

ActorValue Property Health                         const auto mandatory
Spell      Property SelfSpell                      const auto
float      Property RestoreHealthPercent = 0.0     const auto
float      Property ChanceToCast         = 1.0     const auto
Spell      Property SelfAbility                    const auto
float      Property AbilitySeconds       = 10.0    const auto
int                 AbilityTimerID       = 2       const
Actor               Wearer

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Wearer = akTarget
	RegisterForRemoteEvent(akTarget, "OnKill")
	Log("started")
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	UnregisterForRemoteEvent(akTarget, "OnKill")
	if (SelfAbility)
		CancelTimer(AbilityTimerID)
		akTarget.RemoveSpell(SelfAbility)
	endif
	Log("finished")
EndEvent

Event Actor.OnKill(Actor akSender, Actor akVictim)
	if (ChanceToCast < Utility.RandomFloat(0.0, 1.0))
		Log("killed " + akVictim + ": " + ChanceToCast * 100.0 + "% roll failed")
		return
	endif
	Log("killed " + akVictim + ": heals " + RestoreHealthPercent * 100.0 + "%, casts " + SelfSpell)
	if (RestoreHealthPercent > 0.0)
		akSender.RestoreValue(Health, akSender.GetBaseValue(Health) * RestoreHealthPercent)
	endif
	if (SelfSpell)
		SelfSpell.Cast(akSender, akSender)
	endif
	if (SelfAbility)
		akSender.AddSpell(SelfAbility, false)
		StartTimer(AbilitySeconds, AbilityTimerID)   ; each kill restarts it
	endif
EndEvent

Event OnTimer(int aiTimerID)
	if (aiTimerID == AbilityTimerID && SelfAbility)
		Actor who = GetTargetActor()     ; not a variable: an effect already running in an older save never set it
		if (!who)
			who = Wearer
		endif
		if (who)
			who.RemoveSpell(SelfAbility)
		endif
	endif
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
