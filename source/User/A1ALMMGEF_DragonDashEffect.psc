Scriptname A1ALMMGEF_DragonDashEffect extends ActiveMagicEffect
{CLM 2.1 DragonBlade (AgentSmithGSOM): when the wielder swings, the nearest hostile actor within Range that they are
facing (within MaxAngle degrees) and that is not already within reach gets a dash: the wielder appears right in
front of it. At most once every Cooldown seconds. (Papyrus cannot read the crosshair, so the nearest enemy ahead
stands in for it.)}

float Property Range    = 1500.0 const auto
float Property MaxAngle = 30.0   const auto
float Property Reach    = 200.0  const auto
float Property Cooldown = 2.0    const auto
int            TimerID  = 1      const
Actor Wielder
bool  OnCooldown = false

Event OnEffectStart(Actor akTarget, Actor akCaster)
	Wielder = akTarget
	RegisterForAnimationEvent(akTarget, "weaponSwing")
	Log("started")
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	UnregisterForAnimationEvent(akTarget, "weaponSwing")
	Log("finished")
EndEvent

Event OnAnimationEvent(ObjectReference akSource, string asEventName)
	if (OnCooldown || !Wielder)
		Log("swing: on cooldown")
		return
	endif
	Actor foe = Game.FindClosestActorFromRef(Wielder, Range)
	if (foe && foe != Wielder && !foe.IsDead() && foe.IsHostileToActor(Wielder) && Math.abs(Wielder.GetHeadingAngle(foe)) <= MaxAngle)
		float dx = Wielder.GetPositionX() - foe.GetPositionX()
		float dy = Wielder.GetPositionY() - foe.GetPositionY()
		float d = Math.sqrt(dx * dx + dy * dy)
		if (d > Reach)
			Log("swing: dashed " + d + " units to " + foe)
			Wielder.MoveTo(foe, dx / d * 100.0, dy / d * 100.0, 0.0, false)
			OnCooldown = true
			StartTimer(Cooldown, TimerID)
		else
			Log("swing: " + foe + " already within reach")
		endif
	else
		Log("swing: no hostile ahead within range (closest: " + foe + ")")
	endif
EndEvent

Event OnTimer(int aiTimerID)
	If aiTimerID == TimerID
		OnCooldown = false
	EndIf
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
