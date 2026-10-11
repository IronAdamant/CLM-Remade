Scriptname A1ALMMGEF_OnMeleeHitCLMEffect extends ActiveMagicEffect
{CLM (2017, recovered 2026): places the Fortune Finder caps explosion at the target. The hit registration below uses an unset variable and the script has no OnHit, so it does nothing; kept exactly as shipped.}

Keyword Property WeaponTypeHandtoHand const auto mandatory
Keyword Property WeaponTypeUnarmed const auto mandatory
Keyword Property WeaponTypeMelee1H const auto mandatory
Keyword Property WeaponTypeMelee2H const auto mandatory
Explosion Property PerkExplosionMoneyShotFortuneFinder const auto
Actor victim

Event OnEffectStart(Actor akTarget, Actor akCaster)
	akTarget.PlaceAtMe(PerkExplosionMoneyShotFortuneFinder)
	RegisterForHitEvent(victim)
EndEvent
