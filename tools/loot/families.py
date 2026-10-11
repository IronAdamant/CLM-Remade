"""Group CLM's legendaries into families (one unlock holotape each) and collect what's needed to tier them.

    python tools/loot/families.py --ack "D:/Coding Projects/AgentCreationKit" --data "D:/Steam/steamapps/common/Fallout 4/Data"

Writes tools/loot/legendaries.csv: one row per legendary with its plugin, editor ID, name, family (from the editor
ID), kind (weapon/armor), OP flag (its costly recipe requires the Show OP setting item A1ALMSET_ShowOP; before
settings became items, 2026-10-12, A1ALMABALANCED == 1), and its recipe's total component
count (a rough cost signal; the author priced recipes by power). Prints the families with their members.
"""
from __future__ import annotations

import argparse
import csv
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGINS = ['Custom Legendary Modifications Remade.esp', 'CLM - Automatron.esp', 'CLM - Far Harbor.esp',
           'CLM - Nuka-World.esp', 'CLM - Contraptions.esp']
FN_GET_ITEM_COUNT = 47
SKIP = {'A1ALMOMOD_Legendary_Weapon_NotALegendary', 'A1ALMOMOD_Legendary_Armor_NotALegendary'}


# Spawn legendaries: one family per creature class, so a holotape unlocks a sensible group (not 91 at once, not
# one per creature). Keys are creature names as they appear in the editor IDs, legendary/random/boss suffixes removed.
SPAWN_CLASS = {
    'Spawning_BoS': 'Brotherhood of Steel', 'Spawning_Institute': 'Institute', 'Spawning_RailRoad': 'Railroad',
    'Spawning_Neutral': 'Friendly robots', 'Spawning_NukaGang': 'Nuka-World gangs',
    'Automatron': 'Automatron robots',
    'Assaultron': 'Robots', 'MrGutsy': 'Robots', 'SentryBot': 'Robots', 'RandomRobot': 'Robots',
    'Bloatfly': 'Insects', 'Bloodbug': 'Insects', 'RadAntLarge': 'Insects', 'RadAnt': 'Insects',
    'Radroach': 'Insects', 'RadRoach': 'Insects', 'RadRoachGlowing': 'Insects', 'Stingwing': 'Insects', 'Swarm': 'Insects',
    'Mirelurk': 'Mirelurks', 'MirelurkCrab': 'Mirelurks', 'MirelurkHunter': 'Mirelurks',
    'MirelurkKing': 'Mirelurks', 'MirelurkQueen': 'Mirelurks',
    'Deathclaw': 'Wasteland beasts', 'YaoGuai': 'Wasteland beasts', 'RadStag': 'Wasteland beasts',
    'MoleRat': 'Wasteland beasts', 'RadRatLarge': 'Wasteland beasts', 'RadRat': 'Wasteland beasts',
    'RadScorpion': 'Wasteland beasts', 'ViciousDog': 'Wasteland beasts',
    'FeralGhoul': 'Ghouls', 'GlowingOne': 'Ghouls',
    'Stupermutant': 'Super mutants', 'StupermutantHound': 'Super mutants', 'StupermutantBehemoth': 'Super mutants',
    'StupermutantSuicider': 'Super mutants',
    'Raider': 'Raiders and gangs', 'Gunner': 'Raiders and gangs', 'TriggerMan': 'Raiders and gangs',
    'ForgedRaider': 'Raiders and gangs', 'UniqueNPC': 'Raiders and gangs',
    'Alien': 'Aliens',
    'Angler': 'Far Harbor creatures', 'FogCrawler': 'Far Harbor creatures', 'Gulper': 'Far Harbor creatures',
    'HermitCrab': 'Far Harbor creatures', 'Trapper': 'Far Harbor creatures',
    'GatorClaw': 'Nuka-World creatures', 'Ghoulrilla': 'Nuka-World creatures', 'NukaLurk': 'Nuka-World creatures',
    'RandomRustDevil': 'Automatron robots',
}


def family_of(edid: str) -> tuple[str, str]:
    """(kind, family) from an editor ID like A1ALMOMOD_Legendary_Armor_PerkV_Fortify_Jumpy_100."""
    m = re.match(r'A1ALMOMOD_Legendary_(Weapon|Armor|Armour)_(.*)$', edid)
    if not m:
        return 'other', edid
    kind, rest = m.group(1).lower().replace('armour', 'armor'), m.group(2)
    parts = rest.split('_')
    while len(parts) > 1 and parts[0] in ('Custom', 'PerkV', 'Fortify', 'Effect'):
        parts = parts[1:]
    if parts[0] == 'Spawning':
        group = f'Spawning_{parts[1]}'
        if group in SPAWN_CLASS:
            return kind, 'Spawn: ' + SPAWN_CLASS[group]
        creature = parts[2]
        if creature != 'Automatron':
            creature = re.sub(r'(Legendary|Random|Boss)$', '', creature)
        if creature not in SPAWN_CLASS:
            raise SystemExit(f'no spawn class for {creature} ({edid})')
        return kind, 'Spawn: ' + SPAWN_CLASS[creature]
    # Variant suffixes ("Base"/"Variant" parts, numbers, percentages) and sub-names belong to the first token.
    return kind, parts[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--data', required=True)
    a = ap.parse_args()
    sys.path.insert(0, a.ack)
    from ack.plugin import Plugin

    rows = []
    for name in PLUGINS:
        p = Plugin.load(Path(a.data) / name)
        own = {r.formid: r for r in p.records() if p.is_own(r.formid)}
        show_op = next((r.formid for r in own.values() if r.edid == 'A1ALMSET_ShowOP'), None)
        if show_op is None:  # add-ons use the main plugin's setting item
            main = Plugin.load(Path(a.data) / PLUGINS[0])
            show_op = (main.by_edid('A1ALMSET_ShowOP').formid & 0xFFFFFF) | (p.masters.index(PLUGINS[0]) << 24)
        recipes = defaultdict(list)
        for r in own.values():
            if r.sig == 'COBJ' and r.get('CNAM'):
                recipes[struct.unpack('<I', r.get('CNAM').data)[0]].append(r)
        for r in own.values():
            if r.sig != 'OMOD' or not r.get('FULL') or r.edid in SKIP:
                continue
            kind, fam = family_of(r.edid)
            op, cost = False, 0
            for c in recipes.get(r.formid, []):
                if c.edid.endswith('FREE') or c.edid.endswith('_Unlocked'):
                    continue
                for s in c.subrecords:
                    if s.sig == 'CTDA' and struct.unpack_from('<H', s.data, 8)[0] == FN_GET_ITEM_COUNT \
                            and struct.unpack_from('<I', s.data, 12)[0] == show_op:
                        op = True
                fv = c.get('FVPA')
                if fv:
                    cost = sum(struct.unpack_from('<I', fv.data, i + 4)[0] for i in range(0, len(fv.data), 8))
            desc = r.get('DESC')
            rows.append({'plugin': name, 'edid': r.edid, 'name': r.get('FULL').zstring, 'kind': kind, 'family': fam,
                         'op': int(op), 'cost': cost,
                         'recipes': sum(1 for c in recipes.get(r.formid, []) if not c.edid.endswith('_Unlocked')),
                         'desc': desc.zstring if desc else ''})

    out = HERE / 'legendaries.csv'
    with out.open('w', newline='', encoding='utf8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda x: (x['kind'], x['family'], x['edid'])))
    fams = defaultdict(list)
    for x in rows:
        fams[(x['kind'], x['family'])].append(x)
    print(f'{len(rows)} legendaries in {len(fams)} families -> {out}')
    for (kind, fam), xs in sorted(fams.items()):
        print(f'{kind:6} {fam:45} {len(xs):3}  OP {sum(x["op"] for x in xs):2}  ' +
              '; '.join(x['name'].replace('CLM: ', '').replace('ZLM: ', '') for x in xs)[:150])


if __name__ == '__main__':
    main()
