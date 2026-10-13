Scriptname A1ALMMGEF_BurstFireEffect extends ActiveMagicEffect
{CLM 2.1 CQC (DarkArcher045): every shot of the equipped gun is followed by ExtraShots more, Delay seconds apart, a
burst. Each extra shot uses one round from the inventory and fires the gun's base projectile (without its mods).
Fallout 4 has no burst-fire mode, so the extra rounds are fired by this script.}

int   Property ExtraShots = 2    const auto
float Property Delay      = 0.07 const auto
Actor Shooter
bool  Busy = false

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Shooter = akTarget
	RegisterForAnimationEvent(akTarget, "weaponFire")
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	UnregisterForAnimationEvent(akTarget, "weaponFire")
EndEvent

Event OnAnimationEvent(ObjectReference akSource, string asEventName)
	if (asEventName == "weaponFire" && !Busy && Shooter)
		Busy = true
		Weapon gun = Shooter.GetEquippedWeapon()
		Ammo rounds = None
		if (gun)
			rounds = gun.GetAmmo()
		endif
		int i = 0
		while (rounds && i < ExtraShots && Shooter.GetItemCount(rounds) > 0)
			Utility.Wait(Delay)
			gun.Fire(Shooter, rounds)
			Shooter.RemoveItem(rounds, 1, true)
			i += 1
		endwhile
		Busy = false
	endif
EndEvent
