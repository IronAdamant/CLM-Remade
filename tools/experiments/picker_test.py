"""Throwaway experiment: can the chemistry station be CLM's "Legendary Picker" tree? (2026-10-11)

    python tools/experiments/picker_test.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Builds CLM - Picker Test.esp (ESL; masters Fallout4.esm and the main plugin) straight into the game's Data folder.
It changes nothing in CLM. Not part of the mod; delete the plugin after testing.

Chem station recipes get their categories from "Recipe Filter" keywords (KYWD type 9) in the recipe's FNAM; vanilla
always uses one. This tests whether two keywords nest (Category > Subcategory) and which one is the parent:
    Energized (Green Laser), Hurtin' (500%)   FNAM [CLM Weapons]                one level
    Chilling                                  FNAM [CLM Weapons, Elemental]     two keywords
    Burning                                   FNAM [Elemental, CLM Weapons]     two keywords, reversed
    Lobbin' (Frag Mine)                       FNAM [CLM Launchers]              a second top-level category
Each chem recipe (free) makes a weightless "CLM Selector" item; carrying it shows a free recipe for that legendary
at the weapons workbench (condition GetItemCount(selector) >= 1).
"""
from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST = 'CLM - Picker Test.esp'
MAIN = 'Custom Legendary Modifications Remade.esp'
CATEGORIES = {'A1ALMPT_KW_Weapons': 'CLM Weapons', 'A1ALMPT_KW_Elemental': 'Elemental',
              'A1ALMPT_KW_Launchers': 'CLM Launchers'}
PICKS = [  # (short name, legendary editor ID, display name, category keywords in FNAM order)
    ('EnergizedGreen', 'A1ALMOMOD_Legendary_Weapon_Energized_Laser_Green', 'Energized (Green Laser)',
     ['A1ALMPT_KW_Weapons']),
    ('Hurtin500', 'A1ALMOMOD_Legendary_Weapon_DamageBoost_5x', "Hurtin' (500%)", ['A1ALMPT_KW_Weapons']),
    ('Chilling', 'A1ALMOMOD_Legendary_Weapon_Chilling', 'Chilling', ['A1ALMPT_KW_Weapons', 'A1ALMPT_KW_Elemental']),
    ('Burning', 'A1ALMOMOD_Legendary_Weapon_Burning', 'Burning', ['A1ALMPT_KW_Elemental', 'A1ALMPT_KW_Weapons']),
    ('LobbinFragMine', 'A1ALMOMOD_Legendary_Weapon_Lobbing_Variant_Mine_Frag', "Lobbin' (Frag Mine)",
     ['A1ALMPT_KW_Launchers']),
]
FN_GET_ITEM_COUNT, OP_GE = 47, 3 << 5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'

    # 1. records (AgentCreationKit builder): keywords, selector items, empty recipes
    s = [f'file | {TEST}', 'master | Fallout4.esm', f'master | {MAIN}']
    for kw, name in CATEGORIES.items():
        s += [f'new | KYWD | {kw}', f'set | {kw} | FULL | {name}']
    for short, _, name, _ in PICKS:
        sel = f'A1ALMPT_Selector_{short}'
        s += [f'copy | @miscmod_mod_RailwayRifle_Scope_ScopeShort_Recon | {sel}', f'set | {sel} | FULL | CLM Selector: {name}',
              f'remove | {sel} | KWDA', f'remove | {sel} | KSIZ', f'set | {sel} | DATA\\Weight | 0',
              f'set | {sel} | DATA\\Value | 0', f'new | COBJ | A1ALMPT_co_Chem_{short}', f'new | COBJ | A1ALMPT_co_Bench_{short}']
    spec = HERE / 'picker_test.spec'
    spec.write_text('\n'.join(s) + '\n', encoding='utf8')
    cmd = [sys.executable, '-m', 'ack', 'xedit', 'run', 'build', MAIN, '--save', '--timeout', '300',
           '--param', f'SPEC={spec}']
    if (data / TEST).exists():
        cmd += ['--also-load', TEST]
    r = subprocess.run(cmd, cwd=ack, capture_output=True, text=True)
    run = sorted((ack / 'private' / 'runs').glob('*-build'))[-1]
    first = (run / 'result.txt').read_text(encoding='utf8').splitlines()[0]
    print(first)
    if ' 0 errors' not in first:
        raise SystemExit((run / 'result.txt').read_text(encoding='utf8'))

    # 2. raw: keyword type, recipe contents
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord
    fo = Plugin.load(data / 'Fallout4.esm')
    main_p = Plugin.load(data / MAIN)
    p = Plugin.load(data / TEST)
    own = lambda e: p.by_edid(e).formid
    from_main = lambda e: (p.masters.index(MAIN) << 24) | (main_p.by_edid(e).formid & 0xFFFFFF)
    chem = fo.by_edid('WorkbenchChemlab').formid                           # Fallout4.esm is master 0
    for kw in CATEGORIES:
        r = p.by_edid(kw)
        r.subrecords[:] = [r.subrecords[0], Subrecord('CNAM', bytes.fromhex('ffffff00')),
                           Subrecord('TNAM', struct.pack('<I', 9)), r.get('FULL')]   # 9 = Recipe Filter
        r.mark_dirty()
    for short, omod, name, cats in PICKS:
        sel = own(f'A1ALMPT_Selector_{short}')
        r = p.by_edid(f'A1ALMPT_co_Chem_{short}')
        r.subrecords[:] = [r.subrecords[0], Subrecord('DESC', b'\0'), Subrecord('CNAM', struct.pack('<I', sel)),
                           Subrecord('BNAM', struct.pack('<I', chem)),
                           Subrecord('FNAM', b''.join(struct.pack('<I', own(k)) for k in cats)),
                           Subrecord('INTV', struct.pack('<HH', 1, 0))]
        r.mark_dirty()
        r = p.by_edid(f'A1ALMPT_co_Bench_{short}')
        cond = struct.pack('<B3sfH2sIIIIi', OP_GE, b'\0\0\0', 1.0, FN_GET_ITEM_COUNT, b'\0\0', sel, 0, 0, 0, -1)
        r.subrecords[:] = [r.subrecords[0], Subrecord('DESC', b'\0'), Subrecord('CTDA', cond),
                           Subrecord('CNAM', struct.pack('<I', from_main(omod))), Subrecord('INTV', struct.pack('<HH', 1, 0))]
        r.mark_dirty()
    p.save(data / TEST)
    print(f'{TEST}: {len(CATEGORIES)} categories, {len(PICKS)} selectors with chem and workbench recipes')


if __name__ == '__main__':
    main()
