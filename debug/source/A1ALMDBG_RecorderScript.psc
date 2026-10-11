Scriptname A1ALMDBG_RecorderScript extends Quest
{CLM debug recorder - for testing only, never shipped (lives in CLM - Debug Recorder.esp).
Writes to Documents\My Games\Fallout4\Logs\Script\User\CLM.0.log (needs Papyrus logging on in Fallout4Custom.ini):
- the starting state, and the full state again on every game load;
- every change in how many of each watched CLM item the player carries (loose mods, unlock holotapes);
- every unlock perk gained or lost;
- every change to a CLM configuration global (what the configuration holotape sets);
- workbench and Pip-Boy menus opening and closing (the game pauses scripts in most menus, so changes made inside
  one are logged just after it closes).
Vanilla Papyrus cannot read names, so forms are logged by ID: tools/debug/read_log.py translates them.}

Form[] Property WatchItems Auto Const
Perk[] Property WatchPerks Auto Const
GlobalVariable[] Property WatchGlobals Auto Const
float Property Interval = 0.5 Auto Const

string LogName = "CLM"
int[] itemCounts
bool[] perkStates
float[] globalValues
bool started

Event OnInit()
	; a start-game-enabled quest runs OnInit twice (as it is created and as it starts): record once
	If started
		Return
	EndIf
	started = True
	Debug.OpenUserLog(LogName)
	Log("recorder started")
	Snapshot()
	RegisterForRemoteEvent(Game.GetPlayer(), "OnPlayerLoadGame")
	RegisterForMenuOpenCloseEvent("ExamineMenu")     ; weapon/armour workbench
	RegisterForMenuOpenCloseEvent("PipboyMenu")
	RegisterForMenuOpenCloseEvent("TerminalMenu")    ; includes holotapes played on the Pip-Boy
	StartTimer(Interval)
EndEvent

Event Actor.OnPlayerLoadGame(Actor akSender)
	Debug.OpenUserLog(LogName)  ; user logs close when the game quits; reopening an open one is harmless
	Log("game loaded")
	Snapshot()
	StartTimer(Interval)
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
	itemCounts = new int[0]
	perkStates = new bool[0]
	globalValues = new float[0]
	int i = 0
	While i < WatchItems.Length
		int n = player.GetItemCount(WatchItems[i])
		itemCounts.Add(n)
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
EndFunction

; Log anything that changed since the last check.
Function Check()
	If itemCounts == None
		Return
	EndIf
	Actor player = Game.GetPlayer()
	int i = 0
	While i < WatchItems.Length
		int n = player.GetItemCount(WatchItems[i])
		If n != itemCounts[i]
			Log("item " + WatchItems[i] + ": " + itemCounts[i] + " -> " + n)
			itemCounts[i] = n
		EndIf
		i += 1
	EndWhile
	i = 0
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
EndFunction

Function Log(string asText)
	Debug.TraceUser(LogName, asText)
EndFunction
