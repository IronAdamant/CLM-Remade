Scriptname A1ALMMGEF_BurstFireEffect extends ActiveMagicEffect
{CLM 2.1 CQC (DarkArcher045): every shot of the equipped gun is followed by ExtraShots more, Delay seconds apart, a
burst. Each extra shot uses one round from the inventory and fires the gun's base projectile (without its mods).
Fallout 4 has no burst-fire mode, so the extra rounds are fired by this script. (The animation event is
"WeaponFire": names are case-sensitive, and "weaponFire" never arrived.)}

int   Property ExtraShots = 2    const auto
float Property Delay      = 0.07 const auto
Actor Shooter
bool  Busy = false

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Shooter = akTarget
	RegisterForAnimationEvent(akTarget, "WeaponFire")
	Log("started")
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	UnregisterForAnimationEvent(akTarget, "WeaponFire")
	Log("finished")
EndEvent

Event OnAnimationEvent(ObjectReference akSource, string asEventName)
	if (asEventName == "WeaponFire" && !Busy && Shooter)
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
		Log("shot " + gun + ": " + i + " extra rounds of " + rounds + " fired")
		Busy = false
	endif
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
