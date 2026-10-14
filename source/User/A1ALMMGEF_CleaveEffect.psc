Scriptname A1ALMMGEF_CleaveEffect extends ActiveMagicEffect
{CLM 2.1 Cleavin': a melee or unarmed hit also strikes every other actor hostile to the attacker within Radius of
the target with SplashSpell, cast by the attacker (so the kills, XP and aggression are theirs). Ranged hits do
nothing. Companions and the player are never hit.}

Spell     Property SplashSpell           const auto mandatory
Keyword[] Property MeleeTypes            const auto mandatory
{Weapon type keywords that count as melee or unarmed.}
Keyword[] Property ActorTypes            const auto mandatory
{Actor type keywords searched around the target.}
float     Property Radius        = 200.0 const auto

Event OnEffectStart(Actor akTarget, Actor akCaster)
	if (!akTarget || !akCaster || !IsMelee(akCaster.GetEquippedWeapon()))
		return
	endif
	Actor[] struck = new Actor[0]
	int k = 0
	while (k < ActorTypes.Length)
		ObjectReference[] near = akTarget.FindAllReferencesWithKeyword(ActorTypes[k], Radius)
		int i = 0
		while (i < near.Length)
			Actor a = near[i] as Actor
			if (a && a != akTarget && a != akCaster && struck.Find(a) < 0 && !a.IsDead() && a.IsHostileToActor(akCaster))
				struck.Add(a)
				SplashSpell.Cast(akCaster, a)
			endif
			i += 1
		endwhile
		k += 1
	endwhile
	Log("cleaved " + struck.Length + " more around " + akTarget)
EndEvent

bool Function IsMelee(Weapon akWeapon)
	if (!akWeapon)
		return true       ; bare fists
	endif
	int i = 0
	while (i < MeleeTypes.Length)
		if (akWeapon.HasKeyword(MeleeTypes[i]))
			return true
		endif
		i += 1
	endwhile
	return false
EndFunction

; testing traces for the debug recorder (debug/build_recorder.py); release builds strip them with their calls
Function Log(string asText) DebugOnly
	Debug.TraceUser("CLM", GetBaseObject() + " on " + GetTargetActor() + ": " + asText)
EndFunction
