Scriptname A1ALMMGEF_OnMeleeCLMEffect extends ActiveMagicEffect
{CLM (2017, recovered 2026, compiles identical to 1.09): casts SpellToCast on whoever hits the wearer with any weapon type below (or on the wearer if IsSelfCast), with a ChanceToCast roll and a Cooldown in seconds. Far Harbor's dlc03_Legendary_OnMeleeEffect logic with a wider weapon check.}
Keyword Property WeaponTypeHandtoHand const auto mandatory
Keyword Property WeaponTypeUnarmed const auto mandatory
Keyword Property WeaponTypeMelee1H const auto mandatory
Keyword Property WeaponTypeMelee2H const auto mandatory
Keyword Property WeaponTypePossiblyVerySmallClipSize const auto mandatory
Keyword Property WeaponTypePistol const auto mandatory
Keyword Property WeaponTypeRifle const auto mandatory
Keyword Property WeaponTypeAutomatic const auto mandatory
Keyword Property WeaponTypeHeavyGun const auto mandatory
Keyword Property WeaponTypeThrown const auto mandatory
Keyword Property WeaponTypeExplosive const auto mandatory
Keyword Property WeaponTypeLaser const auto mandatory
Keyword Property WeaponTypePlasma const auto mandatory
Keyword Property WeaponTypeBallistic const auto mandatory
Keyword Property WeaponTypeMine const auto mandatory
Keyword Property WeaponTypeGrenade const auto mandatory
Keyword Property WeaponTypeAlienBlaster const auto mandatory
Keyword Property WeaponTypeSniper const auto mandatory
Keyword Property WeaponTypeCryoMine const auto mandatory
Keyword Property WeaponTypePulseMine const auto mandatory
Keyword Property WeaponTypeNukaMine const auto mandatory
Keyword Property WeaponTypePlasmaMine const auto mandatory
Keyword Property WeaponTypeBottlecapMine const auto mandatory
Keyword Property WeaponTypeCryoGrenade const auto mandatory
Keyword Property WeaponTypeNukaGrenade const auto mandatory
Keyword Property WeaponTypePlasmaGrenade const auto mandatory
Keyword Property WeaponTypePulseGrenade const auto mandatory
Keyword Property WeaponTypeMolotov const auto mandatory
Keyword Property WeaponTypeMissileLauncher const auto mandatory
Keyword Property WeaponTypeFatman const auto mandatory
Keyword Property WeaponTypeMinigun const auto mandatory
Keyword Property WeaponTypeGatlingLaser const auto mandatory
Keyword Property WeaponTypeCryolater const auto mandatory
Keyword Property WeaponTypeFlamer const auto mandatory
Keyword Property WeaponTypeFlareGun const auto mandatory
Keyword Property WeaponTypeGammaGun const auto mandatory
Keyword Property WeaponTypeJunkJet const auto mandatory
Keyword Property WeaponTypeRailwayRifle const auto mandatory
Keyword Property WeaponTypeSyringer const auto mandatory
Keyword Property WeaponTypeBroadsider const auto mandatory
Keyword Property WeaponTypeRipper const auto mandatory
Keyword Property WeaponTypeShishkebab const auto mandatory
Keyword Property WeaponTypeLaserMusket const auto mandatory
Keyword Property WeaponTypeShotgun const auto mandatory
Keyword Property WeaponTypeAssaultRifle const auto mandatory
Keyword Property WeaponTypeGaussRifle const auto mandatory
Spell Property SpellToCast const auto mandatory
float Property ChanceToCast = 1.0 const auto
bool Property IsSelfCast = false const auto
float Property Cooldown = 60.00 const auto
int TimerID = 1 const
bool OnCooldown = false

Event OnEffectStart(Actor akTarget, Actor akCaster)
	; Register for a hit event on successful melee.
	RegisterForHitEvent(akTarget)
EndEvent

Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string apMaterial)
	; If we are not on cooldown and this is a matching weapon,
	; we are GO!
	if (!OnCooldown && (akSource.haskeyword(WeaponTypeHandtoHand) || akSource.haskeyword(WeaponTypeUnarmed) || akSource.haskeyword(WeaponTypeMelee1H) || akSource.haskeyword(WeaponTypeMelee2H) || akSource.haskeyword(WeaponTypePossiblyVerySmallClipSize) || akSource.haskeyword(WeaponTypePistol) || akSource.haskeyword(WeaponTypeRifle) || akSource.haskeyword(WeaponTypeAutomatic) || akSource.haskeyword(WeaponTypeHeavyGun) || akSource.haskeyword(WeaponTypeThrown) || akSource.haskeyword(WeaponTypeExplosive) || akSource.haskeyword(WeaponTypeLaser) || akSource.haskeyword(WeaponTypePlasma) || akSource.haskeyword(WeaponTypeBallistic) || akSource.haskeyword(WeaponTypeGrenade) || akSource.haskeyword(WeaponTypeMine) || akSource.haskeyword(WeaponTypeAlienBlaster) || akSource.haskeyword(WeaponTypeSniper) || akSource.haskeyword(WeaponTypeCryoMine) || akSource.haskeyword(WeaponTypePulseMine) || akSource.haskeyword(WeaponTypeNukaMine) || akSource.haskeyword(WeaponTypePlasmaMine) || akSource.haskeyword(WeaponTypeBottlecapMine) || akSource.haskeyword(WeaponTypeCryoGrenade) || akSource.haskeyword(WeaponTypeNukaGrenade) || akSource.haskeyword(WeaponTypePlasmaGrenade) || akSource.haskeyword(WeaponTypePulseGrenade) || akSource.haskeyword(WeaponTypeMolotov) || akSource.haskeyword(WeaponTypeMissileLauncher) || akSource.haskeyword(WeaponTypeFatman) || akSource.haskeyword(WeaponTypeMinigun) || akSource.haskeyword(WeaponTypeGatlingLaser) || akSource.haskeyword(WeaponTypeCryolater) || akSource.haskeyword(WeaponTypeFlamer) || akSource.haskeyword(WeaponTypeFlareGun) || akSource.haskeyword(WeaponTypeGammaGun) || akSource.haskeyword(WeaponTypeJunkJet) || akSource.haskeyword(WeaponTypeRailwayRifle) || akSource.haskeyword(WeaponTypeSyringer) || akSource.haskeyword(WeaponTypeBroadsider) || akSource.haskeyword(WeaponTypeRipper) || akSource.haskeyword(WeaponTypeShishkebab) || akSource.haskeyword(WeaponTypeLaserMusket) || akSource.haskeyword(WeaponTypeShotgun) || akSource.haskeyword(WeaponTypeAssaultRifle) || akSource.haskeyword(WeaponTypeGaussRifle)))

		if (ChanceToCast >= Utility.randomfloat(0.0, 1.0))

			if !IsSelfCast
				; Onto my attacker...
				SpellToCast.cast(akTarget, akAggressor)
			else
				; Onto myself...
				SpellToCast.cast(akTarget, akTarget)
			endif

			OnCooldown = true
			StartTimer(Cooldown, TimerID)
		endif
	endif

	; Re-register for a hit event on melee.
	RegisterForHitEvent(akTarget)
EndEvent

Event OnTimer(int aiTimerID)
	If aiTimerID == TimerID
		OnCooldown = false
	EndIf
EndEvent
