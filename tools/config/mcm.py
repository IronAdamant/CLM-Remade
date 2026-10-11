"""CLM's optional F4SE add-on: a Mod Configuration Menu (MCM) page that replaces the holotapes.

    python tools/config/mcm.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4" \
        --mcm "D:/Mod Organiser 2 Mod Files/mods/Mod Configuration Menu/Scripts/Source/User"

Run after tools/config/settings.py. Builds mcm/data (shipped as the optional "CLM - MCM" download, PC only; needs F4SE
and MCM) and copies it into the game's Data folder for testing:
    CLM - MCM.esp                       ESL; one start-game quest running A1ALMMCMScript
    Scripts/A1ALMMCMScript.pex          from mcm/source/A1ALMMCMScript.psc (generated)
    MCM/Config/CLM/config.json          the menu: Settings, CLM Perks, Cheat Perks
    MCM/Config/CLM/settings.ini         its defaults
The menu works on the same setting items as the chemistry station and the holotape (tools/config/settings.py), so
all three always agree: changing a menu option gives or takes the item; opening the menu (MCM's OnMCMMenuOpen, and
the pause menu as a fallback) reads the items and perks the player really has. The perk pages add and remove the
110 perks of the perk holotape (found from its terminal fragments).

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
from settings import ITEMS, ctda, OP_EQ  # noqa: E402

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
KEYS = list(ITEMS)                # Settings[] order in the script


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


def config_json(perks) -> dict:
    def switch(text, sid, help_):
        return {'text': text, 'type': 'switcher', 'id': sid, 'help': help_, 'valueOptions': {'sourceType': 'ModSettingBool'}}
    settings = [
        {'text': "<font color='#AAAAAA'>These are the same settings as the \"CLM Setting\" items you can make at a "
                 'chemistry station: changing one here gives or takes that item, and this page always shows what you '
                 'carry.</font>', 'type': 'text'},
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
        switch('Picker mode', 'bPicker:Settings', 'The workbench shows only the families you pick at a chemistry station '
               '(CLM Armour / Spawns / Weapon categories).'),
        {'text': 'Holotapes', 'type': 'section'},
        switch('Holotapes', 'bHolotapes:Settings', 'This menu replaces the configuration and perk holotapes. Turn this on '
               'to get both holotapes (and their recipes) back anyway.'),
    ]
    pages = [{'pageDisplayName': 'Settings', 'content': settings}]
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
                        {'text': 'Settings: crafting mode, OP legendaries, variants, Legendary Picker, loot drop rate.',
                         'type': 'text'},
                        {'text': 'CLM Perks / Cheat Perks: add or remove the perks of the perk holotape.', 'type': 'text'}],
            'pages': pages}


def settings_ini(perks) -> str:
    lines = ['[Settings]', 'iCrafting=0', 'iDropRate=1', 'bShowOP=0', 'bShowVariants=0', 'bHidePerk=0', 'bHideSpawn=0',
             'bPicker=0', 'bHolotapes=0', '', '[Perks]'] + [f'bPerk{i}=0' for i in range(len(perks))]
    return '\n'.join(lines) + '\n'


def script_source(perks) -> str:
    k = KEYS.index
    s = f'''Scriptname {SCRIPT} extends Quest
{{CLM's MCM menu (optional F4SE add-on "CLM - MCM", needs F4SE and Mod Configuration Menu). Generated by
tools/config/mcm.py. Settings are CLM's setting items (the same ones made at a chemistry station): changing a menu
option gives or takes the item, and opening the menu reads what the player carries. Perk pages add and remove the
perk holotape's perks.}}

MiscObject[] Property Settings Auto Const Mandatory
{{In the order: {", ".join(KEYS)}}}
Perk[] Property Perks Auto Const Mandatory
{{In the order of the menu's bPerk<n> settings}}
Form[] Property Holotapes Auto Const Mandatory
{{Configuration holotape, perk holotape}}
GlobalVariable Property {GLOBAL} Auto Const Mandatory
{{1 = the holotapes are given and craftable, 0 = this menu replaces them}}

string Property ModName = "{MOD}" AutoReadOnly

bool initialised

Event OnInit()
	If initialised
		Return
	EndIf
	initialised = true
	SetHolotapes(false)
	Setup()
EndEvent

Event Actor.OnPlayerLoadGame(Actor akSender)
	Setup()
EndEvent

Function Setup()
	RegisterForRemoteEvent(Game.GetPlayer(), "OnPlayerLoadGame")
	RegisterForExternalEvent("OnMCMSettingChange|" + ModName, "OnMCMSettingChange")
	RegisterForExternalEvent("OnMCMMenuOpen|" + ModName, "OnMCMMenuOpen")
	RegisterForMenuOpenCloseEvent("PauseMenu")
EndFunction

Event OnMenuOpenCloseEvent(string asMenuName, bool abOpening)
	If abOpening
		Sync()
	EndIf
EndEvent

Function OnMCMMenuOpen(string asModName)
	Sync()
	MCM.RefreshMenu()
EndFunction

; the menu shows what the player really has (items may have been made or dropped since)
Function Sync()
	Actor player = Game.GetPlayer()
	int crafting = 0
	If Has({k("loot")})
		crafting = 2
	ElseIf Has({k("free")})
		crafting = 1
	EndIf
	MCM.SetModSettingInt(ModName, "iCrafting:Settings", crafting)
	int rate = 1
	If Has({k("low")})
		rate = 0
	ElseIf Has({k("high")})
		rate = 2
	EndIf
	MCM.SetModSettingInt(ModName, "iDropRate:Settings", rate)
	MCM.SetModSettingBool(ModName, "bShowOP:Settings", Has({k("op")}))
	MCM.SetModSettingBool(ModName, "bShowVariants:Settings", Has({k("variants")}))
	MCM.SetModSettingBool(ModName, "bHidePerk:Settings", Has({k("noperk")}))
	MCM.SetModSettingBool(ModName, "bHideSpawn:Settings", Has({k("nospawn")}))
	MCM.SetModSettingBool(ModName, "bPicker:Settings", Has({k("picker")}))
	MCM.SetModSettingBool(ModName, "bHolotapes:Settings", {GLOBAL}.GetValue() != 0)
	int i = 0
	While i < Perks.Length
		MCM.SetModSettingBool(ModName, "bPerk" + i + ":Perks", player.HasPerk(Perks[i]))
		i += 1
	EndWhile
EndFunction

Function OnMCMSettingChange(string asModName, string asID)
	If asID == "iCrafting:Settings"
		int v = MCM.GetModSettingInt(ModName, asID)
		SetItem({k("free")}, v == 1)
		SetItem({k("loot")}, v == 2)
	ElseIf asID == "iDropRate:Settings"
		int v = MCM.GetModSettingInt(ModName, asID)
		SetItem({k("low")}, v == 0)
		SetItem({k("high")}, v == 2)
	ElseIf asID == "bShowOP:Settings"
		SetItem({k("op")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bShowVariants:Settings"
		SetItem({k("variants")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bHidePerk:Settings"
		SetItem({k("noperk")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bHideSpawn:Settings"
		SetItem({k("nospawn")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bPicker:Settings"
		SetItem({k("picker")}, MCM.GetModSettingBool(ModName, asID))
	ElseIf asID == "bHolotapes:Settings"
		SetHolotapes(MCM.GetModSettingBool(ModName, asID))
	Else
		int i = 0
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

bool Function Has(int aiIndex)
	Return Game.GetPlayer().GetItemCount(Settings[aiIndex]) > 0
EndFunction

Function SetItem(int aiIndex, bool abOn)
	Actor player = Game.GetPlayer()
	int n = player.GetItemCount(Settings[aiIndex])
	If abOn && n == 0
		player.AddItem(Settings[aiIndex], 1, true)
	ElseIf !abOn && n > 0
		player.RemoveItem(Settings[aiIndex], n, true)
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
'''
    return s


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
    print(f'{len(perks)} perks')

    # 1. records: the holotape switch in the main plugin, the add-on's quest
    items = ','.join('@' + ITEMS[k][0] for k in KEYS)
    s = ['# Generated by tools/config/mcm.py', f'file | {MAIN}', f'new | GLOB | {GLOBAL}',
         f'file | {ADDON}', 'master | Fallout4.esm', f'master | {MAIN}',
         f'new | QUST | {QUEST}', f'set | {QUEST} | FULL | CLM Mod Configuration Menu',
         f'set | {QUEST} | DNAM\\Flags | 1', f'script | {QUEST} | {SCRIPT}',
         f'prop | {QUEST} | {SCRIPT} | Settings | Array of Object | {items}',
         f'prop | {QUEST} | {SCRIPT} | Perks | Array of Object | ' + ','.join('@' + e for _, e, _ in perks),
         f'prop | {QUEST} | {SCRIPT} | Holotapes | Array of Object | ' + ','.join('@' + e for e in HOLOTAPES),
         f'prop | {QUEST} | {SCRIPT} | {GLOBAL} | Object | @{GLOBAL}']
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

    # 2. raw (main plugin): the switch is 1; holotape recipes need it; a label typo on the perk holotape
    p = Plugin.load(data / MAIN)
    glob = p.by_edid(GLOBAL)
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

    # 3. scripts
    (REPO / 'source' / 'User' / 'A1ALMQuestConfigInit.psc').write_text(
        CONFIG_INIT.format(fid=glob.formid & 0xFFFFFF, main=MAIN), encoding='utf8')
    (OUT / 'source').mkdir(parents=True, exist_ok=True)
    (OUT / 'source' / f'{SCRIPT}.psc').write_text(script_source(perks), encoding='utf8')
    comp = REPO / 'tools' / 'papyrus' / 'compile.py'
    subprocess.run([sys.executable, str(comp), '--game', str(game), 'A1ALMQuestConfigInit'], check=True)
    subprocess.run([sys.executable, str(comp), '--game', str(game), '--f4se', str(OUT / 'source'), '--mcm', str(a.mcm),
                    SCRIPT], check=True)
    shutil.copy(REPO / 'data' / 'SCRIPTS' / 'A1ALMQuestConfigInit.pex', data / 'Scripts' / 'A1ALMQuestConfigInit.pex')

    # 4. the add-on's files: menu, plugin, script - into mcm/data and the game's Data folder
    cfg = OUT / 'data' / 'MCM' / 'Config' / MOD
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / 'config.json').write_text(json.dumps(config_json(perks), indent=2, ensure_ascii=False), encoding='utf8')
    (cfg / 'settings.ini').write_text(settings_ini(perks), encoding='utf8')
    shutil.copy(data / ADDON, OUT / 'data' / ADDON)
    for f in (OUT / 'data').rglob('*'):
        if f.is_file() and f.name != ADDON:
            dest = data / f.relative_to(OUT / 'data')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, dest)
    print(f'{ADDON}: menu with {len(perks)} perks written to mcm/data and {data}')


if __name__ == '__main__':
    main()
