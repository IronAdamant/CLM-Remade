Scriptname A1ALMMGEF_ImplodeEffect extends ActiveMagicEffect
{CLM 2.1 Singularity: every hit sets off Blast at the target and pulls the actors hostile to the attacker within
Radius towards it, knocked down. An explosion cannot pull (a negative force does nothing), so each actor is pushed
from a marker placed just beyond it, away from the target. The PlayStation build uses vanilla Fortune Finder's
script instead (the blast on killing hits, no pull).}

Explosion Property Blast                  const auto mandatory
Keyword[] Property ActorTypes             const auto mandatory
Static    Property Marker                 const auto mandatory
float     Property Radius         = 500.0 const auto
float     Property Force          = 3.0   const auto

Event OnEffectStart(Actor akTarget, Actor akCaster)
	if (!akTarget || !akCaster)
		return
	endif
	akTarget.PlaceAtMe(Blast)
	Actor[] pulled = new Actor[0]
	int k = 0
	while (k < ActorTypes.Length)
		ObjectReference[] near = akTarget.FindAllReferencesWithKeyword(ActorTypes[k], Radius)
		int i = 0
		while (i < near.Length)
			Actor a = near[i] as Actor
			if (a && a != akTarget && a != akCaster && pulled.Find(a) < 0 && !a.IsDead() && a.IsHostileToActor(akCaster))
				pulled.Add(a)
				float dx = a.GetPositionX() - akTarget.GetPositionX()
				float dy = a.GetPositionY() - akTarget.GetPositionY()
				float d = Math.sqrt(dx * dx + dy * dy)
				if (d > 1.0)
					ObjectReference m = a.PlaceAtMe(Marker)
					m.MoveTo(a, dx / d * 100.0, dy / d * 100.0, 0.0)
					m.PushActorAway(a, Force)
					m.Delete()
				endif
			endif
			i += 1
		endwhile
		k += 1
	endwhile
	Log("imploded, pulled " + pulled.Length)
EndEvent

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
