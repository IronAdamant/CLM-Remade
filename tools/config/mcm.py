"""CLM's optional F4SE add-on: a Mod Configuration Menu (MCM) page that replaces the holotapes.

    python tools/config/mcm.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4" \
        --mcm "D:/Mod Organiser 2 Mod Files/mods/Mod Configuration Menu/Scripts/Source/User"

Run after tools/config/settings.py (items, globals), tools/loot/generate.py and tools/config/picker.py. Builds
mcm/data (shipped as the optional "CLM - MCM" download, Nexus only; needs F4SE and MCM) and copies it into the
game's Data folder for testing:
    CLM - MCM.esp                       ESL; one start-game quest running A1ALMMCMScript
    Scripts/A1ALMMCMScript.pex          from mcm/source/A1ALMMCMScript.psc (generated)
    MCM/Config/CLM/config.json          the menu: Settings, Picker, CLM Perks, Cheat Perks
    MCM/Config/CLM/settings.ini         its defaults
Every setting and every pick is also a global in the main plugin (tools/config/settings.py: a recipe accepts the item
OR the global). The menu sets the globals, so F4SE players carry no setting or pick items: when it starts, and
on every save load, any such items the player carries (made earlier at a chemistry station, or given by
the holotape) become their globals. A1ALMMCM = 1 hides the chemistry station's settings and picks meanwhile. The
"Before removing this add-on" button turns everything back into items and A1ALMMCM to 0, so a save stays usable
without the add-on. The perk pages add and remove the 110 perks of the perk holotape (found from its fragments).

Holotapes: the main plugin gets A1ALMHOLOTAPES (1). At 0 the configuration holotape is not given after Vault 111
and neither holotape can be crafted. The add-on sets it to 0 when it starts (removing the holotapes if the player
has them); the menu's "Holotapes" option turns them back on. Without the add-on (Xbox, PlayStation) nothing changes.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
from settings import ITEMS, ctda, OP_EQ, MCM_GLOBAL, setting_global  # noqa: E402
from picker import CATEGORIES, load_families, selector, pick_global  # noqa: E402

MAIN = 'Custom Legendary Modifications Remade.esp'
ADDON = 'CLM - MCM.esp'
MOD = 'CLM'                       # MCM mod name = MCM/Config folder
QUEST, SCRIPT = 'A1ALMMCM_Quest', 'A1ALMMCMScript'
GLOBAL = 'A1ALMHOLOTAPES'
HOLOTAPES = ['A1ALMTAPE_Holotape_Config', 'A1ALMTAPE_Holotape_Perk']
HOLOTAPE_RECIPES = ['co_A1ALMTAPE_Holotape_Config', 'co_A1ALMTAPE_Holotape_Perk', 'co_A1ALMTAPE_Holotape_PerkFREE']
PERK_TERMS = {'A1ALMTERM_Holotape_Perk_Add_RM': 'CLM Perks', 'A1ALMTERM_Holotape_Perk_Cheat_RM': 'Cheat Perks'}
FRAGMENTS = REPO / 'source' / 'User' / 'Fragments' / 'Terminals'
OUT = REPO / 'mcm'
FN_GET_GLOBAL_VALUE = 74
KEYS = list(ITEMS)                # SettingItems[] / SettingGlobals[] order in the script


def perk_list(p) -> list[tuple[str, str, str]]:
    """(page, perk editor ID, name) in holotape order, from the perk terminals' menu items and fragment sources."""
    code = {}
    for f in FRAGMENTS.glob('*.psc'):
        for m in re.finditer(r'Function (Fragment_Terminal_\d+)\(.*?\)(.*?)EndFunction', f.read_text(encoding='utf8'), re.S):
            code[(f.stem.lower(), m.group(1).lower())] = m.group(2)
    out, seen = [], set()
    for term, page in PERK_TERMS.items():
        t = p.by_edid(term)
        script = re.search(rb'Fragments:Terminals:(\w+)', t.get('VMAD').data).group(1).decode().lower()
        for s in t.subrecords:
            if s.sig != 'ITID':
                continue
            body = code.get((script, f'fragment_terminal_{struct.unpack("<H", s.data)[0]:02d}'), '')
            m = re.search(r'AddPerk\((\w+)\)', body)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                perk = p.by_edid(m.group(1))
                assert perk is not None, m.group(1)
                out.append((page, m.group(1), perk.get('FULL').zstring.removeprefix('CLM: ')))
    return out


def family(name: str) -> str:
    return re.split(r' [(\[]', name)[0]


def switch(text, sid, help_):
    return {'text': text, 'type': 'switcher', 'id': sid, 'help': help_, 'valueOptions': {'sourceType': 'ModSettingBool'}}


def config_json(perks, picks, fams, quest_id: int) -> dict:
    settings = [
        {'text': "<font color='#AAAAAA'>CLM's settings and Legendary Picker live here instead of on holotapes and "
                 "\"CLM Setting\" / \"CLM Pick\" items: nothing to carry. (Items you already had are turned into "
                 'these settings.)</font>', 'type': 'text'},
        {'text': 'Crafting', 'type': 'section'},
        {'text': 'Crafting mode', 'type': 'dropdown', 'id': 'iCrafting:Settings',
         'help': 'Costly: legendaries cost components. Free: they cost nothing. Loot mode: they drop from enemies '
                 'instead (carry a CLM holotape to craft its family; OP ones need a Legendary Core).',
         'valueOptions': {'options': ['Costly', 'Free', 'Loot mode'], 'sourceType': 'ModSettingInt'}},
        {'text': 'Loot mode drop rate', 'type': 'dropdown', 'id': 'iDropRate:Settings',
         'help': 'How often loot mode drops legendaries. Standard: common 3%, uncommon 1%, rare 0.3%, OP 0.1% per kill.',
         'valueOptions': {'options': ['Low', 'Standard', 'Higher'], 'sourceType': 'ModSettingInt'}},
        {'text': 'What the workbench shows', 'type': 'section'},
        switch('Show OP legendaries', 'bShowOP:Settings', 'Also show the overpowered legendaries.'),
        switch('Show variants', 'bShowVariants:Settings', 'Show every strength and variant of each legendary.'),
        switch('Hide perk-style legendaries', 'bHidePerk:Settings', 'Hide the legendaries that work like perks (Jumpy, Speedy, Nimble...).'),
        switch('Hide spawning legendaries', 'bHideSpawn:Settings', 'Hide the legendaries that spawn creatures and people.'),
        switch('Picker mode', 'bPicker:Settings', 'The workbench shows only the families turned on in the Legendary '
               'Picker page.'),
        {'text': 'Holotapes', 'type': 'section'},
        switch('Holotapes', 'bHolotapes:Settings', 'This menu replaces the configuration and perk holotapes. Turn this on '
               'to get both holotapes (and their recipes) back anyway.'),
        {'text': 'Before removing this add-on', 'type': 'section'},
        {'text': 'Turn settings and picks back into items', 'type': 'button',
         'help': 'Use this before uninstalling CLM - MCM: your settings and picks become "CLM Setting" / "CLM Pick" '
                 'items again (as without F4SE), the chemistry station shows them again and the holotapes come back. '
                 'Changing any option here afterwards switches the menu back on.',
         'action': {'type': 'CallFunction', 'form': f'{ADDON}|{quest_id:X}', 'function': 'PrepareUninstall', 'params': []}},
    ]
    picker = [{'text': "<font color='#AAAAAA'>With Picker mode on (Settings page), the workbench shows only the families "
                       'turned on here. Your other settings still apply (OP, variants...).</font>', 'type': 'text'}]
    for (kind, cat), names in CATEGORIES.items():
        picker.append({'text': f'CLM {cat}', 'type': 'section'})
        for n in names:
            i = picks.index((kind, n))
            f = fams[(kind, n)]
            label = n.removeprefix('Spawn: ')
            picker.append(switch(label, f'bPick{i}:Picks', f'Show the {len(f["rows"])} {n} legendaries '
                                 f'({"weapon" if kind == "weapon" else "armour"}) while Picker mode is on.'))
    pages = [{'pageDisplayName': 'Settings', 'content': settings},
             {'pageDisplayName': 'Legendary Picker', 'content': picker}]
    for page in PERK_TERMS.values():
        content = [{'text': "<font color='#AAAAAA'>Add or remove the perks of CLM's legendaries directly, without "
                            'wearing the armour (the perk holotape\'s options).</font>', 'type': 'text'}]
        mine = [(i, name) for i, (pg, _, name) in enumerate(perks) if pg == page]
        groups: dict[str, list] = {}
        for i, name in mine:
            groups.setdefault(family(name), []).append((i, name))
        singles = [x for g in groups.values() if len(g) == 1 for x in g]
        for g, members in groups.items():
            if len(members) > 1:
                content.append({'text': g, 'type': 'section'})
                content += [switch(name, f'bPerk{i}:Perks', f'Add or remove the perk "{name}".') for i, name in members]
        if singles:
            content.append({'text': 'Other perks' if len(singles) < len(mine) else 'Perks', 'type': 'section'})
            content += [switch(name, f'bPerk{i}:Perks', f'Add or remove the perk "{name}".') for i, name in singles]
        pages.append({'pageDisplayName': page, 'content': content})
    return {'modName': MOD, 'displayName': 'Custom Legendary Modifications', 'minMcmVersion': 2,
            'content': [{'text': 'Custom Legendary Modifications Remade', 'type': 'section'},
                        {'text': 'Settings: crafting mode, OP legendaries, variants, Picker mode, loot drop rate.',
                         'type': 'text'},
                        {'text': 'Legendary Picker: the families the workbench shows in Picker mode.', 'type': 'text'},
                        {'text': 'CLM Perks / Cheat Perks: add or remove the perks of the perk holotape.', 'type': 'text'}],
            'pages': pages}


def settings_ini(perks, picks) -> str:
    lines = ['[Settings]', 'iCrafting=0', 'iDropRate=1', 'bShowOP=0', 'bShowVariants=0', 'bHidePerk=0', 'bHideSpawn=0',
             'bPicker=0', 'bHolotapes=0', '', '[Picks]'] + [f'bPick{i}=0' for i in range(len(picks))] + \
        ['', '[Perks]'] + [f'bPerk{i}=0' for i in range(len(perks))]
    return '\n'.join(lines) + '\n'


def script_source(perks, pick_items: list[tuple[str, int]]) -> str:
    k = KEYS.index
    lookup = '\n'.join(f'\t{"If" if i == 0 else "ElseIf"} aiIndex == {i}\n'
                       f'\t\tReturn Game.GetFormFromFile(0x{fid:06X}, "{plugin}")'
                       for i, (plugin, fid) in enumerate(pick_items))
    return f'''Scriptname {SCRIPT} extends Quest
{{CLM's MCM menu (optional F4SE add-on "CLM - MCM", needs F4SE and Mod Configuration Menu). Generated by
tools/config/mcm.py. Every CLM setting and pick is also a global: a recipe accepts the item or the global. The menu
sets the globals, and turns any setting / pick items the player carries into them, so nothing is carried.
PrepareUninstall turns everything back into items before the add-on is removed.}}

MiscObject[] Property SettingItems Auto Const Mandatory
{{In the order: {", ".join(KEYS)}}}
GlobalVariable[] Property SettingGlobals Auto Const Mandatory
{{Same order}}
GlobalVariable[] Property PickGlobals Auto Const Mandatory
{{In the order of the menu's bPick<n> settings; the pick items are found with PickItem}}
Perk[] Property Perks Auto Const Mandatory
{{In the order of the menu's bPerk<n> settings}}
Form[] Property Holotapes Auto Const Mandatory
{{Configuration holotape, perk holotape}}
GlobalVariable Property {GLOBAL} Auto Const Mandatory
{{1 = the holotapes are given and craftable, 0 = this menu replaces them}}
GlobalVariable Property {MCM_GLOBAL} Auto Const Mandatory
{{1 = this menu runs: the chemistry station hides the settings and picks}}

string Property ModName = "{MOD}" AutoReadOnly

bool initialised
; the player's changes in the menu: a Sync running meanwhile stops, so it never writes an old value back
int changes

Event OnInit()
	If initialised
		Return
	EndIf
	initialised = true
	{MCM_GLOBAL}.SetValue(1)
	SetHolotapes(false)
	Setup()
	Sync()
EndEvent

Event Actor.OnPlayerLoadGame(Actor akSender)
	Setup()
	Sync()
EndEvent

; Sync never runs while the menu is open: it takes a few seconds (hundreds of calls), and a change made meanwhile
; would be overwritten by the old value (it used to run whenever the pause menu opened)
Function Setup()
	RegisterForRemoteEvent(Game.GetPlayer(), "OnPlayerLoadGame")
	RegisterForExternalEvent("OnMCMSettingChange|" + ModName, "OnMCMSettingChange")
	UnregisterForExternalEvent("OnMCMMenuOpen|" + ModName)
	UnregisterForMenuOpenCloseEvent("PauseMenu")
	RegisterForMenuOpenCloseEvent("TerminalMenu")
	RegisterForMenuOpenCloseEvent("TerminalHolotapeMenu")
EndFunction

; the holotapes (when turned back on) change settings and perks too
Event OnMenuOpenCloseEvent(string asMenuName, bool abOpening)
	If !abOpening && {GLOBAL}.GetValue() != 0
		Sync()
	EndIf
EndEvent

; setting and pick items the player carries (made at a chemistry station before, or from the holotape) -> globals
Function Absorb()
	If {MCM_GLOBAL}.GetValue() != 1
		Return
	EndIf
	Actor player = Game.GetPlayer()
	int i = 0
	While i < SettingItems.Length
		int n = player.GetItemCount(SettingItems[i])
		If n > 0
			player.RemoveItem(SettingItems[i], n, true)
			SetSetting(i, true)
		EndIf
		i += 1
	EndWhile
	i = 0
	While i < PickGlobals.Length
		Form pick = PickItem(i)
		If pick
			int n = player.GetItemCount(pick)
			If n > 0
				player.RemoveItem(pick, n, true)
				PickGlobals[i].SetValue(1)
			EndIf
		EndIf
		i += 1
	EndWhile
EndFunction

; the menu shows the real state (globals and perks belong to the save; the menu's values are shared by all saves)
Function Sync()
	Absorb()
	int start = changes
	int crafting = 0
	If On({k("loot")})
		crafting = 2
	ElseIf On({k("free")})
		crafting = 1
	EndIf
	PutInt("iCrafting:Settings", crafting, start)
	int rate = 1
	If On({k("low")})
		rate = 0
	ElseIf On({k("high")})
		rate = 2
	EndIf
	PutInt("iDropRate:Settings", rate, start)
	Put("bShowOP:Settings", On({k("op")}), start)
	Put("bShowVariants:Settings", On({k("variants")}), start)
	Put("bHidePerk:Settings", On({k("noperk")}), start)
	Put("bHideSpawn:Settings", On({k("nospawn")}), start)
	Put("bPicker:Settings", On({k("picker")}), start)
	Put("bHolotapes:Settings", {GLOBAL}.GetValue() != 0, start)
	int i = 0
	While i < PickGlobals.Length && changes == start
		Put("bPick" + i + ":Picks", PickGlobals[i].GetValue() == 1, start)
		i += 1
	EndWhile
	Actor player = Game.GetPlayer()
	i = 0
	While i < Perks.Length && changes == start
		Put("bPerk" + i + ":Perks", player.HasPerk(Perks[i]), start)
		i += 1
	EndWhile
	If changes == start
		MCM.RefreshMenu()
	EndIf
EndFunction

; writes a value unless the player changed something since the Sync began
Function Put(string asID, bool abOn, int aiStart)
	If changes == aiStart
		MCM.SetModSettingBool(ModName, asID, abOn)
	EndIf
EndFunction

Function PutInt(string asID, int aiValue, int aiStart)
	If changes == aiStart
		MCM.SetModSettingInt(ModName, asID, aiValue)
	EndIf
EndFunction

Function OnMCMSettingChange(string asModName, string asID)
	changes += 1
	{MCM_GLOBAL}.SetValue(1)
	If asID == "iCrafting:Settings"
		int v = MCM.GetModSettingInt(ModName, asID)
		SetSetting({k("free")}, v == 1)
		SetSetting({k("loot")}, v == 2)
	ElseIf asID == "iDropRate:Settings"
		int v = MCM.GetModSettingInt(ModName, asID)
		SetSetting({k("low")}, v == 0)
		SetSetting({k("high")}, v == 2)
	ElseIf asID == "bShowOP:Settings"
		SetSetting({k("op")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bShowVariants:Settings"
		SetSetting({k("variants")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bHidePerk:Settings"
		SetSetting({k("noperk")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bHideSpawn:Settings"
		SetSetting({k("nospawn")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bPicker:Settings"
		SetSetting({k("picker")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bHolotapes:Settings"
		SetHolotapes(MCM.GetModSettingBool(ModName, asID))
	Else
		int i = 0
		While i < PickGlobals.Length
			If asID == "bPick" + i + ":Picks"
				SetPick(i, MCM.GetModSettingBool(ModName, asID))
				Return
			EndIf
			i += 1
		EndWhile
		i = 0
		While i < Perks.Length
			If asID == "bPerk" + i + ":Perks"
				If MCM.GetModSettingBool(ModName, asID)
					Game.GetPlayer().AddPerk(Perks[i])
				Else
					Game.GetPlayer().RemovePerk(Perks[i])
				EndIf
				Return
			EndIf
			i += 1
		EndWhile
	EndIf
EndFunction

bool Function On(int aiIndex)
	Return SettingGlobals[aiIndex].GetValue() == 1 || Game.GetPlayer().GetItemCount(SettingItems[aiIndex]) > 0
EndFunction

; a setting is its global from now on; any item of it goes (it would keep the setting on)
Function SetSetting(int aiIndex, bool abOn)
	SettingGlobals[aiIndex].SetValue(abOn as int)
	If abOn
		If aiIndex == {k("free")}
			SettingGlobals[{k("loot")}].SetValue(0)
		ElseIf aiIndex == {k("loot")}
			SettingGlobals[{k("free")}].SetValue(0)
		ElseIf aiIndex == {k("low")}
			SettingGlobals[{k("high")}].SetValue(0)
		ElseIf aiIndex == {k("high")}
			SettingGlobals[{k("low")}].SetValue(0)
		EndIf
	EndIf
	Actor player = Game.GetPlayer()
	int n = player.GetItemCount(SettingItems[aiIndex])
	If n > 0
		player.RemoveItem(SettingItems[aiIndex], n, true)
	EndIf
EndFunction

Function SetPick(int aiIndex, bool abOn)
	PickGlobals[aiIndex].SetValue(abOn as int)
	Form pick = PickItem(aiIndex)
	If pick
		int n = Game.GetPlayer().GetItemCount(pick)
		If n > 0
			Game.GetPlayer().RemoveItem(pick, n, true)
		EndIf
	EndIf
EndFunction

Function SetHolotapes(bool abOn)
	Actor player = Game.GetPlayer()
	{GLOBAL}.SetValue(abOn as int)
	int i = 0
	While i < Holotapes.Length
		int n = player.GetItemCount(Holotapes[i])
		If abOn && n == 0
			player.AddItem(Holotapes[i], 1, true)
		ElseIf !abOn && n > 0
			player.RemoveItem(Holotapes[i], n, true)
		EndIf
		i += 1
	EndWhile
EndFunction

; before the add-on is removed: everything back to items (the way CLM works without F4SE)
Function PrepareUninstall()
	{MCM_GLOBAL}.SetValue(0)
	SetHolotapes(true)
	MCM.SetModSettingBool(ModName, "bHolotapes:Settings", true)
	Actor player = Game.GetPlayer()
	int i = 0
	While i < SettingItems.Length
		If SettingGlobals[i].GetValue() == 1
			SettingGlobals[i].SetValue(0)
			If player.GetItemCount(SettingItems[i]) == 0
				player.AddItem(SettingItems[i], 1, true)
			EndIf
		EndIf
		i += 1
	EndWhile
	i = 0
	While i < PickGlobals.Length
		If PickGlobals[i].GetValue() == 1
			PickGlobals[i].SetValue(0)
			Form pick = PickItem(i)
			If pick && player.GetItemCount(pick) == 0
				player.AddItem(pick, 1, true)
			EndIf
		EndIf
		i += 1
	EndWhile
	MCM.RefreshMenu()
	Debug.Notification("CLM: settings and picks are items again; holotapes are back.")
	Debug.MessageBox("CLM: your settings and picks are items again (Misc), and the holotapes are back. You can now remove CLM - MCM.")
EndFunction

; pick item n
Form Function PickItem(int aiIndex)
{lookup}
	EndIf
	Return None
EndFunction
'''


CONFIG_INIT = '''Scriptname A1ALMQuestConfigInit extends ReferenceAlias
{{CLM (2017, recovered 2026): gives the player the configuration holotape once MQ102 stage 6 is done (out of Vault 111), at once on a save already past it, then clears the alias.
2.0: not when A1ALMHOLOTAPES is 0 (the optional MCM menu replaces the holotape). Read with GetFormFromFile, so the
alias needs no new property. Generated by tools/config/mcm.py.}}

Form Property A1ALMTAPE_Holotape_Config Auto
Quest Property MQ102 Auto Const

Event OnInit()
	If MQ102.IsStageDone(6)
		Give()
	Else
		RegisterForRemoteEvent(MQ102, "OnStageSet")
	EndIf
EndEvent

Event Quest.OnStageSet(Quest akSender, int auiStageID, int auiItemID)
	If akSender == MQ102 && auiStageID == 6
		UnregisterForRemoteEvent(MQ102, "OnStageSet")
		Give()
	EndIf
EndEvent

Function Give()
	GlobalVariable holotapes = Game.GetFormFromFile(0x{fid:06X}, "{main}") as GlobalVariable
	If !holotapes || holotapes.GetValue() != 0
		Game.GetPlayer().AddItem(A1ALMTAPE_Holotape_Config)
	EndIf
	Clear()
EndFunction
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    ap.add_argument('--mcm', required=True, type=Path, help="MCM's Scripts/Source/User folder (MCM.psc)")
    a = ap.parse_args()
    ack, game = Path(a.ack), Path(a.game)
    data = game / 'Data'
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord

    perks = perk_list(Plugin.load(data / MAIN))
    fams = load_families()
    picks = sorted(fams)
    print(f'{len(perks)} perks, {len(picks)} picks')

    # 1. records: the holotape switch in the main plugin, the add-on's quest
    obj = lambda edids: ','.join('@' + e for e in edids)
    s = ['# Generated by tools/config/mcm.py', f'file | {MAIN}', f'new | GLOB | {GLOBAL}',
         f'file | {ADDON}', 'master | Fallout4.esm', f'master | {MAIN}',
         f'new | QUST | {QUEST}', f'set | {QUEST} | FULL | CLM Mod Configuration Menu',
         f'set | {QUEST} | DNAM\\Flags | 1', f'script | {QUEST} | {SCRIPT}',
         f'propremove | {QUEST} | {SCRIPT} | Settings',
         f'prop | {QUEST} | {SCRIPT} | SettingItems | Array of Object | {obj(ITEMS[k][0] for k in KEYS)}',
         f'prop | {QUEST} | {SCRIPT} | SettingGlobals | Array of Object | {obj(setting_global(k) for k in KEYS)}',
         f'prop | {QUEST} | {SCRIPT} | PickGlobals | Array of Object | {obj(pick_global(*f) for f in picks)}',
         f'prop | {QUEST} | {SCRIPT} | Perks | Array of Object | {obj(e for _, e, _ in perks)}',
         f'prop | {QUEST} | {SCRIPT} | Holotapes | Array of Object | {obj(HOLOTAPES)}',
         f'prop | {QUEST} | {SCRIPT} | {GLOBAL} | Object | @{GLOBAL}',
         f'prop | {QUEST} | {SCRIPT} | {MCM_GLOBAL} | Object | @{MCM_GLOBAL}']
    spec = HERE / 'mcm.spec'
    spec.write_text('\n'.join(s) + '\n', encoding='utf8')
    cmd = [sys.executable, '-m', 'ack', 'xedit', 'run', 'build', MAIN, '--save', '--timeout', '600', '--param', f'SPEC={spec}']
    if (data / ADDON).exists():
        cmd += ['--also-load', ADDON]
    subprocess.run(cmd, cwd=ack, capture_output=True, text=True)
    result = (sorted((ack / 'private' / 'runs').glob('*-build'))[-1] / 'result.txt').read_text(encoding='utf8')
    print(result.splitlines()[0])
    if ' 0 errors' not in result.splitlines()[0]:
        raise SystemExit('\n'.join(l for l in result.splitlines() if 'ERR' in l))
    spec.unlink()

    # 2. raw (main plugin): the switch is 1; holotape recipes need it; a label typo on the perk holotape
    p = Plugin.load(data / MAIN)
    glob = p.by_edid(GLOBAL)
    if glob.get('FLTV') is None:
        glob.subrecords[:] = [glob.subrecords[0], Subrecord('FNAM', b'f'), Subrecord('FLTV', struct.pack('<f', 1.0))]
        glob.mark_dirty()
    cond = ctda(OP_EQ, 1.0, FN_GET_GLOBAL_VALUE, glob.formid)
    for e in HOLOTAPE_RECIPES:
        r = p.by_edid(e)
        if any(x.sig == 'CTDA' and x.data == cond for x in r.subrecords):
            continue
        at = next(i for i, x in enumerate(r.subrecords) if x.sig == 'CNAM')
        r.subrecords.insert(at, Subrecord('CTDA', cond))
        r.mark_dirty()
    for x in p.by_edid('A1ALMTERM_Holotape_Perk_Add_RM').subrecords:
        if x.sig == 'ITXT' and x.data.startswith(b'Add Perk -J'):
            x.data = x.data.replace(b'Add Perk -J', b'Add Perk - J')
            p.by_edid('A1ALMTERM_Holotape_Perk_Add_RM').mark_dirty()
    p.save(data / MAIN)

    # 3. scripts (pick items are found by plugin and local ID)
    pick_items = [(MAIN, p.by_edid(selector(*f)).formid & 0xFFFFFF) for f in picks]
    (REPO / 'source' / 'User' / 'A1ALMQuestConfigInit.psc').write_text(
        CONFIG_INIT.format(fid=glob.formid & 0xFFFFFF, main=MAIN), encoding='utf8')
    (OUT / 'source').mkdir(parents=True, exist_ok=True)
    (OUT / 'source' / f'{SCRIPT}.psc').write_text(script_source(perks, pick_items), encoding='utf8')
    comp = REPO / 'tools' / 'papyrus' / 'compile.py'
    subprocess.run([sys.executable, str(comp), '--game', str(game), 'A1ALMQuestConfigInit'], check=True)
    subprocess.run([sys.executable, str(comp), '--game', str(game), '--f4se', str(OUT / 'source'), '--mcm', str(a.mcm),
                    SCRIPT], check=True)
    shutil.copy(REPO / 'data' / 'SCRIPTS' / 'A1ALMQuestConfigInit.pex', data / 'Scripts' / 'A1ALMQuestConfigInit.pex')

    # 4. the add-on's files: menu, plugin, script - into mcm/data and the game's Data folder
    quest_id = Plugin.load(data / ADDON).by_edid(QUEST).formid & 0xFFF
    cfg = OUT / 'data' / 'MCM' / 'Config' / MOD
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / 'config.json').write_text(json.dumps(config_json(perks, picks, fams, quest_id), indent=2, ensure_ascii=False),
                                     encoding='utf8')
    (cfg / 'settings.ini').write_text(settings_ini(perks, picks), encoding='utf8')
    shutil.copy(data / ADDON, OUT / 'data' / ADDON)
    for f in (OUT / 'data').rglob('*'):
        if f.is_file() and f.name != ADDON:
            dest = data / f.relative_to(OUT / 'data')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, dest)
    print(f'{ADDON}: menu with {len(perks)} perks and {len(picks)} picks written to mcm/data and {data}')


if __name__ == '__main__':
    main()
