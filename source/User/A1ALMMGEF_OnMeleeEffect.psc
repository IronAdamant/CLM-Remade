Scriptname A1ALMMGEF_OnMeleeEffect extends ActiveMagicEffect
{CLM copy of Far Harbor's DLC03:dlc03_Legendary_OnMeleeEffect (Bethesda, shipped with the Creation Kit sources),
with identical code, so CLM's "Untouchable" style effects no longer require the Far Harbor DLC.
Casts SpellToCast on whoever hits the wearer with a melee or unarmed attack (or on the wearer if IsSelfCast),
with a ChanceToCast roll and a Cooldown in seconds.}

Keyword Property WeaponTypeHandtoHand         const auto mandatory
Keyword Property WeaponTypeUnarmed            const auto mandatory
Keyword Property WeaponTypeMelee1H            const auto mandatory
Keyword Property WeaponTypeMelee2H            const auto mandatory
Spell   Property SpellToCast                  const auto mandatory
float   Property ChanceToCast         = 1.0   const auto
bool    Property IsSelfCast           = false const auto
float   Property Cooldown             = 60.00 const auto
int              TimerID              = 1     const
bool             OnCooldown           = false

Event OnEffectStart(Actor akTarget, Actor akCaster)
	; Register for a hit event on successful melee.
	RegisterForHitEvent(akTarget)
EndEvent

Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string apMaterial)
	; If we are not on cooldown and this is a melee, we are GO!
	if (!OnCooldown && (akSource.haskeyword(WeaponTypeHandtoHand) || akSource.haskeyword(WeaponTypeUnarmed)  || akSource.haskeyword(WeaponTypeMelee1H) || akSource.haskeyword(WeaponTypeMelee2H)))
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
