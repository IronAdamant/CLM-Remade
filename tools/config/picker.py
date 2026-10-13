"""CLM 2.0 Legendary Picker: choose at the chemistry station which families of legendaries the workbench shows.

    python tools/config/picker.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Run after tools/config/settings.py (items, conditions) and tools/loot/generate.py. Safe to re-run.

Off by default. With the "Picker mode" setting item carried (tools/config/settings.py), every costly and free CLM
recipe whose legendary belongs to a family (tools/loot/loot_plan.csv) also needs that family's selector: a weightless
"CLM Pick" item, crafted for free at the chemistry station under one of the "CLM Armour / Spawns / Weapon" categories
below. Drop a selector to hide its family again. Settings still apply on top (Show OP, Show variants...), and loot
mode ignores the picker. Recipes outside the families (Not A Legendary, test items) always show.

Selectors of families that are entirely OP are also listed under "CLM OP" (a recipe with two category keywords shows
in both) and need Show OP; families that are entirely spawning or perk-style follow those settings too. No scripts:
works on PlayStation.

Each workbench recipe gets, in front of its own conditions (each pick and Picker mode is also a global, set by the
optional F4SE menu instead of carrying items; see tools/config/settings.py):
    GetItemCount(Picker mode) == 0  OR  GetItemCount(family selector) >= 1  OR  GetGlobalValue(family pick) == 1
    GetGlobalValue(Picker mode) == 0  OR  GetItemCount(family selector) >= 1  OR  GetGlobalValue(family pick) == 1
"""
from __future__ import annotations

import argparse
import struct
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / 'tools' / 'loot'))
sys.path.insert(0, str(HERE))
import generate  # noqa: E402
from settings import (ITEMS, ctda, FN_GET_ITEM_COUNT, FN_GET_GLOBAL_VALUE, OP_EQ, OP_GE, FLAG_OR,  # noqa: E402
                      MCM_GLOBAL, setting_global, on_conds, off_conds)

MAIN = generate.MAIN
PLUGINS = [MAIN]   # the DLC add-ons were merged into it (2026-10-12)
TEMPLATE_MISC = '@miscmod_mod_RailwayRifle_Scope_ScopeShort_Recon'
MODEL = 'Props\\Holotape_Prop.nif'
OP_CATEGORY = 'OP'

# category -> families (names as in tools/loot/loot_plan.csv); armour families and weapon families are separate
CATEGORIES = {
    ('armor', 'Armour: Defence'): ['Plating', 'Juggernaut', 'Shields', 'Immunities', 'Bouncing and Jedi',
                                   'Forbidden (armour)'],
    ('armor', 'Armour: Retaliation'): ['Untouchable', 'Punching', "Shavka's Explosive Striking", 'Flaming', "Radiatin'",
                                       'Brawlers', 'Impact Landing'],
    ('armor', 'Armour: Movement'): ["Jumpy and Flyin'", 'Speedy', 'Nimble', 'Combined Speed and Jump'],
    ('armor', 'Armour: Stealth and Sight'): ['Ghostly and Camouflaged', 'Sight', 'Steady aim'],
    ('armor', 'Armour: Combat'): ["Fisto's", "Lucky Hittin'", 'Murderous', 'Factional Damaging', "One Punch Man's",
                                  'Grit', "Cap Showerin'"],
    ('armor', 'Armour: Survival'): ['Healing', 'Carrying', 'Enlightenment', 'Handiwork', 'Power armour', 'Refilling',
                                    'Surroundings'],
    ('weapon', 'Weapon: Damage'): ["Hurtin'", 'Heavy hitters', "Destroyer's", 'Savage', 'Forcible', 'Fury',
                                   "Slayer's", 'Backstabbing', "Limb Breaker's", 'Relentless', 'Forbidden (weapon)',
                                   'RoomClearing'],
    ('weapon', 'Weapon: Elemental'): ['Elemental', 'Fire', 'Cold', 'Shock', 'Poison and acid', 'Bleeding', 'Energy',
                                      'Alien tech'],
    ('weapon', 'Weapon: Explosive Rounds'): ['BioReactive Explosive', 'Havoc', 'Rebounding', 'Spikes', "Garm's",
                                             "Ultima Hecate's", "Liberty Prime's"],
    ('weapon', 'Weapon: Launchers'): ["Lobbin'", "Mine launchin'", "Rocketin'", "Rainman's", "Splinterin'",
                                      "Seekin'", 'Ordnance', "Hydra's Fang", 'Nuka-Infused'],
    ('weapon', 'Weapon: Fun Launchers'): ['Paintball', 'Pyrotechnical', "Trappin'", 'Weather Altering',
                                          "Moby-Dick's"],
    ('weapon', 'Weapon: Lasers and Conversions'): ['Energized', "Disintegratin'", 'Gauss conversions', 'Strikers',
                                                   'Scattering', 'Curios'],
    ('weapon', 'Weapon: Handling'): ['Performance tuning', 'Quicker', 'Automatic', 'Recoilless', 'Marksman',
                                     'Gunslingers', "Operator's", 'Multi-shot', "Shotgun Surgeon's"],
    ('weapon', 'Weapon: Ammo and Time'): ["Keltas' Factorium", 'Synthesised Factorium', "Concentratin'", 'Vampiric',
                                          'Utility'],
    ('weapon', 'Weapon: Melee'): ["Shavka's Explosive Striking", "Thumpin'", 'Brawn', 'Majestically Swaggering',
                                  'Pushing'],
    ('weapon', 'Spawns: Creatures'): ['Spawn: Aliens', 'Spawn: Far Harbor creatures', 'Spawn: Ghouls',
                                      'Spawn: Insects', 'Spawn: Mirelurks', 'Spawn: Nuka-World creatures',
                                      'Spawn: Super mutants', 'Spawn: Wasteland beasts'],
    ('weapon', 'Spawns: People and Robots'): ['Spawn: Automatron robots', 'Spawn: Brotherhood of Steel',
                                              'Spawn: Friendly robots', 'Spawn: Institute', 'Spawn: Nuka-World gangs',
                                              'Spawn: Raiders and gangs', 'Spawn: Railroad', 'Spawn: Robots',
                                              'Spawn: Minutemen', 'Spawn: Children of Atom'],
}


def keyword(category: str) -> str:
    return 'A1ALMKW_RecipeFilter_' + generate.slug(category)


def selector(kind: str, family: str) -> str:
    return f'A1ALMPICK_{kind.capitalize()}_{generate.slug(family)}'


def pick_global(kind: str, family: str) -> str:
    """The pick as a global (main plugin, every family): set by the F4SE menu"""
    return f'A1ALMPICKG_{kind.capitalize()}_{generate.slug(family)}'


def load_families() -> dict:
    """(kind, family) -> {'home': plugin, 'rows': [...], 'category': name}"""
    fams = defaultdict(lambda: {'rows': []})
    for r in generate.load_plan():
        f = fams[(r['kind'], r['family'])]
        f['rows'].append(r)
        f['home'] = r['holotape_plugin']
    placed = {}
    for (kind, cat), names in CATEGORIES.items():
        for n in names:
            assert (kind, n) in fams, (kind, n)
            assert (kind, n) not in placed, (kind, n)
            placed[(kind, n)] = cat
    missing = set(fams) - set(placed)
    assert not missing, f'families without a category: {sorted(missing)}'
    for key, f in fams.items():
        f['category'] = placed[key]
        for r in f['rows']:       # a selector must be visible from every plugin holding one of its legendaries
            assert r['plugin'] == f['home'] or f['home'] == MAIN, (key, r['plugin'], f['home'])
    return dict(fams)


def write_spec(fams: dict) -> Path:
    s = ['# Generated by tools/config/picker.py - do not edit', f'file | {MAIN}']
    for cat in sorted({c for _, c in CATEGORIES} | {OP_CATEGORY}):
        s += [f'new | KYWD | {keyword(cat)}', f'set | {keyword(cat)} | FULL | CLM {cat}']
    for plugin in PLUGINS:
        mine = sorted(k for k, f in fams.items() if f['home'] == plugin)
        if not mine:
            continue
        if plugin != MAIN:
            s.append(f'file | {plugin}')
        for kind, family in mine:
            e = selector(kind, family)
            name = family.removeprefix('Spawn: ') if family.startswith('Spawn: ') else family
            label = 'Spawning' if family.startswith('Spawn: ') else 'Weapon' if kind == 'weapon' else 'Armour'
            s += [f'copy | {TEMPLATE_MISC} | {e}', f'set | {e} | FULL | CLM Pick: {name} ({label})',
                  f'set | {e} | Model\\MODL | {MODEL}', f'remove | {e} | Model\\MODT',
                  f'remove | {e} | KWDA', f'remove | {e} | KSIZ',
                  f'set | {e} | DATA\\Weight | 0', f'set | {e} | DATA\\Value | 0', f'new | COBJ | co_{e}']
        s.append('prunerecords | A1ALMPICK_')
        s.append('prunerecords | co_A1ALMPICK_')
    path = HERE / 'picker.spec'
    path.write_text('\n'.join(s) + '\n', encoding='utf8')
    return path


def write_raw(fams: dict, data: Path, ack: Path) -> None:
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord
    main = Plugin.load(data / MAIN)
    plugins = {n: (main if n == MAIN else Plugin.load(data / n)) for n in PLUGINS if (data / n).exists()}
    chem = Plugin.load(data / 'Fallout4.esm').by_edid('WorkbenchChemlab').formid

    def ref(in_plugin: str, edid: str, home: str = MAIN) -> int:
        p, h = plugins[in_plugin], plugins[home]
        r = h.by_edid(edid)
        assert r is not None, edid
        if in_plugin == home:
            return r.formid
        return (p.masters.index(home) << 24) | (r.formid & 0xFFFFFF)

    for cat in sorted({c for _, c in CATEGORIES} | {OP_CATEGORY}):
        kw = main.by_edid(keyword(cat))
        kw.subrecords[:] = [kw.subrecords[0], Subrecord('CNAM', bytes.fromhex('ffffff00')),
                            Subrecord('TNAM', struct.pack('<I', 9)), kw.get('FULL')]   # 9 = Recipe Filter
        kw.mark_dirty()

    # what each family's recipes already require: selectors of all-OP / all-spawn / all-perk families follow suit
    item_key = {}                                  # setting item form ID (as seen from a plugin) -> settings key
    for name, p in plugins.items():
        for key, (edid, _, _) in ITEMS.items():
            item_key[(name, ref(name, edid))] = key
    omod_family = {r['edid']: key for key, f in fams.items() for r in f['rows']}
    selectors = {(name, ref(name, selector(*k), f['home'])) for k, f in fams.items() for name in plugins
                 if f['home'] in (name, MAIN)}
    picker = {name: ref(name, ITEMS['picker'][0]) for name in plugins}
    picker_g = {name: ref(name, setting_global('picker')) for name in plugins}
    pick_gs = {(name, ref(name, pick_global(*k))) for k in fams for name in plugins}
    needs = defaultdict(lambda: defaultdict(int))  # family -> settings key -> recipes requiring it
    total = defaultdict(int)
    changed = 0
    for name, p in plugins.items():
        omods = {r.formid: r.edid for r in p.records('OMOD') if p.is_own(r.formid)}
        for c in p.records('COBJ'):
            if not p.is_own(c.formid) or c.edid.endswith('_Unlocked') or c.edid.startswith(('co_A1ALMSET', 'co_A1ALMPICK')):
                continue
            cn = c.get('CNAM')
            fam = omod_family.get(omods.get(struct.unpack('<I', cn.data)[0])) if cn else None
            if fam is None:
                continue
            subs = c.subrecords
            conds = [s for s in subs if s.sig == 'CTDA']
            # drop earlier picker conditions (re-runs)
            def mine(s):
                fn, p1 = struct.unpack_from('<H', s.data, 8)[0], struct.unpack_from('<I', s.data, 12)[0]
                return fn == FN_GET_ITEM_COUNT and (p1 == picker[name] or (name, p1) in selectors) or                     fn == FN_GET_GLOBAL_VALUE and (p1 == picker_g[name] or (name, p1) in pick_gs)
            keep = [s for s in conds if not mine(s)]
            total[fam] += 1
            for s in keep:
                k = item_key.get((name, struct.unpack_from('<I', s.data, 12)[0]))
                if k and struct.unpack_from('<H', s.data, 8)[0] == FN_GET_ITEM_COUNT:
                    needs[fam][(k, s.data[0] >> 5)] += 1
            sel = ref(name, selector(*fam), fams[fam]['home'])
            sel_g = ref(name, pick_global(*fam))
            picked = [ctda(OP_GE | FLAG_OR, 1.0, FN_GET_ITEM_COUNT, sel), ctda(OP_EQ, 1.0, FN_GET_GLOBAL_VALUE, sel_g)]
            new = [Subrecord('CTDA', d) for d in
                   [ctda(OP_EQ | FLAG_OR, 0.0, FN_GET_ITEM_COUNT, picker[name])] + picked +
                   [ctda(OP_EQ | FLAG_OR, 0.0, FN_GET_GLOBAL_VALUE, picker_g[name])] + picked]
            first = next(i for i, s in enumerate(subs) if s.sig == 'CTDA')
            rest = [s for s in subs if s.sig != 'CTDA']
            at = sum(1 for s in subs[:first] if s.sig != 'CTDA')
            c.subrecords[:] = rest[:at] + new + keep + rest[at:]
            c.mark_dirty()
            changed += 1

    # selector recipes at the chemistry station
    for (kind, family), f in fams.items():
        home = f['home']
        p = plugins[home]
        item = ref(home, selector(kind, family), home)
        r = p.by_edid(f'co_{selector(kind, family)}')
        def setting(key: str, on: bool) -> list[bytes]:
            return (on_conds if on else off_conds)(ref(home, ITEMS[key][0]), ref(home, setting_global(key)))
        conds = [*setting('picker', True), ctda(OP_EQ, 0.0, FN_GET_ITEM_COUNT, item), *setting('loot', False),
                 ctda(OP_EQ, 0.0, FN_GET_GLOBAL_VALUE, ref(home, MCM_GLOBAL))]
        n = total[(kind, family)]
        all_op = n and needs[(kind, family)][('op', 3)] == n
        for key, op in (('op', OP_GE), ('noperk', OP_EQ), ('nospawn', OP_EQ)):
            if n and needs[(kind, family)][(key, op >> 5)] == n:
                conds += setting(key, op == OP_GE)
        cats = [keyword(f['category'])] + ([keyword(OP_CATEGORY)] if all_op else [])
        text = (f'Show the {family.removeprefix("Spawn: ")} {"spawning " if family.startswith("Spawn: ") else ""}'
                f'legendaries ({len(f["rows"])}) at the {"weapons" if kind == "weapon" else "armour"} workbench '
                'while Picker mode is on. Drop this to hide them again.')
        r.subrecords[:] = [r.subrecords[0], Subrecord('DESC', text.encode('cp1252') + b'\0'),
                           *[Subrecord('CTDA', d) for d in conds],
                           Subrecord('CNAM', struct.pack('<I', item)),
                           Subrecord('BNAM', struct.pack('<I', chem if home == MAIN else
                                                         (p.masters.index('Fallout4.esm') << 24) | chem)),
                           Subrecord('FNAM', b''.join(struct.pack('<I', ref(home, k)) for k in cats)),
                           Subrecord('INTV', struct.pack('<HH', 1, 0))]
        r.mark_dirty()
    for name, p in plugins.items():
        p.save(data / name)
    op_only = sum(1 for k in fams if total[k] and needs[k][('op', 3)] == total[k])
    print(f'{len(fams)} selectors ({op_only} also under CLM OP), {changed} workbench recipes follow the picker')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    ap.add_argument('--raw-only', action='store_true')
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    sys.path.insert(0, str(ack))
    fams = load_families()
    if not a.raw_only:
        generate.run_build(write_spec(fams), data, ack)
    write_raw(fams, data, ack)


if __name__ == '__main__':
    main()
