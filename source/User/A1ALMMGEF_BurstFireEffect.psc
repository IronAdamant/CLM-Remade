Scriptname A1ALMMGEF_BurstFireEffect extends ActiveMagicEffect
{CLM 2.1 CQC (DarkArcher045): every shot of the equipped gun is followed by ExtraShots more, Delay seconds apart, a
burst. Fallout 4 has no burst-fire mode, so the extra rounds are fired by this script: it makes the shooter fire the
gun itself with FireAction (ActionFireSingle, the action the AI fires with), so the extra rounds are the real shot:
the gun's mods, projectile, ammo use and sound. If the game refuses the action, it falls back to Weapon.Fire, which
can only fire the gun's plain projectile and takes the round from the inventory.
The animation event is "WeaponFire" (names are case-sensitive; "weaponFire" never arrived). The forced shots raise it
too, so Pending counts them and they do not start bursts of their own.}

int    Property ExtraShots = 2    const auto
float  Property Delay      = 0.12 const auto
Action Property FireAction        const auto
Actor Shooter
int   Pending = 0
int   ResetTimer = 1 const

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
	if (asEventName != "WeaponFire" || !Shooter)
		return
	endif
	if (Pending > 0)                      ; one of our own forced shots
		Pending -= 1
		return
	endif
	Weapon gun = Shooter.GetEquippedWeapon()
	if (!gun)
		return
	endif
	Pending = ExtraShots
	StartTimer(2.0, ResetTimer)          ; a forced shot that never comes must not swallow a real one
	int forced = 0
	int plain = 0
	int i = 0
	while (i < ExtraShots)
		Utility.Wait(Delay)
		if (FireAction && Shooter.PlayIdleAction(FireAction))
			forced += 1
		else
			Pending -= 1                     ; no WeaponFire event will come for this one
			Ammo rounds = gun.GetAmmo()
			if (rounds && Shooter.GetItemCount(rounds) > 0)
				gun.Fire(Shooter, rounds)
				Shooter.RemoveItem(rounds, 1, true)
				plain += 1
			endif
		endif
		i += 1
	endwhile
	Log("shot " + gun + ": " + forced + " real extra rounds, " + plain + " plain")
EndEvent

Event OnTimer(int aiTimerID)
	if (aiTimerID == ResetTimer)
		Pending = 0
	endif
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
