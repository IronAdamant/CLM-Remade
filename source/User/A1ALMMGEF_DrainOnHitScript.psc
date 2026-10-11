Scriptname A1ALMMGEF_DrainOnHitScript extends ActiveMagicEffect
{CLM vampiric hit (2.0): takes the effect's magnitude in health from the target and gives it to the attacker.
Replaces the "Absorb Health" effect type, which only healed on targets that survived the hit - kills (molerats,
radroaches...) gave nothing, as players reported. This heals on every hit, kills included.}

ActorValue Property Health Auto Const Mandatory
float Property Amount = 25.0 Auto Const
{Health taken and given per hit. (Vanilla Papyrus cannot read the effect's magnitude, so each amount has its own
magic effect with this set.)}

Event OnEffectStart(Actor akTarget, Actor akCaster)
	float heal = Amount
	If akCaster
		akCaster.RestoreValue(Health, heal)
	EndIf
	If akTarget && !akTarget.IsDead()
		akTarget.DamageValue(Health, heal)
	EndIf
EndEvent
