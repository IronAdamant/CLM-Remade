Scriptname A1ALMSettingsMigrateScript extends Quest
{CLM 2.0, PC/Xbox: converts the settings of a save made with an older CLM (globals set by the old holotape)
into setting items, once. New games start with the globals at -1 ("never configured") and get nothing.}

MiscObject[] Property Settings Auto Const Mandatory
{In the order: free, loot, op, variants, noperk, nospawn, low, high, picker, all, loothidden, spawn}
GlobalVariable Property A1ALMAFREE Auto Const Mandatory
GlobalVariable Property A1ALMABALANCED Auto Const Mandatory
GlobalVariable Property A1ALMAVAR Auto Const Mandatory
GlobalVariable Property A1ALMAPERK Auto Const Mandatory
GlobalVariable Property A1ALMASPAWN Auto Const Mandatory

bool done

Event OnInit()
	If done
		Return
	EndIf
	done = true
	Actor player = Game.GetPlayer()
	float mode = A1ALMAFREE.GetValue()
	If mode < 0
		Return  ; never configured: the defaults apply
	EndIf
	If mode == 1
		Give(player, 0)
	ElseIf mode == 4
		Give(player, 1)
	EndIf
	If A1ALMABALANCED.GetValue() == 1
		Give(player, 2)
	EndIf
	If A1ALMAVAR.GetValue() == 1
		Give(player, 3)
	EndIf
	If A1ALMAPERK.GetValue() == 0
		Give(player, 4)
	EndIf
	If A1ALMASPAWN.GetValue() == 0
		Give(player, 5)
	Else
		Give(player, 11)  ; 1.09 showed them; since 2.1 that takes a setting
	EndIf
	A1ALMAFREE.SetValue(-1)
EndEvent

Function Give(Actor akPlayer, int aiIndex)
	If akPlayer.GetItemCount(Settings[aiIndex]) == 0
		akPlayer.AddItem(Settings[aiIndex], 1, true)
	EndIf
EndFunction
