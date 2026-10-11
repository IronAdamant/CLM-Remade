"""CLM 2.0 settings as items: one configuration that works on every platform (author's "Option 2", 2026-10-12).

    python tools/config/settings.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4" items
    python tools/loot/generate.py ...           (loot mode reads the setting items)
    python tools/config/settings.py --ack ... --game ... conditions

PlayStation mods cannot run custom scripts, so 1.09's holotape (script fragments setting globals) did nothing there.
Settings are now weightless items: carrying one turns a setting on, dropping it turns it off. A player carrying none
gets the defaults: Costly crafting, Balanced (OP hidden), variants hidden, perk-style and spawning legendaries shown,
Standard loot drop rate. Settings are crafted at the chemistry station (category "CLM Settings"); on PC and Xbox the
configuration holotape is a front end that gives and removes the same items. A one-time quest converts the old global
settings of existing saves into items (PC/Xbox).

items:      setting items, the "CLM Settings" chem station category and its recipes, the rebuilt holotape menus
            (A1ALMSettingsTerminalScript), the migration quest; old globals' defaults become -1 ("never configured").
conditions: every costly/FREE recipe's global checks become item checks, and holotape items hide while active.
"""
from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / 'tools' / 'loot'))
from generate import rate_welcome  # noqa: E402  (the drop-rate page describes loot mode's RATES)
MAIN = 'Custom Legendary Modifications Remade.esp'
ADDONS = ['CLM - Automatron.esp', 'CLM - Far Harbor.esp', 'CLM - Nuka-World.esp', 'CLM - Contraptions.esp']
TEMPLATE_MISC = '@miscmod_mod_RailwayRifle_Scope_ScopeShort_Recon'
MODEL = 'Props\\Holotape_Prop.nif'
CATEGORY = ('A1ALMKW_RecipeFilter_Settings', 'CLM Settings')
CONFIG_TERM, RATE_TERM = 'A1ALMTERM_Holotape_Config_RM', 'A1ALMTERM_Holotape_Config_LootRate'
TERM_SCRIPT, MIGRATE_SCRIPT, MIGRATE_QUEST = 'A1ALMSettingsTerminalScript', 'A1ALMSettingsMigrateScript', 'A1ALMQUST_SettingsMigrate'

# key -> (editor ID, item name, chem station recipe text)
ITEMS = {
    'free':     ('A1ALMSET_ModeFree', 'CLM Setting: Free crafting', 'Legendaries cost nothing to craft.'),
    'loot':     ('A1ALMSET_ModeLoot', 'CLM Setting: Loot mode', 'Legendaries drop from enemies instead of being crafted.'),
    'op':       ('A1ALMSET_ShowOP', 'CLM Setting: Show OP legendaries', 'Also show the overpowered legendaries.'),
    'variants': ('A1ALMSET_ShowVariants', 'CLM Setting: Show variants', 'Show every variant of each legendary.'),
    'noperk':   ('A1ALMSET_HidePerk', 'CLM Setting: Hide perk-style legendaries',
                 'Hide the legendaries that work like perks (Jumpy, Speedy, Nimble...).'),
    'nospawn':  ('A1ALMSET_HideSpawn', 'CLM Setting: Hide spawning legendaries',
                 'Hide the legendaries that spawn creatures and people.'),
    'low':      ('A1ALMSET_DropLow', 'CLM Setting: Low drop rate', 'Loot mode: legendaries drop extremely rarely.'),
    'high':     ('A1ALMSET_DropHigh', 'CLM Setting: Higher drop rate', 'Loot mode: legendaries drop generously.'),
}
# mutually exclusive settings: crafting one takes the other back
EXCLUSIVE = {'free': 'loot', 'loot': 'free', 'low': 'high', 'high': 'low'}
NEEDS = {'low': 'loot', 'high': 'loot'}   # offered at the chemistry station only with this setting carried
OLD = {'A1ALMAFREE', 'A1ALMAPERK', 'A1ALMASPAWN', 'A1ALMAVAR', 'A1ALMABALANCED', 'A1ALMAWPN'}

# holotape: (item ID, text, action [(key, add?)], shown when [(key, carried?)] - any one true)
CONFIG_MENU = [
    (1, 'Crafting: Free', [('free', True), ('loot', False)], [('free', False)]),
    (2, 'Crafting: Costly', [('free', False), ('loot', False)], [('free', True), ('loot', True)]),
    (3, 'Loot version - Hunt for legendaries', [('loot', True), ('free', False)], [('loot', False)]),
    (4, 'Show OP legendaries', [('op', True)], [('op', False)]),
    (5, 'Balanced only - hide OP legendaries', [('op', False)], [('op', True)]),
    (6, 'Show every variant', [('variants', True)], [('variants', False)]),
    (7, 'Hide variants', [('variants', False)], [('variants', True)]),
    (8, 'Hide perk-style legendaries', [('noperk', True)], [('noperk', False)]),
    (9, 'Show perk-style legendaries', [('noperk', False)], [('noperk', True)]),
    (10, 'Hide spawning legendaries', [('nospawn', True)], [('nospawn', False)]),
    (11, 'Show spawning legendaries', [('nospawn', False)], [('nospawn', True)]),
]
RATE_MENU = [
    (1, 'Low - extremely rare drops', [('low', True), ('high', False)], [('low', False)]),
    (2, 'Standard - the intended rate', [('low', False), ('high', False)], [('low', True), ('high', True)]),
    (3, 'Higher - generous drops', [('high', True), ('low', False)], [('high', False)]),
]
SUBMENU_SHOWN = {(CONFIG_TERM, 12): [('loot', True)]}   # the drop-rate page: only in loot mode
CONFIG_WELCOME = ('Welcome to the CLM Config Holotape! Settings are items you carry (weightless, under Misc): this '
                  'holotape gives and takes them for you, or craft them at any chemistry station under "CLM Settings". '
                  'With none, you get Costly crafting, Balanced (no OP legendaries) and no variants. In Loot mode '
                  'legendaries drop from enemies (starred ones drop far more); carry a CLM holotape to craft its '
                  'family; OP legendaries need a Legendary Core.')
ITEM_SIGS = {'ITXT', 'RNAM', 'ANAM', 'ITID', 'TNAM', 'UNAM', 'VNAM', 'CTDA', 'CIS1', 'CIS2', 'INAM', 'SNAM', 'BSIZ'}
FN_GET_ITEM_COUNT, FN_GET_GLOBAL_VALUE = 47, 74
OP_EQ, OP_GE, FLAG_OR = 0, 3 << 5, 1
RUN_SUBJECT, RUN_REFERENCE, PLAYER_REF = 0, 2, 0x14


def ctda(op_flags: int, value: float, function: int, param1: int, run_on: int = RUN_SUBJECT, ref: int = 0) -> bytes:
    return struct.pack('<B3sfH2sIIIIi', op_flags, b'\0\0\0', value, function, b'\0\0', param1, 0, run_on, ref, -1)


def build(ack: Path, spec_lines: list[str], extra: list[str] = ()) -> None:
    spec = HERE / 'settings.spec'
    spec.write_text('\n'.join(spec_lines) + '\n', encoding='utf8')
    subprocess.run([sys.executable, "-m", "ack", "xedit", "run", "build", MAIN, '--save', '--timeout', '600',
                        '--param', f'SPEC={spec}', *extra], cwd=ack, capture_output=True, text=True)
    run = sorted((ack / 'private' / 'runs').glob('*-build'))[-1]
    first = (run / 'result.txt').read_text(encoding='utf8').splitlines()[0]
    print(first)
    if ' 0 errors' not in first:
        raise SystemExit((run / 'result.txt').read_text(encoding='utf8'))


def terminal_script() -> str:
    keys = list(ITEMS)
    lines = [f'Scriptname {TERM_SCRIPT} extends Terminal',
             '{CLM settings holotape (PC/Xbox): gives and takes the setting items - the same items crafted at the',
             'chemistry station, which are what every recipe checks. Generated by tools/config/settings.py.}', '',
             'MiscObject[] Property Settings Auto Const Mandatory',
             '{In the order: ' + ', '.join(keys) + '}',
             'int Property Page = 0 Auto Const',
             '{0 = main configuration menu, 1 = loot drop rate menu}', '',
             'Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)']
    for page, menu in ((0, CONFIG_MENU), (1, RATE_MENU)):
        lines.append(f'\t{"If" if page == 0 else "ElseIf"} Page == {page}')
        for i, (item, text, action, _) in enumerate(menu):
            lines.append(f'\t\t{"If" if i == 0 else "ElseIf"} auiMenuItemID == {item}')
            for key, on in action:
                lines.append(f'\t\t\tSetSetting({keys.index(key)}, {"true" if on else "false"})')
            lines.append(f'\t\t\tDebug.Notification("CLM: {text}")')
        lines.append('\t\tEndIf')
    lines += ['\tEndIf', 'EndEvent', '',
              'Function SetSetting(int aiIndex, bool abOn)',
              '\tActor player = Game.GetPlayer()',
              '\tint n = player.GetItemCount(Settings[aiIndex])',
              '\tIf abOn && n == 0',
              '\t\tplayer.AddItem(Settings[aiIndex], 1, true)',
              '\tElseIf !abOn && n > 0',
              '\t\tplayer.RemoveItem(Settings[aiIndex], n, true)',
              '\tEndIf',
              'EndFunction', '']
    return '\n'.join(lines)


def migrate_script() -> str:
    keys = list(ITEMS)
    return '\n'.join([
        f'Scriptname {MIGRATE_SCRIPT} extends Quest',
        '{CLM 2.0, PC/Xbox: converts the settings of a save made with an older CLM (globals set by the old holotape)',
        'into setting items, once. New games start with the globals at -1 ("never configured") and get nothing.}', '',
        'MiscObject[] Property Settings Auto Const Mandatory',
        '{In the order: ' + ', '.join(keys) + '}',
        'GlobalVariable Property A1ALMAFREE Auto Const Mandatory',
        'GlobalVariable Property A1ALMABALANCED Auto Const Mandatory',
        'GlobalVariable Property A1ALMAVAR Auto Const Mandatory',
        'GlobalVariable Property A1ALMAPERK Auto Const Mandatory',
        'GlobalVariable Property A1ALMASPAWN Auto Const Mandatory', '',
        'bool done', '',
        'Event OnInit()',
        '\tIf done',
        '\t\tReturn',
        '\tEndIf',
        '\tdone = true',
        '\tActor player = Game.GetPlayer()',
        '\tfloat mode = A1ALMAFREE.GetValue()',
        '\tIf mode < 0',
        '\t\tReturn  ; never configured: the defaults apply',
        '\tEndIf',
        f'\tIf mode == 1\n\t\tGive(player, {keys.index("free")})\n\tElseIf mode == 4\n\t\tGive(player, {keys.index("loot")})\n\tEndIf',
        f'\tIf A1ALMABALANCED.GetValue() == 1\n\t\tGive(player, {keys.index("op")})\n\tEndIf',
        f'\tIf A1ALMAVAR.GetValue() == 1\n\t\tGive(player, {keys.index("variants")})\n\tEndIf',
        f'\tIf A1ALMAPERK.GetValue() == 0\n\t\tGive(player, {keys.index("noperk")})\n\tEndIf',
        f'\tIf A1ALMASPAWN.GetValue() == 0\n\t\tGive(player, {keys.index("nospawn")})\n\tEndIf',
        '\tA1ALMAFREE.SetValue(-1)',
        'EndEvent', '',
        'Function Give(Actor akPlayer, int aiIndex)',
        '\tIf akPlayer.GetItemCount(Settings[aiIndex]) == 0',
        '\t\takPlayer.AddItem(Settings[aiIndex], 1, true)',
        '\tEndIf',
        'EndFunction', ''])


def cmd_items(ack: Path, game: Path) -> None:
    data = game / 'Data'
    for name, text in ((TERM_SCRIPT, terminal_script()), (MIGRATE_SCRIPT, migrate_script())):
        (REPO / 'source' / 'User' / f'{name}.psc').write_text(text, encoding='utf8')
    subprocess.run([sys.executable, str(REPO / 'tools' / 'papyrus' / 'compile.py'), '--game', str(game),
                    TERM_SCRIPT, MIGRATE_SCRIPT], check=True)
    for name in (TERM_SCRIPT, MIGRATE_SCRIPT):   # loose copies for testing (the release packs them into the archive)
        (data / 'Scripts' / f'{name}.pex').write_bytes((REPO / 'data' / 'SCRIPTS' / f'{name}.pex').read_bytes())

    item_list = ','.join('@' + v[0] for v in ITEMS.values())
    s = [f'file | {MAIN}', f'new | KYWD | {CATEGORY[0]}', f'set | {CATEGORY[0]} | FULL | {CATEGORY[1]}']
    for key, (edid, name, _) in ITEMS.items():
        s += [f'copy | {TEMPLATE_MISC} | {edid}', f'set | {edid} | FULL | {name}', f'remove | {edid} | KWDA',
              f'set | {edid} | Model\\MODL | {MODEL}', f'remove | {edid} | Model\\MODT',
              f'remove | {edid} | KSIZ', f'set | {edid} | DATA\\Weight | 0', f'set | {edid} | DATA\\Value | 0',
              f'new | COBJ | co_{edid}']
        if key in EXCLUSIVE:
            s.append(f'new | COBJ | co_{edid}_Switch')
    s += [f'copy | @A1ALMTERM_Holotape_Config_Free_RM | {RATE_TERM}',
          f'set | {RATE_TERM} | FULL | (CLM) Terminal - Loot drop rate',
          f'set | {RATE_TERM} | NAM0 | CLM Terminal - Loot drop rate', f'set | {RATE_TERM} | WNAM | {rate_welcome()}']
    for term, menu, page in ((CONFIG_TERM, CONFIG_MENU, 0), (RATE_TERM, RATE_MENU, 1)):
        s += [f'remove | {term} | VMAD', f'menuclear | {term}']
        s += [f'menu | {term} | {item} | {text} | - | -' for item, text, _, _ in menu]
        s += [f'script | {term} | {TERM_SCRIPT}',
              f'prop | {term} | {TERM_SCRIPT} | Settings | Array of Object | {item_list}',
              f'prop | {term} | {TERM_SCRIPT} | Page | Int32 | {page}']
    s += [f'set | {CONFIG_TERM} | WNAM | {CONFIG_WELCOME}',
          f'menu | {CONFIG_TERM} | 12 | Loot version - Drop rate | @{RATE_TERM} | -',
          f'new | QUST | {MIGRATE_QUEST}', f'set | {MIGRATE_QUEST} | FULL | CLM Settings Migration',
          f'set | {MIGRATE_QUEST} | DNAM\\Flags | 1', f'script | {MIGRATE_QUEST} | {MIGRATE_SCRIPT}',
          f'prop | {MIGRATE_QUEST} | {MIGRATE_SCRIPT} | Settings | Array of Object | {item_list}']
    for g in ('A1ALMAFREE', 'A1ALMABALANCED', 'A1ALMAVAR', 'A1ALMAPERK', 'A1ALMASPAWN'):
        s.append(f'prop | {MIGRATE_QUEST} | {MIGRATE_SCRIPT} | {g} | Object | @{g}')
    build(ack, s)

    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord
    p = Plugin.load(data / MAIN)
    fo = Plugin.load(game / 'Data' / 'Fallout4.esm')
    chem = fo.by_edid('WorkbenchChemlab').formid
    fid = lambda e: p.by_edid(e).formid
    kw = p.by_edid(CATEGORY[0])
    kw.subrecords[:] = [kw.subrecords[0], Subrecord('CNAM', bytes.fromhex('ffffff00')),
                        Subrecord('TNAM', struct.pack('<I', 9)), kw.get('FULL')]
    kw.mark_dirty()
    for key, (edid, name, text) in ITEMS.items():
        item = fid(edid)
        variants = [('', None)] + ([('_Switch', EXCLUSIVE[key])] if key in EXCLUSIVE else [])
        for suffix, other in variants:
            r = p.by_edid(f'co_{edid}{suffix}')
            conds = [Subrecord('CTDA', ctda(OP_EQ, 0.0, FN_GET_ITEM_COUNT, item))]      # not already carried
            comps = []
            if other:   # switching: shown while carrying the other one, which the recipe takes back
                o = fid(ITEMS[other][0])
                conds.append(Subrecord('CTDA', ctda(OP_GE, 1.0, FN_GET_ITEM_COUNT, o)))
                comps = [Subrecord('FVPA', struct.pack('<II', o, 1))]
            elif key in EXCLUSIVE:
                conds.append(Subrecord('CTDA', ctda(OP_EQ, 0.0, FN_GET_ITEM_COUNT, fid(ITEMS[EXCLUSIVE[key]][0]))))
            if key in NEEDS:
                conds.append(Subrecord('CTDA', ctda(OP_GE, 1.0, FN_GET_ITEM_COUNT, fid(ITEMS[NEEDS[key]][0]))))
            r.subrecords[:] = [r.subrecords[0], *comps, Subrecord('DESC', text.encode('cp1252') + b'\0'), *conds,
                               Subrecord('CNAM', struct.pack('<I', item)), Subrecord('BNAM', struct.pack('<I', chem)),
                               Subrecord('FNAM', struct.pack('<I', kw.formid)), Subrecord('INTV', struct.pack('<HH', 1, 0))]
            r.mark_dirty()
    for g in p.records('GLOB'):           # old settings: -1 = never configured (new games convert nothing)
        if g.edid in OLD:
            g.set('FLTV', struct.pack('<f', -1.0))
    p.save(data / MAIN)
    print('setting items, chem station recipes, holotape menus and migration quest built')


def cmd_conditions(ack: Path, game: Path) -> None:
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord
    data = game / 'Data'
    main = Plugin.load(data / MAIN)
    old = {main.by_edid(g).formid & 0xFFFFFF: g for g in OLD}
    for name in [MAIN] + ADDONS:
        p = main if name == MAIN else Plugin.load(data / name)
        idx = len(p.masters) if p is main else p.masters.index(MAIN)
        item = lambda key: (idx << 24) | (main.by_edid(ITEMS[key][0]).formid & 0xFFFFFF)
        changed = 0
        for c in p.records('COBJ'):
            if not p.is_own(c.formid):
                continue
            subs = c.subrecords
            conds = [s for s in subs if s.sig == 'CTDA']
            settings, keep = {}, []
            for s in conds:
                fn, value, p1 = struct.unpack_from('<H', s.data, 8)[0], struct.unpack_from('<f', s.data, 4)[0], \
                    struct.unpack_from('<I', s.data, 12)[0]
                if fn == FN_GET_GLOBAL_VALUE and (p1 >> 24) == idx and (p1 & 0xFFFFFF) in old:
                    settings[old[p1 & 0xFFFFFF]] = value
                else:
                    keep.append(s)
            if 'A1ALMAFREE' not in settings or settings['A1ALMAFREE'] == 4:
                continue        # not a costly/FREE recipe (loot recipes: tools/loot/generate.py)
            new = []
            if settings['A1ALMAFREE'] == 1:
                new += [ctda(OP_GE, 1, FN_GET_ITEM_COUNT, item('free')), ctda(OP_EQ, 0, FN_GET_ITEM_COUNT, item('loot'))]
            else:
                new += [ctda(OP_EQ, 0, FN_GET_ITEM_COUNT, item('free')), ctda(OP_EQ, 0, FN_GET_ITEM_COUNT, item('loot'))]
            if settings.get('A1ALMABALANCED') == 1:
                new.append(ctda(OP_GE, 1, FN_GET_ITEM_COUNT, item('op')))
            if settings.get('A1ALMAVAR') == 1:
                new.append(ctda(OP_GE, 1, FN_GET_ITEM_COUNT, item('variants')))
            if settings.get('A1ALMAPERK') == 1:
                new.append(ctda(OP_EQ, 0, FN_GET_ITEM_COUNT, item('noperk')))
            if settings.get('A1ALMASPAWN') == 1:
                new.append(ctda(OP_EQ, 0, FN_GET_ITEM_COUNT, item('nospawn')))
            at = next(i for i, s in enumerate(subs) if s.sig == 'CTDA')
            rest = [s for s in subs if s.sig != 'CTDA']
            at = sum(1 for s in subs[:at] if s.sig != 'CTDA')
            c.subrecords[:] = rest[:at] + [Subrecord('CTDA', d) for d in new] + keep + rest[at:]
            c.mark_dirty()
            changed += 1
        if p is main:   # holotape menu items: shown only when they would change something
            for term, menu in ((CONFIG_TERM, CONFIG_MENU), (RATE_TERM, RATE_MENU)):
                t = p.by_edid(term)
                subs = t.subrecords
                starts = [i for i, s in enumerate(subs) if s.sig == 'ITXT']
                end = starts[-1]          # the last item ends at the first subrecord that is not part of an item
                while end < len(subs) and subs[end].sig in ITEM_SIGS:
                    end += 1
                starts.append(end)
                for k in range(len(starts) - 1, 0, -1):
                    a, b = starts[k - 1], starts[k]
                    ids = [struct.unpack('<H', s.data)[0] for s in subs[a:b] if s.sig == 'ITID']
                    spec = next((m for m in menu if ids and m[0] == ids[0]), None)
                    shown = spec[3] if spec else SUBMENU_SHOWN.get((term, ids[0] if ids else None))
                    if not shown:
                        continue
                    conds = [Subrecord('CTDA', ctda((OP_GE if carried else OP_EQ) | (FLAG_OR if j < len(shown) - 1 else 0),
                                                    1.0 if carried else 0.0, FN_GET_ITEM_COUNT,
                                                    item(key), RUN_REFERENCE, PLAYER_REF))
                             for j, (key, carried) in enumerate(shown)]
                    body = [s for s in subs[a:b] if s.sig not in ('CTDA', 'CIS1', 'CIS2')]
                    assert body[0].sig == 'ITXT' and all(s.sig in ITEM_SIGS for s in body), [s.sig for s in body]
                    subs[a:b] = body + conds
                t.mark_dirty()
        p.save(data / name)
        print(f'{name}: {changed} recipes now check setting items')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    ap.add_argument('step', choices=['items', 'conditions'])
    a = ap.parse_args()
    {'items': cmd_items, 'conditions': cmd_conditions}[a.step](Path(a.ack), Path(a.game))


if __name__ == '__main__':
    main()
