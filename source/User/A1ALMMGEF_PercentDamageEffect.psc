Scriptname A1ALMMGEF_PercentDamageEffect extends ActiveMagicEffect
{CLM 2.1 Decimatin' (ViscousVitriol): each hit takes Percent of the target's base health on top of the weapon's
damage. Essential actors go down to bleedout as usual instead of dying.}

ActorValue Property Health          const auto mandatory
float      Property Percent = 0.1   const auto

Event OnEffectStart(Actor akTarget, Actor akCaster)
	if (akTarget && !akTarget.IsDead())
		akTarget.DamageValue(Health, akTarget.GetBaseValue(Health) * Percent)
	endif
EndEvent
