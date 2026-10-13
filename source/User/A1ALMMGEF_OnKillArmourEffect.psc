Scriptname A1ALMMGEF_OnKillArmourEffect extends ActiveMagicEffect
{CLM 2.1 (Bloodthirsty, Momentum, Cinematic Excellence): every time the wearer kills someone (with a ChanceToCast
roll), heals them RestoreHealthPercent of their health and casts SelfSpell on them (each optional). Runs from a perk's ability, so wearing several pieces with
it still gives one effect.}

ActorValue Property Health                         const auto mandatory
Spell      Property SelfSpell                      const auto
float      Property RestoreHealthPercent = 0.0     const auto
float      Property ChanceToCast         = 1.0     const auto

Event OnEffectStart(Actor akTarget, Actor akCaster)
	RegisterForRemoteEvent(akTarget, "OnKill")
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	UnregisterForRemoteEvent(akTarget, "OnKill")
EndEvent

Event Actor.OnKill(Actor akSender, Actor akVictim)
	if (ChanceToCast < Utility.RandomFloat(0.0, 1.0))
		return
	endif
	if (RestoreHealthPercent > 0.0)
		akSender.RestoreValue(Health, akSender.GetBaseValue(Health) * RestoreHealthPercent)
	endif
	if (SelfSpell)
		SelfSpell.Cast(akSender, akSender)
	endif
EndEvent
