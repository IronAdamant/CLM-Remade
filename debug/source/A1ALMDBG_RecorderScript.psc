Scriptname A1ALMDBG_RecorderScript extends Quest
{CLM debug recorder - for testing only, never shipped (lives in CLM - Debug Recorder.esp).
Writes to Documents\My Games\Fallout4\Logs\Script\User\CLM.0.log (needs Papyrus logging on in Fallout4Custom.ini):
- the starting state, and the full state again on every game load;
- every watched CLM item (loose mods, unlock holotapes, catalysts) the player gains or loses, with the container it
  came from or went to and the new count;
- every kill by the player, and whether the target was a starred legendary (to match drops to kills);
- every watched perk gained or lost, every change to a CLM configuration global, and every change to the player's
  watched actor values (e.g. jump height: shows a legendary taking effect);
- workbench, Pip-Boy and terminal menus opening and closing (the game pauses scripts in most menus, so changes made
  inside one are logged just after it closes).
Vanilla Papyrus cannot read names, so forms are logged by ID: debug/read_log.py translates them.}

Form[] Property WatchItems Auto Const
Perk[] Property WatchPerks Auto Const
GlobalVariable[] Property WatchGlobals Auto Const
ActorValue[] Property WatchValues Auto Const
float Property Interval = 0.5 Auto Const

string LogName = "CLM"
bool[] perkStates
float[] globalValues
float[] actorValues
bool started
Keyword legendaryKeyword

Event OnInit()
	; a start-game-enabled quest runs OnInit twice (as it is created and as it starts): record once
	If started
		Return
	EndIf
	started = True
	Debug.OpenUserLog(LogName)
	Log("recorder started")
	Register()
	Snapshot()
	StartTimer(Interval)
EndEvent

Event Actor.OnPlayerLoadGame(Actor akSender)
	Debug.OpenUserLog(LogName)  ; user logs close when the game quits; reopening an open one is harmless
	Log("game loaded")
	Register()
	Snapshot()
	StartTimer(Interval)
EndEvent

; Event registrations, repeated on every load: a save made with an older recorder build keeps that build's
; registrations, and OnInit does not run again for an already started quest.
Function Register()
	Actor player = Game.GetPlayer()
	legendaryKeyword = Game.GetFormFromFile(0x001CF26C, "Fallout4.esm") as Keyword  ; EncTypeLegendary
	RemoveAllInventoryEventFilters()
	int i = 0
	While i < WatchItems.Length
		AddInventoryEventFilter(WatchItems[i])
		i += 1
	EndWhile
	RegisterForRemoteEvent(player, "OnItemAdded")
	RegisterForRemoteEvent(player, "OnItemRemoved")
	RegisterForRemoteEvent(player, "OnKill")
	RegisterForRemoteEvent(player, "OnPlayerLoadGame")
	RegisterForMenuOpenCloseEvent("ExamineMenu")     ; weapon/armour workbench
	RegisterForMenuOpenCloseEvent("PipboyMenu")
	RegisterForMenuOpenCloseEvent("TerminalMenu")    ; includes holotapes played on the Pip-Boy
EndFunction

Event ObjectReference.OnItemAdded(ObjectReference akSender, Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akSourceContainer)
	Log("item gained " + aiItemCount + " x " + akBaseItem + " from " + akSourceContainer + " (now " + akSender.GetItemCount(akBaseItem) + ")")
EndEvent

Event ObjectReference.OnItemRemoved(ObjectReference akSender, Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akDestContainer)
	Log("item lost " + aiItemCount + " x " + akBaseItem + " to " + akDestContainer + " (now " + akSender.GetItemCount(akBaseItem) + ")")
EndEvent

Event Actor.OnKill(Actor akSender, Actor akVictim)
	string kind = "normal"
	If legendaryKeyword && akVictim.HasKeyword(legendaryKeyword)
		kind = "LEGENDARY"
	EndIf
	Log("kill " + kind + " " + akVictim.GetActorBase() + " " + akVictim)
EndEvent

Event OnMenuOpenCloseEvent(string asMenuName, bool abOpening)
	If abOpening
		Log("menu opened: " + asMenuName)
	Else
		Log("menu closed: " + asMenuName)
		Check()
	EndIf
EndEvent

Event OnTimer(int aiTimerID)
	Check()
	StartTimer(Interval)
EndEvent

; Record the current state in full and remember it.
Function Snapshot()
	Actor player = Game.GetPlayer()
	perkStates = new bool[0]
	globalValues = new float[0]
	actorValues = new float[0]
	int i = 0
	While i < WatchItems.Length
		int n = player.GetItemCount(WatchItems[i])
		If n > 0
			Log("  carrying " + n + " x " + WatchItems[i])
		EndIf
		i += 1
	EndWhile
	i = 0
	While i < WatchPerks.Length
		bool has = player.HasPerk(WatchPerks[i])
		perkStates.Add(has)
		If has
			Log("  has perk " + WatchPerks[i])
		EndIf
		i += 1
	EndWhile
	i = 0
	While i < WatchGlobals.Length
		float v = WatchGlobals[i].GetValue()
		globalValues.Add(v)
		Log("  global " + WatchGlobals[i] + " = " + v)
		i += 1
	EndWhile
	i = 0
	While i < WatchValues.Length
		float v = player.GetValue(WatchValues[i])
		actorValues.Add(v)
		Log("  actor value " + WatchValues[i] + " = " + v)
		i += 1
	EndWhile
EndFunction

; Log anything polled that changed since the last check (items are logged by their events instead).
Function Check()
	If perkStates == None
		Return
	EndIf
	Actor player = Game.GetPlayer()
	int i = 0
	While i < WatchPerks.Length
		bool has = player.HasPerk(WatchPerks[i])
		If has != perkStates[i]
			If has
				Log("perk gained " + WatchPerks[i])
			Else
				Log("perk lost " + WatchPerks[i])
			EndIf
			perkStates[i] = has
		EndIf
		i += 1
	EndWhile
	i = 0
	While i < WatchGlobals.Length
		float v = WatchGlobals[i].GetValue()
		If v != globalValues[i]
			Log("global " + WatchGlobals[i] + ": " + globalValues[i] + " -> " + v)
			globalValues[i] = v
		EndIf
		i += 1
	EndWhile
	i = 0
	While i < WatchValues.Length
		float v = player.GetValue(WatchValues[i])
		If v != actorValues[i]
			Log("actor value " + WatchValues[i] + ": " + actorValues[i] + " -> " + v)
			actorValues[i] = v
		EndIf
		i += 1
	EndWhile
EndFunction

Function Log(string asText)
	Debug.TraceUser(LogName, asText)
EndFunction
