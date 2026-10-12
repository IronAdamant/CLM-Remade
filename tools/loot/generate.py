"""Generate CLM's loot mode from tools/loot/loot_plan.csv (run plan.py first).

    python tools/loot/generate.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Builds into the main plugin in the game's Data folder, safe to re-run:
- per family: an unlock holotape (MISC, weightless). Carrying it shows the family's unlocked recipes.
- per legendary: a loose mod (MISC, linked from the legendary's LNAM like vanilla loose mods) and an unlocked recipe
  (copy of the costly recipe) with conditions
      loot mode on (Loot mode item carried, or its global set by the F4SE menu - tools/config/settings.py)
      GetItemCount(family holotape) >= 1   OR         unlocked...
      GetItemCount(loose mod) >= 1                    ...or the player found this legendary
  (the engine groups ORs before ANDs). OP recipes also take one catalyst (weapon or armour).
- two OP catalysts (weapon, armour).
- drop lists: per kind of drop (common, uncommon, rare, OP, holotape, catalyst) a pool, and per drop-rate setting
  (Low / Standard / Higher) a gate and a drop list with fixed chance-none values (Outer, Inner: 1% x 1% gives 0.01%
  steps). No globals or scripts: the rate is a setting item, so it works on PlayStation too.
- a hidden perk with six "Add Leveled List On Death" entries: per drop rate (checked with the rate setting
  items), normal targets get one roll and targets with EncTypeLegendary ten; only while the loot setting item is
  carried. Granted by a start-game quest running A1ALMLoot_GrantPerkScript.

Steps: write tools/loot/build_spec.txt and run AgentCreationKit's builder (creates/updates records), then write the
parts xEdit makes awkward directly with ack.plugin (conditions, leveled lists, globals, perk entries), then check
the plugin with FO4Edit.
"""
from __future__ import annotations

import argparse
import csv
import re
import struct
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MAIN = 'Custom Legendary Modifications Remade.esp'
PRE = 'A1ALM'
LOOSE_SOURCE = '@miscmod_mod_RailwayRifle_Scope_ScopeShort_Recon'   # vanilla loose mod, copied as a template
HOLOTAPE_MODEL = 'Props\\Holotape_Prop.nif'
CATALYSTS = {  # kind -> (editor ID, name, model)
    'weapon': ('A1ALMMISC_Catalyst_Weapon', 'CLM Catalyst: Legendary Weapon Core', 'Props\\MS11PowerRelayCoil.nif'),
    'armor': ('A1ALMMISC_Catalyst_Armor', 'CLM Catalyst: Legendary Armour Core', 'Props\\SynthChip\\SynthChip.nif'),
}
LOOSE_VALUE = {'common': 75, 'uncommon': 200, 'rare': 500, 'OP': 1500}
KINDS = ['Common', 'Uncommon', 'Rare', 'OP', 'Holotape', 'Catalyst']
# Drop-rate settings: (outer, inner) chance-none per kind. Drop chance = (100-outer)% x (100-inner)%.
RATES = {
    'Low':      {'Common': (90, 95), 'Uncommon': (90, 98), 'Rare': (95, 99), 'OP': (99, 99),
                 'Holotape': (90, 99), 'Catalyst': (98, 99)},
    'Standard': {'Common': (97, 0), 'Uncommon': (99, 0), 'Rare': (90, 97), 'OP': (90, 99),
                 'Holotape': (90, 95), 'Catalyst': (90, 98)},
    'Higher':   {'Common': (75, 0), 'Uncommon': (85, 0), 'Rare': (92, 0), 'OP': (95, 0),
                 'Holotape': (95, 0), 'Catalyst': (97, 0)},
}
RATE_LIST = ['Low', 'Standard', 'Higher']
SETTING_LOOT, SETTING_LOW, SETTING_HIGH = 'A1ALMSET_ModeLoot', 'A1ALMSET_DropLow', 'A1ALMSET_DropHigh'
LEGENDARY_ROLLS = 10
ENC_TYPE_LEGENDARY = 0x001CF26C  # Fallout4.esm keyword on legendary actors
SCRIPT = 'A1ALMLoot_GrantPerkScript'

FN_GET_ITEM_COUNT, FN_GET_GLOBAL_VALUE, FN_HAS_KEYWORD = 47, 74, 560
OP_EQ, OP_GE, FLAG_OR = 0 << 5, 3 << 5, 0x01
LVLF_ALL_LEVELS, LVLF_EACH_IN_COUNT, LVLF_USE_ALL = 0x01, 0x02, 0x04


def slug(text: str) -> str:
    return ''.join(w[:1].upper() + w[1:] for w in re.findall(r'[A-Za-z0-9]+', text))


def holotape_edid(kind: str, family: str) -> str:
    return f'A1ALMMISC_Unlock_{kind.capitalize()}_{slug(family)}'


def loose_edid(omod: str) -> str:
    return 'A1ALMMISC_LooseMod_' + omod.removeprefix('A1ALMOMOD_Legendary_')


def load_plan() -> list[dict]:
    return list(csv.DictReader((HERE / 'loot_plan.csv').open(encoding='utf8')))


def pct(outer: int, inner: int) -> str:
    return f'{(100 - outer) * (100 - inner) / 100:g}%'


def rate_welcome() -> str:
    lines = [f'How often CLM loot drops from each enemy you kill (starred legendary enemies roll {LEGENDARY_ROLLS} '
             'times).']
    for name in RATE_LIST:
        r = RATES[name]
        lines.append(f'{name}: common {pct(*r["Common"])}, uncommon {pct(*r["Uncommon"])}, rare {pct(*r["Rare"])}, '
                     f'OP {pct(*r["OP"])}, holotape {pct(*r["Holotape"])}, Legendary Core {pct(*r["Catalyst"])}.')
    return ' '.join(lines)


# ---------------------------------------------------------------------------------------------- step 1: spec
def write_spec(plan: list[dict], data: Path, ack: Path) -> Path:
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    costly = {}  # OMOD editor ID -> its costly recipe's editor ID
    p = Plugin.load(data / MAIN)
    omods = {r.formid: r.edid for r in p.records('OMOD') if p.is_own(r.formid)}
    for c in p.records('COBJ'):
        cn = c.get('CNAM')
        if cn and p.is_own(c.formid) and not c.edid.endswith(('FREE', '_Unlocked')):
            fid = struct.unpack('<I', cn.data)[0]
            if fid in omods:
                costly[omods[fid]] = c.edid

    s = ['# Generated by tools/loot/generate.py - do not edit', '', f'file | {MAIN}']
    for edid, name, model in CATALYSTS.values():
        s += [f'copy | {LOOSE_SOURCE} | {edid}', f'set | {edid} | FULL | {name}',
              f'set | {edid} | Model\\MODL | {model}', f'remove | {edid} | Model\\MODT',
              f'remove | {edid} | KWDA', f'remove | {edid} | KSIZ',
              f'set | {edid} | DATA\\Value | 1000', f'set | {edid} | DATA\\Weight | 0.1']
    for kind, fam in sorted({(r['kind'], r['family']) for r in plan}):
        e = holotape_edid(kind, fam)
        s += [f'copy | {LOOSE_SOURCE} | {e}',
              f'set | {e} | FULL | CLM Holotape: {fam} ({"Weapon" if kind == "weapon" else "Armour"})',
              f'set | {e} | Model\\MODL | {HOLOTAPE_MODEL}', f'remove | {e} | Model\\MODT',
              f'remove | {e} | KWDA', f'remove | {e} | KSIZ',
              f'set | {e} | DATA\\Value | 25', f'set | {e} | DATA\\Weight | 0']
    for r in plan:
        e = loose_edid(r['edid'])
        s += [f'copy | {LOOSE_SOURCE} | {e}', f'set | {e} | FULL | CLM: {r["name"]}',
              f'set | {e} | DATA\\Value | {LOOSE_VALUE[r["tier"]]}',
              f'set | {r["edid"]} | LNAM | @{e}',
              f'copy | @{costly[r["edid"]]} | co_{r["edid"]}_Unlocked']
    for kind in KINDS:
        s.append(f'new | LVLI | {PRE}LL_Pool_{kind}')
        for rate in RATE_LIST:
            s += [f'new | LVLI | {PRE}LL_Gate_{kind}_{rate}', f'new | LVLI | {PRE}LL_Drop_{kind}_{rate}']
    for rate in RATE_LIST:
        s += [f'new | LVLI | {PRE}LL_Drop_Normal_{rate}', f'new | LVLI | {PRE}LL_Drop_Legendary_{rate}']
    s += [f'prunerecords | {PRE}LL_',          # the single-rate lists from before drop rates became setting items
          f'new | PERK | {PRE}PERK_Loot',
          f'new | QUST | {PRE}QUST_Loot', f'set | {PRE}QUST_Loot | FULL | CLM Loot ({MAIN})',
          f'set | {PRE}QUST_Loot | DNAM\\Flags | 1',  # Start Game Enabled
          f'script | {PRE}QUST_Loot | {SCRIPT}',
          f'prop | {PRE}QUST_Loot | {SCRIPT} | LootPerk | Object | @{PRE}PERK_Loot',
          'prunerecords | A1ALMMISC_Unlock_', 'prunerecords | A1ALMMISC_LooseMod_',
          'prunerecords | A1ALMLOOT']   # the drop-rate globals from before drop rates became setting items
    path = HERE / 'build_spec.txt'
    path.write_text('\n'.join(s) + '\n', encoding='utf8')
    return path


def run_build(spec: Path, data: Path, ack: Path) -> None:
    cmd = [sys.executable, '-m', 'ack', 'xedit', 'run', 'build', MAIN, '--save', '--timeout', '900',
           '--param', f'SPEC={spec}']
    r = subprocess.run(cmd, cwd=ack, capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[0] if r.stdout.strip() else r.stderr)
    run = sorted((ack / 'private' / 'runs').glob('*-build'))[-1]
    result = (run / 'result.txt').read_text(encoding='utf8')
    print(result.splitlines()[0])
    if ' 0 errors' not in result.splitlines()[0]:
        raise SystemExit('\n'.join(l for l in result.splitlines() if 'ERROR' in l)[:4000])


# ------------------------------------------------------------------------------------------ step 2: raw parts
def ctda(op_flags: int, value: float, function: int, param1: int) -> bytes:
    return struct.pack('<B3sfH2sIIIIi', op_flags, b'\0\0\0', value, function, b'\0\0', param1, 0, 0, 0, -1)


def lvli(Subrecord, entries: list[tuple[int, int]], flags: int, chance_none: int = 0, glob: int | None = None):
    """Leveled item subrecords after EDID: entries are (form ID, count), all at level 1."""
    subs = [Subrecord('OBND', bytes(12)), Subrecord('LVLD', bytes([chance_none])), Subrecord('LVLM', b'\0'),
            Subrecord('LVLF', bytes([flags]))]
    if glob is not None:
        subs.append(Subrecord('LVLG', struct.pack('<I', glob)))
    assert len(entries) < 256, len(entries)
    subs.append(Subrecord('LLCT', bytes([len(entries)])))
    subs += [Subrecord('LVLO', struct.pack('<HHIHBB', 1, 0, fid, count, 0, 0)) for fid, count in entries]
    return subs


def write_raw(plan: list[dict], data: Path, ack: Path) -> None:
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord
    sys.path.insert(0, str(REPO / 'tools' / 'config'))
    from settings import ITEMS, setting_global, on_conds, off_conds   # not at import: settings imports this module
    p = Plugin.load(data / MAIN)

    def ref(edid: str) -> int:
        r = p.by_edid(edid)
        assert r is not None and p.is_own(r.formid), edid
        return r.formid

    def setting(key: str, on: bool) -> list[bytes]:
        return (on_conds if on else off_conds)(ref(ITEMS[key][0]), ref(setting_global(key)))

    def set_subs(rec, subs):
        edid = rec.subrecords[0]
        rec.subrecords[:] = [edid] + subs
        rec.mark_dirty()

    # unlocked recipes
    for r in plan:
        rec = p.by_edid(f'co_{r["edid"]}_Unlocked')
        hol = ref(holotape_edid(r['kind'], r['family']))
        loose = ref(loose_edid(r['edid']))
        subs = [s for s in rec.subrecords if s.sig != 'CTDA']
        at = next(i for i, s in enumerate(subs) if s.sig == 'CNAM')  # conditions go before CNAM
        subs[at:at] = [*[Subrecord('CTDA', d) for d in setting('loot', True)],
                       Subrecord('CTDA', ctda(OP_GE | FLAG_OR, 1.0, FN_GET_ITEM_COUNT, hol)),
                       Subrecord('CTDA', ctda(OP_GE, 1.0, FN_GET_ITEM_COUNT, loose))]
        if r['tier'] == 'OP':
            fv = next((s for s in subs if s.sig == 'FVPA'), None)
            if fv is None:  # a recipe that costs nothing (e.g. Mr. Freeze's): components go right after EDID
                fv = Subrecord('FVPA', b'')
                subs.insert(1, fv)
            cat = ref(CATALYSTS[r['kind']][0])
            pairs = [struct.unpack_from('<II', fv.data, i) for i in range(0, len(fv.data), 8)]
            if all(fid != cat for fid, _ in pairs):
                fv.data += struct.pack('<II', cat, 1)
        rec.subrecords[:] = subs
        rec.mark_dirty()
    # pools
    pools = {'Common': [], 'Uncommon': [], 'Rare': [], 'OP': [], 'Holotape': [], 'Catalyst': []}
    for r in plan:
        pools[{'common': 'Common', 'uncommon': 'Uncommon', 'rare': 'Rare', 'OP': 'OP'}[r['tier']]].append(
            (ref(loose_edid(r['edid'])), 1))
    for kind, fam in sorted({(r['kind'], r['family']) for r in plan}):
        pools['Holotape'].append((ref(holotape_edid(kind, fam)), 1))
    pools['Catalyst'] = [(ref(e), 1) for e, _, _ in CATALYSTS.values()]
    drops = defaultdict(list)   # rate -> drop lists
    for kind, items in pools.items():
        set_subs(p.by_edid(f'{PRE}LL_Pool_{kind}'), lvli(Subrecord, items, LVLF_ALL_LEVELS))
        for rate in RATE_LIST:
            outer, inner = RATES[rate][kind]
            gate, drop = f'{PRE}LL_Gate_{kind}_{rate}', f'{PRE}LL_Drop_{kind}_{rate}'
            set_subs(p.by_edid(gate), lvli(Subrecord, [(ref(f'{PRE}LL_Pool_{kind}'), 1)], LVLF_ALL_LEVELS,
                                           chance_none=inner))
            set_subs(p.by_edid(drop), lvli(Subrecord, [(ref(gate), 1)], LVLF_ALL_LEVELS, chance_none=outer))
            drops[rate].append(ref(drop))
    for rate in RATE_LIST:
        set_subs(p.by_edid(f'{PRE}LL_Drop_Normal_{rate}'),
                 lvli(Subrecord, [(d, 1) for d in drops[rate]], LVLF_ALL_LEVELS | LVLF_USE_ALL))
        set_subs(p.by_edid(f'{PRE}LL_Drop_Legendary_{rate}'),
                 lvli(Subrecord, [(d, LEGENDARY_ROLLS) for d in drops[rate]],
                      LVLF_ALL_LEVELS | LVLF_USE_ALL | LVLF_EACH_IN_COUNT))
    # perk: hidden, one rank; per drop rate two "Add Leveled List On Death" entries (normal, legendary target)
    rate_conds = {'Low': setting('low', True),
                  'Standard': setting('low', False) + setting('high', False),
                  'Higher': setting('low', False) + setting('high', True)}
    subs = [Subrecord('FULL', f'CLM Loot ({MAIN})'.encode('cp1252') + b'\0'), Subrecord('DESC', b'\0'),
            Subrecord('DATA', bytes([0, 0, 1, 0, 1]))]  # trait, level, ranks, playable, hidden
    entries = [(rate, legendary, f'{PRE}LL_Drop_{"Legendary" if legendary else "Normal"}_{rate}')
               for rate in RATE_LIST for legendary in (0, 1)]
    for entry_id, (rate, legendary, drop) in enumerate(entries):
        subs += [Subrecord('PRKE', bytes([2, 0, 0])),           # entry point, rank 0, priority 0
                 Subrecord('DATA', bytes([9, 8, 2])),           # Add Leveled List On Death, Add Leveled List, 2 tabs
                 Subrecord('PRKC', b'\0'),                      # tab 0: perk owner (the player)
                 *[Subrecord('CTDA', c) for c in setting('loot', True)],
                 *[Subrecord('CTDA', c) for c in rate_conds[rate]],
                 Subrecord('PRKC', b'\1'),                      # tab 1: the target
                 Subrecord('CTDA', ctda(OP_EQ, float(legendary), FN_HAS_KEYWORD, ENC_TYPE_LEGENDARY)),
                 Subrecord('EPFT', b'\3'), Subrecord('EPFB', struct.pack('<H', entry_id)),
                 Subrecord('EPFD', struct.pack('<I', ref(drop))), Subrecord('PRKF', b'')]
    set_subs(p.by_edid(f'{PRE}PERK_Loot'), subs)
    p.save(data / MAIN)
    print(f'{MAIN}: {len(plan)} unlocked recipes, pools ' + ', '.join(f'{k} {len(v)}' for k, v in pools.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    ap.add_argument('--raw-only', action='store_true', help='skip the xEdit build (records already exist)')
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    sys.path.insert(0, str(ack))
    plan = load_plan()
    if not a.raw_only:
        spec = write_spec(plan, data, ack)
        print(f'spec: {sum(1 for _ in spec.open())} lines')
        run_build(spec, data, ack)
    write_raw(plan, data, ack)


if __name__ == '__main__':
    main()
