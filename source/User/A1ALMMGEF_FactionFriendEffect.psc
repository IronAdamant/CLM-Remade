Scriptname A1ALMMGEF_FactionFriendEffect extends ActiveMagicEffect
{CLM 2.1 Hello Neighbour! (stephen4000): while it is worn, FriendlyFaction is no longer the player's enemy; taking it
off makes them enemies again. Runs from a perk's ability, so wearing several pieces with it still gives one effect.}

Faction Property FriendlyFaction const auto mandatory

Event OnEffectStart(Actor akTarget, Actor akCaster)
	FriendlyFaction.SetPlayerEnemy(false)
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
	FriendlyFaction.SetPlayerEnemy(true)
EndEvent
