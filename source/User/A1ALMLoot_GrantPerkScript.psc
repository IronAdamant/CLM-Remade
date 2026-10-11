Scriptname A1ALMLoot_GrantPerkScript extends Quest
{CLM loot mode: gives the player this plugin's hidden loot perk, whose "Add Leveled List On Death" entries add CLM
drops to whatever the player kills (only while loot mode is on - the perk's own conditions check that). One quest
with this script per plugin (main plugin and each DLC add-on). Checked again on every load, so the perk returns if
anything removed it.}

Perk Property LootPerk Auto Const Mandatory

Event OnInit()
	Grant()
	RegisterForRemoteEvent(Game.GetPlayer(), "OnPlayerLoadGame")
EndEvent

Event Actor.OnPlayerLoadGame(Actor akSender)
	Grant()
EndEvent

Function Grant()
	Actor player = Game.GetPlayer()
	If !player.HasPerk(LootPerk)
		player.AddPerk(LootPerk)
	EndIf
EndFunction
