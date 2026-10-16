Scriptname A1ALMMGEF_DragonDashEffect extends ActiveMagicEffect
{CLM 2.1 DragonBlade (AgentSmithGSOM): when the wielder swings, the nearest hostile actor within Range that they are
facing (within MaxAngle degrees) and that is not already within reach gets a dash: the wielder appears right in
front of it. At most once every Cooldown seconds. (Papyrus cannot read the crosshair, so the nearest enemy ahead
stands in for it.)}

float Property Range    = 1500.0 const auto
float Property MaxAngle = 30.0   const auto
float Property Reach    = 200.0  const auto
float Property Cooldown = 2.0    const auto
float Property DashSpeed = 4000.0 const auto
{Units a second (about 57 m/s).}
Keyword[] Property ActorTypes   const auto mandatory
{Actor type keywords searched for the enemy ahead (Game.FindClosestActorFromRef returned the wielder itself).}
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
	Actor foe = None
	float best = Range
	int k = 0
	while (k < ActorTypes.Length)
		ObjectReference[] near = Wielder.FindAllReferencesWithKeyword(ActorTypes[k], Range)
		int i = 0
		while (i < near.Length)
			Actor a = near[i] as Actor
			if (a && a != Wielder && !a.IsDead() && a.IsHostileToActor(Wielder) && Math.abs(Wielder.GetHeadingAngle(a)) <= MaxAngle)
				float d = Wielder.GetDistance(a)
				if (d < best)
					foe = a
					best = d
				endif
			endif
			i += 1
		endwhile
		k += 1
	endwhile
	if (!foe)
		Log("swing: no hostile ahead within range")
	elseif (best <= Reach)
		Log("swing: " + foe + " already within reach")
	else
		float dx = Wielder.GetPositionX() - foe.GetPositionX()
		float dy = Wielder.GetPositionY() - foe.GetPositionY()
		float d2 = Math.sqrt(dx * dx + dy * dy)
		Log("swing: dashed " + best + " units to " + foe)
		; TranslateTo slides the wielder there; MoveTo and SetPosition on the player both put up a loading screen
		; (2.1 testing)
		float face = Wielder.GetAngleZ() + Wielder.GetHeadingAngle(foe)
		Wielder.TranslateTo(foe.GetPositionX() + dx / d2 * 100.0, foe.GetPositionY() + dy / d2 * 100.0, foe.GetPositionZ(), 0.0, 0.0, face, DashSpeed)
		OnCooldown = true
		StartTimer(Cooldown, TimerID)
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
