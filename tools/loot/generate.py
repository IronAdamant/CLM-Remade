"""Generate CLM's loot mode from tools/loot/loot_plan.csv (run plan.py first).

    python tools/loot/generate.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Builds into the plugins in the game's Data folder (main plugin and add-ons), safe to re-run:
- per family: an unlock holotape (MISC, weightless). Carrying it shows the family's unlocked recipes.
- per legendary: a loose mod (MISC, linked from the legendary's LNAM like vanilla loose mods) and an unlocked recipe
  (copy of the costly recipe) with conditions
      GetGlobalValue(A1ALMAFREE) == 4                 loot mode (the holotape's "No-craft" setting)
      GetItemCount(family holotape) >= 1   OR         unlocked...
      GetItemCount(loose mod) >= 1                    ...or the player found this legendary
  (the engine groups ORs before ANDs). OP recipes also take one catalyst (weapon or armour).
- two OP catalysts (weapon, armour).
- drop lists: per kind of drop (common, uncommon, rare, OP, holotape, catalyst) a pool, gated twice by global chance-none
  values (Outer, Inner: 1% x 1% gives 0.01% steps for the Low / Standard / Higher drop-rate settings). Add-on pools
  get an extra fixed gate for their share of the legendaries, so installing an add-on does not raise drop rates.
- a hidden perk per plugin with two "Add Leveled List On Death" entries (in loot mode; normal targets get one roll,
  targets with EncTypeLegendary ten), granted by a start-game quest running A1ALMLoot_GrantPerkScript.

Steps: write tools/loot/build_spec.txt and run AgentCreationKit's builder (creates/updates records), then write the
parts xEdit makes awkward directly with ack.plugin (conditions, leveled lists, globals, perk entries), then check
every plugin with FO4Edit.
"""
from __future__ import annotations

import argparse
import csv
import re
import shutil
import struct
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MAIN = 'Custom Legendary Modifications Remade.esp'
ADDONS = {'CLM - Automatron.esp': 'Automatron', 'CLM - Far Harbor.esp': 'FarHarbor',
          'CLM - Nuka-World.esp': 'NukaWorld', 'CLM - Contraptions.esp': 'Contraptions'}
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
DEFAULT_RATE = 'Standard'
LEGENDARY_ROLLS = 10
ENC_TYPE_LEGENDARY = 0x001CF26C  # Fallout4.esm keyword on legendary actors
SCRIPT = 'A1ALMLoot_GrantPerkScript'
RATE_SCRIPT = 'A1ALMLoot_RateTerminalScript'
CONFIG_TERM = 'A1ALMTERM_Holotape_Config_RM'          # the holotape's main configuration menu
RATE_TERM = 'A1ALMTERM_Holotape_Config_LootRate'      # new: drop-rate submenu
LOOT_ITEM_TEXT = ('Loot version - Hunt for legendaries', 'Loot mode is on.',
                  'Loot mode is on. CLM legendaries are no longer crafted from the start: they drop from the enemies '
                  'you kill, as loose mods you can attach at any workbench. Starred legendary enemies drop far more.\n\n'
                  'CLM holotapes drop too: carry one to craft its whole family of legendaries. OP legendaries also '
                  'need a Legendary Core (weapon or armour) to craft.\n\n'
                  'Set how often things drop under "Loot version - Drop rate". To go back to crafting everything, '
                  'run a Starting Configuration on the Free or Costly version page.')
RATE_ITEM = (4, 'Loot version - Drop rate', 'Loot drop rate')
RATE_NAMES = {1: 'Low', 2: 'Standard', 3: 'Higher'}

FN_GET_ITEM_COUNT, FN_GET_GLOBAL_VALUE, FN_HAS_KEYWORD = 47, 74, 560
OP_EQ, OP_GE, FLAG_OR = 0 << 5, 3 << 5, 0x01
LVLF_ALL_LEVELS, LVLF_EACH_IN_COUNT, LVLF_USE_ALL = 0x01, 0x02, 0x04


def slug(text: str) -> str:
    return ''.join(w[:1].upper() + w[1:] for w in re.findall(r'[A-Za-z0-9]+', text))


def holotape_edid(kind: str, family: str) -> str:
    return f'A1ALMMISC_Unlock_{kind.capitalize()}_{slug(family)}'


def loose_edid(omod: str) -> str:
    return 'A1ALMMISC_LooseMod_' + omod.removeprefix('A1ALMOMOD_Legendary_')


def prefix(plugin: str) -> str:
    return 'A1ALM' if plugin == MAIN else f'A1ALM{ADDONS[plugin]}'


def load_plan() -> list[dict]:
    return list(csv.DictReader((HERE / 'loot_plan.csv').open(encoding='utf8')))


def pct(outer: int, inner: int) -> str:
    return f'{(100 - outer) * (100 - inner) / 100:g}%'


def rate_welcome() -> str:
    lines = [f'How often CLM loot drops from each enemy you kill (starred legendary enemies roll {LEGENDARY_ROLLS} '
             'times).']
    for name in RATE_NAMES.values():
        r = RATES[name]
        lines.append(f'{name}: common {pct(*r["Common"])}, uncommon {pct(*r["Uncommon"])}, rare {pct(*r["Rare"])}, '
                     f'OP {pct(*r["OP"])}, holotape {pct(*r["Holotape"])}, Legendary Core {pct(*r["Catalyst"])}.')
    return ' '.join(lines)


def write_rate_script() -> Path:
    """The drop-rate terminal's script, generated from RATES so the menu and the drop lists always agree."""
    out = [f'Scriptname {RATE_SCRIPT} extends Terminal',
           '{CLM loot mode: the drop-rate menu. Items 1-3 set the chance-none globals that gate the drop lists.',
           'Generated by tools/loot/generate.py from its RATES table - edit that, not this file.}', '',
           'GlobalVariable[] Property Outer Auto Const Mandatory',
           '{Outer gates, in the order: ' + ', '.join(KINDS) + '}',
           'GlobalVariable[] Property Inner Auto Const Mandatory',
           'GlobalVariable Property Rate Auto Const Mandatory',
           '{0 Low, 1 Standard, 2 Higher}', '',
           'Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)']
    for item, name in RATE_NAMES.items():
        out.append(f'\t{"If" if item == 1 else "ElseIf"} auiMenuItemID == {item}')
        for i, kind in enumerate(KINDS):
            o, n = RATES[name][kind]
            out += [f'\t\tOuter[{i}].SetValue({o})', f'\t\tInner[{i}].SetValue({n})']
        out += [f'\t\tRate.SetValue({item - 1})', f'\t\tDebug.Notification("CLM loot drop rate: {name}")']
    out += ['\tEndIf', 'EndEvent', '']
    path = REPO / 'source' / 'User' / f'{RATE_SCRIPT}.psc'
    path.write_text('\n'.join(out), encoding='utf8')
    return path


def update_config_menu(main, Subrecord, rate_term: int) -> None:
    """Configuration menu: item 3 ("No-craft version / WIP" in 1.09) becomes the loot-mode item, and item 4 opens the
    drop-rate submenu (added once)."""
    term = main.by_edid(CONFIG_TERM)
    subs = term.subrecords
    item_of = []  # (start index of each menu item, its ITID)
    for i, s in enumerate(subs):
        if s.sig == 'ITXT':
            item_of.append([i, None])
        elif s.sig == 'ITID' and item_of:
            item_of[-1][1] = struct.unpack('<H', s.data)[0]
    starts = [i for i, _ in item_of] + [len(subs)]
    for k, (start, item) in enumerate(item_of):
        if item != 3:
            continue
        for i in range(start, starts[k + 1]):
            text = {'ITXT': LOOT_ITEM_TEXT[0], 'RNAM': LOOT_ITEM_TEXT[1], 'UNAM': LOOT_ITEM_TEXT[2]}.get(subs[i].sig)
            if text is not None:
                subs[i].data = text.encode('cp1252') + b'\0'
    if all(item != RATE_ITEM[0] for _, item in item_of):
        # the last item ends at the first subrecord after it that is not part of a menu item
        end = starts[-2]
        while end < len(subs) and subs[end].sig in ('ITXT', 'RNAM', 'ANAM', 'ITID', 'TNAM', 'UNAM', 'VNAM',
                                                     'CTDA', 'CIS1', 'CIS2', 'INAM', 'SNAM', 'BSIZ'):
            end += 1
        subs[end:end] = [Subrecord('ITXT', RATE_ITEM[1].encode('cp1252') + b'\0'),
                         Subrecord('RNAM', RATE_ITEM[2].encode('cp1252') + b'\0'),
                         Subrecord('ANAM', b'\x04'), Subrecord('ITID', struct.pack('<H', RATE_ITEM[0])),
                         Subrecord('TNAM', struct.pack('<I', rate_term))]
        isiz = next(s for s in subs if s.sig == 'ISIZ')
        isiz.data = struct.pack('<I', struct.unpack('<I', isiz.data)[0] + 1)
    term.mark_dirty()


# ---------------------------------------------------------------------------------------------- step 1: spec
def write_spec(plan: list[dict], data: Path, ack: Path) -> Path:
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    costly = {}  # OMOD editor ID -> its costly recipe's editor ID
    for name in [MAIN, *ADDONS]:
        p = Plugin.load(data / name)
        omods = {r.formid: r.edid for r in p.records('OMOD') if p.is_own(r.formid)}
        for c in p.records('COBJ'):
            cn = c.get('CNAM')
            if cn and p.is_own(c.formid) and not c.edid.endswith(('FREE', '_Unlocked')):
                fid = struct.unpack('<I', cn.data)[0]
                if fid in omods:
                    costly[omods[fid]] = c.edid

    s = ['# Generated by tools/loot/generate.py - do not edit']
    by_plugin = defaultdict(list)
    for r in plan:
        by_plugin[r['plugin']].append(r)
    families = {(r['kind'], r['family']): r['holotape_plugin'] for r in plan}
    for plugin in [MAIN, *ADDONS]:
        if plugin not in by_plugin and plugin != MAIN:
            continue
        pre = prefix(plugin)
        s += ['', f'file | {plugin}']
        if plugin == MAIN:
            for edid, name, model in CATALYSTS.values():
                s += [f'copy | {LOOSE_SOURCE} | {edid}', f'set | {edid} | FULL | {name}',
                      f'set | {edid} | Model\\MODL | {model}', f'remove | {edid} | Model\\MODT',
                      f'remove | {edid} | KWDA', f'remove | {edid} | KSIZ',
                      f'set | {edid} | DATA\\Value | 1000', f'set | {edid} | DATA\\Weight | 0.1']
            for kind in KINDS:
                for half in ('Outer', 'Inner'):
                    s.append(f'new | GLOB | A1ALMLOOT_{kind}_{half}')
            s.append('new | GLOB | A1ALMLOOTRATE')
            s += [f'copy | @A1ALMTERM_Holotape_Config_Free_RM | {RATE_TERM}', f'remove | {RATE_TERM} | VMAD',
                  f'set | {RATE_TERM} | FULL | (CLM) Terminal - Loot drop rate',
                  f'set | {RATE_TERM} | NAM0 | CLM Terminal - Loot drop rate',
                  f'set | {RATE_TERM} | WNAM | {rate_welcome()}', f'menuclear | {RATE_TERM}']
            for item, label in ((1, 'Low - extremely rare drops'), (2, 'Standard - the intended rate'),
                                (3, 'Higher - generous drops')):
                s.append(f'menu | {RATE_TERM} | {item} | {label} | - | -')
            s += [f'script | {RATE_TERM} | {RATE_SCRIPT}',
                  f'prop | {RATE_TERM} | {RATE_SCRIPT} | Outer | Array of Object | ' +
                  ','.join(f'@A1ALMLOOT_{k}_Outer' for k in KINDS),
                  f'prop | {RATE_TERM} | {RATE_SCRIPT} | Inner | Array of Object | ' +
                  ','.join(f'@A1ALMLOOT_{k}_Inner' for k in KINDS),
                  f'prop | {RATE_TERM} | {RATE_SCRIPT} | Rate | Object | @A1ALMLOOTRATE']
        for (kind, fam), home in sorted(families.items()):
            if home != plugin:
                continue
            e = holotape_edid(kind, fam)
            s += [f'copy | {LOOSE_SOURCE} | {e}',
                  f'set | {e} | FULL | CLM Holotape: {fam} ({"Weapon" if kind == "weapon" else "Armour"})',
                  f'set | {e} | Model\\MODL | {HOLOTAPE_MODEL}', f'remove | {e} | Model\\MODT',
                  f'remove | {e} | KWDA', f'remove | {e} | KSIZ',
                  f'set | {e} | DATA\\Value | 25', f'set | {e} | DATA\\Weight | 0']
        for r in by_plugin[plugin]:
            e = loose_edid(r['edid'])
            s += [f'copy | {LOOSE_SOURCE} | {e}', f'set | {e} | FULL | CLM: {r["name"]}',
                  f'set | {e} | DATA\\Value | {LOOSE_VALUE[r["tier"]]}',
                  f'set | {r["edid"]} | LNAM | @{e}',
                  f'copy | @{costly[r["edid"]]} | co_{r["edid"]}_Unlocked']
        for kind in KINDS:
            if plugin != MAIN and kind == 'Catalyst':
                continue
            for part in ('Pool', 'Gate', 'Drop'):
                s.append(f'new | LVLI | {pre}LL_{part}_{kind}')
        s += [f'new | LVLI | {pre}LL_Drop_Normal', f'new | LVLI | {pre}LL_Drop_Legendary',
              f'new | PERK | {pre}PERK_Loot',
              f'new | QUST | {pre}QUST_Loot', f'set | {pre}QUST_Loot | FULL | CLM Loot ({plugin})',
              f'set | {pre}QUST_Loot | DNAM\\Flags | 1',  # Start Game Enabled
              f'script | {pre}QUST_Loot | {SCRIPT}',
              f'prop | {pre}QUST_Loot | {SCRIPT} | LootPerk | Object | @{pre}PERK_Loot',
              'prunerecords | A1ALMMISC_Unlock_', 'prunerecords | A1ALMMISC_LooseMod_']
    path = HERE / 'build_spec.txt'
    path.write_text('\n'.join(s) + '\n', encoding='utf8')
    return path


def run_build(spec: Path, data: Path, ack: Path) -> None:
    cmd = [sys.executable, '-m', 'ack', 'xedit', 'run', 'build', MAIN, '--save', '--timeout', '900',
           '--param', f'SPEC={spec}']
    for addon in ADDONS:
        if (data / addon).exists():
            cmd += ['--also-load', addon]
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
    main = Plugin.load(data / MAIN)
    plugins = {MAIN: main}
    for a in ADDONS:
        if (data / a).exists():
            plugins[a] = Plugin.load(data / a)

    def ref(in_plugin: str, edid: str) -> int:
        """Form ID of a CLM record as seen from in_plugin (records live in in_plugin or in the main plugin)."""
        p = plugins[in_plugin]
        r = p.by_edid(edid)
        if r is not None and p.is_own(r.formid):
            return r.formid
        r = main.by_edid(edid)
        assert r is not None, edid
        return (p.masters.index(MAIN) << 24) | (r.formid & 0xFFFFFF)

    def set_subs(rec, subs):
        edid = rec.subrecords[0]
        rec.subrecords[:] = [edid] + subs
        rec.mark_dirty()

    # globals (main): defaults = Standard
    for kind in KINDS:
        for half, value in zip(('Outer', 'Inner'), RATES[DEFAULT_RATE][kind]):
            set_subs(main.by_edid(f'A1ALMLOOT_{kind}_{half}'),
                     [Subrecord('FNAM', b'f'), Subrecord('FLTV', struct.pack('<f', value))])
    set_subs(main.by_edid('A1ALMLOOTRATE'), [Subrecord('FNAM', b'f'), Subrecord('FLTV', struct.pack('<f', 1))])

    counts = defaultdict(int)  # tier -> legendaries in all plugins, for add-on shares
    for r in plan:
        counts[r['tier']] += 1
    fam_counts = defaultdict(int)
    for (kind, fam), home in {(r['kind'], r['family']): r['holotape_plugin'] for r in plan}.items():
        fam_counts[home] += 1
    total_fams = sum(fam_counts.values())

    for name, p in plugins.items():
        pre = prefix(name)
        mine = [r for r in plan if r['plugin'] == name]
        # unlocked recipes
        for r in mine:
            rec = p.by_edid(f'co_{r["edid"]}_Unlocked')
            hol = ref(name, holotape_edid(r['kind'], r['family']))
            loose = ref(name, loose_edid(r['edid']))
            free = ref(name, 'A1ALMAFREE')
            subs = [s for s in rec.subrecords if s.sig != 'CTDA']
            at = next(i for i, s in enumerate(subs) if s.sig == 'CNAM')  # conditions go before CNAM
            subs[at:at] = [Subrecord('CTDA', ctda(OP_EQ, 4.0, FN_GET_GLOBAL_VALUE, free)),
                           Subrecord('CTDA', ctda(OP_GE | FLAG_OR, 1.0, FN_GET_ITEM_COUNT, hol)),
                           Subrecord('CTDA', ctda(OP_GE, 1.0, FN_GET_ITEM_COUNT, loose))]
            if r['tier'] == 'OP':
                fv = next((s for s in subs if s.sig == 'FVPA'), None)
                if fv is None:  # a recipe that costs nothing (e.g. Mr. Freeze's): components go right after EDID
                    fv = Subrecord('FVPA', b'')
                    subs.insert(1, fv)
                cat = ref(name, CATALYSTS[r['kind']][0])
                pairs = [struct.unpack_from('<II', fv.data, i) for i in range(0, len(fv.data), 8)]
                if all(fid != cat for fid, _ in pairs):
                    fv.data += struct.pack('<II', cat, 1)
            rec.subrecords[:] = subs
            rec.mark_dirty()
        # pools
        pools = {'Common': [], 'Uncommon': [], 'Rare': [], 'OP': [], 'Holotape': [], 'Catalyst': []}
        for r in mine:
            pools[{'common': 'Common', 'uncommon': 'Uncommon', 'rare': 'Rare', 'OP': 'OP'}[r['tier']]].append(
                (ref(name, loose_edid(r['edid'])), 1))
        for (kind, fam), home in sorted({(r['kind'], r['family']): r['holotape_plugin'] for r in plan}.items()):
            if home == name:
                pools['Holotape'].append((ref(name, holotape_edid(kind, fam)), 1))
        if name == MAIN:
            pools['Catalyst'] = [(ref(name, e), 1) for e, _, _ in CATALYSTS.values()]
        drops = []
        for kind, items in pools.items():
            if name != MAIN and kind == 'Catalyst':
                continue
            share = 0
            if name != MAIN:  # an add-on's pool only gets its share of the whole tier
                n_all = total_fams if kind == 'Holotape' else counts[kind if kind == 'OP' else kind.lower()]
                share = 100 - round(100 * len(items) / n_all) if n_all else 100
            set_subs(p.by_edid(f'{pre}LL_Pool_{kind}'), lvli(Subrecord, items, LVLF_ALL_LEVELS, chance_none=share))
            set_subs(p.by_edid(f'{pre}LL_Gate_{kind}'), lvli(Subrecord, [(ref(name, f'{pre}LL_Pool_{kind}'), 1)],
                                                              LVLF_ALL_LEVELS, glob=ref(name, f'A1ALMLOOT_{kind}_Inner')))
            set_subs(p.by_edid(f'{pre}LL_Drop_{kind}'), lvli(Subrecord, [(ref(name, f'{pre}LL_Gate_{kind}'), 1)],
                                                              LVLF_ALL_LEVELS, glob=ref(name, f'A1ALMLOOT_{kind}_Outer')))
            if items:
                drops.append(ref(name, f'{pre}LL_Drop_{kind}'))
        set_subs(p.by_edid(f'{pre}LL_Drop_Normal'),
                 lvli(Subrecord, [(d, 1) for d in drops], LVLF_ALL_LEVELS | LVLF_USE_ALL))
        set_subs(p.by_edid(f'{pre}LL_Drop_Legendary'),
                 lvli(Subrecord, [(d, LEGENDARY_ROLLS) for d in drops],
                      LVLF_ALL_LEVELS | LVLF_USE_ALL | LVLF_EACH_IN_COUNT))
        # perk: hidden, one rank; two "Add Leveled List On Death" entries
        free = ref(name, 'A1ALMAFREE')
        subs = [Subrecord('FULL', f'CLM Loot ({name})'.encode('cp1252') + b'\0'), Subrecord('DESC', b'\0'),
                Subrecord('DATA', bytes([0, 0, 1, 0, 1]))]  # trait, level, ranks, playable, hidden
        for entry_id, (legendary, drop) in enumerate(((0, f'{pre}LL_Drop_Normal'), (1, f'{pre}LL_Drop_Legendary'))):
            subs += [Subrecord('PRKE', bytes([2, 0, 0])),           # entry point, rank 0, priority 0
                     Subrecord('DATA', bytes([9, 8, 2])),           # Add Leveled List On Death, Add Leveled List, 2 tabs
                     Subrecord('PRKC', b'\0'),                      # tab 0: perk owner (the player)
                     Subrecord('CTDA', ctda(OP_EQ, 4.0, FN_GET_GLOBAL_VALUE, free)),
                     Subrecord('PRKC', b'\1'),                      # tab 1: the target
                     Subrecord('CTDA', ctda(OP_EQ, float(legendary), FN_HAS_KEYWORD, ENC_TYPE_LEGENDARY)),
                     Subrecord('EPFT', b'\3'), Subrecord('EPFB', struct.pack('<H', entry_id)),
                     Subrecord('EPFD', struct.pack('<I', ref(name, drop))), Subrecord('PRKF', b'')]
        set_subs(p.by_edid(f'{pre}PERK_Loot'), subs)
        if name == MAIN:
            update_config_menu(main, Subrecord, ref(name, RATE_TERM))
        p.save(data / name)
        print(f'{name}: {len(mine)} unlocked recipes, pools ' +
              ', '.join(f'{k} {len(v)}' for k, v in pools.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    ap.add_argument('--raw-only', action='store_true', help='skip the xEdit build (records already exist)')
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    sys.path.insert(0, str(ack))
    plan = load_plan()
    rate = write_rate_script()
    subprocess.run([sys.executable, str(REPO / 'tools' / 'papyrus' / 'compile.py'), '--game', a.game, rate.stem],
                   check=True)
    shutil.copy(REPO / 'data' / 'SCRIPTS' / f'{rate.stem}.pex', data / 'Scripts' / f'{rate.stem}.pex')
    if not a.raw_only:
        spec = write_spec(plan, data, ack)
        print(f'spec: {sum(1 for _ in spec.open())} lines')
        run_build(spec, data, ack)
    write_raw(plan, data, ack)
    # the drop-rate menu was rebuilt: hide-when-selected conditions for every configuration terminal again
    subprocess.run([sys.executable, str(REPO / 'tools' / 'edits' / 'terminal_hide_selected.py'), str(data / MAIN)],
                   check=True, capture_output=True)


if __name__ == '__main__':
    main()
