Scriptname A1ALMQuestConfigInit extends ReferenceAlias
{CLM (2017, recovered 2026): gives the player the configuration holotape once MQ102 stage 6 is done (out of Vault 111), at once on a save already past it, then clears the alias.}

Form Property A1ALMTAPE_Holotape_Config Auto
Quest Property MQ102 Auto Const





Event OnInit()
	If MQ102.IsStageDone(6)
		Game.GetPlayer().AddItem(A1ALMTAPE_Holotape_Config)
		Clear()
	Else
		RegisterForRemoteEvent(MQ102, "OnStageSet")
	EndIf
EndEvent

Event Quest.OnStageSet(Quest akSender, int auiStageID, int auiItemID)
	If akSender == MQ102 && auiStageID == 6
		Game.GetPlayer().AddItem(A1ALMTAPE_Holotape_Config)
		UnregisterForRemoteEvent(MQ102, "OnStageSet")
		Clear()
	EndIf
EndEvent
