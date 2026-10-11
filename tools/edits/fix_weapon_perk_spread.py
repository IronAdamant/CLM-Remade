"""Weapon legendaries' hidden perks work only with that weapon equipped (Nexus complaints #2 and #8, 2026-10-11).

Players reported weapon effects (infinite ammo, slow time, damage boosts) applying to weapons they had not modded, and
slow time never turning off. Weapon legendaries give the player hidden perks through their enchantment; nothing in
those perks checked which weapon is in use, so a perk the engine fails to remove (it can happen, e.g. when the
legendary is changed at a workbench) keeps working on every weapon.

The fix follows vanilla: each such perk gets its own keyword (A1ALMKW_WeaponPerk_<perk>); every weapon legendary that
grants it adds that keyword to the weapon (Keywords ADD), and the perk's effects require WornHasKeyword(keyword) on
the player - the equipped weapon must carry it. Entry-point perks get the condition on their perk-owner tab; ability
perks (the slow-time ones) on their ability spell's effects. Perks, magic effects, enchantments and spells that armour
legendaries share get weapon-only copies (suffix _W), so the armour versions keep working with every weapon.

    python tools/edits/fix_weapon_perk_spread.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4" [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import struct
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MAIN = 'Custom Legendary Modifications Remade.esp'
KEYWORD_TEMPLATE_OMOD = 'A1ALMOMOD_Legendary_Weapon_Recoilless_Variant_Electrical_Striker'  # has a Keywords property
FN_WORN_HAS_KEYWORD = 682


def run(ack: Path, *args: str) -> Path:
    r = subprocess.run([sys.executable, '-m', 'ack', 'xedit', 'run', *args], cwd=ack, capture_output=True, text=True)
    script = args[0]
    out = sorted((ack / 'private' / 'runs').glob(f'*-{script}'))[-1]
    if 'done' not in r.stdout:
        raise SystemExit(r.stdout + r.stderr)
    return out


def analyse(export: Path):
    sys.path.insert(0, str(REPO / 'tools' / 'audit'))
    import catalog as c
    cat = c.Catalog(export)
    mgef_perk = {n: c.edid_of(c.field(b, 'Perk to Apply')) for n, b in cat.r['MGEF'].items()}
    ench_mgefs = {n: re.findall(r'EFID - Base Effect = (\S+)', b) for n, b in cat.r['ENCH'].items()}
    perk_ability = {n: re.findall(r'Ability = (\S+)', b) for n, b in cat.r['PERK'].items()}
    ench_users = defaultdict(set)      # ENCH -> OMODs
    for om in cat.r['OMOD']:
        for fn, prop, v1, v2 in cat.props(om):
            if prop == 'Enchantments':
                ench_users[c.edid_of(v1)].add(om)
    is_weapon = lambda om: '_Weapon_' in om
    # weapon OMOD -> perks it grants, with the (ENCH, MGEF) path
    grants = defaultdict(list)
    perk_users = defaultdict(lambda: {'weapon': set(), 'armor': set()})
    mgef_users = defaultdict(lambda: {'weapon': set(), 'armor': set()})
    for ench, oms in ench_users.items():
        for mg in ench_mgefs.get(ench, []):
            pk = mgef_perk.get(mg)
            if not pk or pk == 'NULL' or pk not in cat.r['PERK']:
                continue
            for om in oms:
                side = 'weapon' if is_weapon(om) else 'armor'
                perk_users[pk][side].add(om)
                mgef_users[mg][side].add(om)
                if side == 'weapon':
                    grants[om].append((ench, mg, pk))
    return cat, grants, perk_users, mgef_users, ench_users, perk_ability


def short(edid: str) -> str:
    return re.sub(r'^A1ALMPERK_(Legendary_)?(Hidden_)?', '', edid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    sys.path.insert(0, str(ack))
    export = run(ack, 'export_records', MAIN, '--timeout', '400')
    cat, grants, perk_users, mgef_users, ench_users, perk_ability = analyse(export)

    perks = sorted({pk for g in grants.values() for _, _, pk in g})
    shared_perks = {pk for pk in perks if perk_users[pk]['armor']}
    print(f'{len(grants)} weapon legendaries grant {len(perks)} perks ({len(shared_perks)} shared with armour)')
    # names of the weapon-side records
    wperk = {pk: (pk + '_W' if pk in shared_perks else pk) for pk in perks}
    wmgef, wench, wspell = {}, {}, {}
    for om, g in grants.items():
        for ench, mg, pk in g:
            needs_copy = pk in shared_perks
            wmgef[mg] = mg + '_W' if needs_copy or mgef_users[mg]['armor'] else mg
            ench_shared = any('_Weapon_' not in o for o in ench_users[ench])
            wench[ench] = ench + '_W' if (needs_copy or wmgef[mg] != mg) and ench_shared else ench
    for pk in perks:
        for sp in perk_ability.get(pk, []):
            wspell[sp] = sp + '_W' if pk in shared_perks else sp
    keyword = {pk: f'A1ALMKW_WeaponPerk_{short(pk)}' for pk in perks}

    if a.dry_run:
        for pk in perks:
            print(f'  {wperk[pk]:70} kw {keyword[pk]}  abilities {perk_ability.get(pk)}')
        print('  MGEF copies:', [m for m, w in wmgef.items() if w != m])
        print('  ENCH copies:', [e for e, w in wench.items() if w != e])
        print('  SPEL copies:', [s for s, w in wspell.items() if w != s])
        return

    # 1. records: keywords, and weapon-only copies of shared records
    s = ['# Generated by fix_weapon_perk_spread.py', f'file | {MAIN}']
    for pk in perks:
        s += [f'new | KYWD | {keyword[pk]}']
        if wperk[pk] != pk:
            s += [f'copy | @{pk} | {wperk[pk]}']
    for old, new in {**wmgef, **wench, **wspell}.items():
        if new != old:
            s += [f'copy | @{old} | {new}']
    spec = HERE / 'fix_weapon_perk_spread.spec'
    spec.write_text('\n'.join(s) + '\n', encoding='utf8')
    out = run(ack, 'build', MAIN, '--save', '--timeout', '600', '--param', f'SPEC={spec}')
    print((out / 'result.txt').read_text(encoding='utf8').splitlines()[0])

    # 2. raw: repoint copies, add conditions, repoint weapon OMODs' enchantments
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord
    p = Plugin.load(data / MAIN)
    fid = lambda e: p.by_edid(e).formid

    def swap(rec, old_fid: int, new_fid: int) -> int:
        n = 0
        for sub in rec.subrecords:
            if old_fid != new_fid and struct.pack('<I', old_fid) in sub.data:
                sub.data = sub.data.replace(struct.pack('<I', old_fid), struct.pack('<I', new_fid))
                n += 1
        if n:
            rec.mark_dirty()
        return n

    def ctda(kw: int) -> Subrecord:
        return Subrecord('CTDA', struct.pack('<B3sfH2sIIIIi', 0, b'\0\0\0', 1.0, FN_WORN_HAS_KEYWORD, b'\0\0', kw, 0,
                                             0, 0, -1))

    for mg, w in wmgef.items():               # weapon MGEF copies point at the weapon perk
        if w != mg:
            pk = next(pk for g in grants.values() for _, m, pk in g if m == mg)
            swap(p.by_edid(w), fid(pk), fid(wperk[pk]))
    for e, w in wench.items():               # weapon ENCHs use the weapon MGEFs
        for mg, wm in wmgef.items():
            if wm != mg:
                swap(p.by_edid(w), fid(mg), fid(wm))
    for pk in perks:                         # weapon perks: ability spells -> weapon copies; conditions
        rec = p.by_edid(wperk[pk])
        for sp, ws in wspell.items():
            swap(rec, fid(sp), fid(ws))
        kw = fid(keyword[pk])
        subs = rec.subrecords
        i = 0
        while i < len(subs):
            if subs[i].sig == 'PRKE' and subs[i].data[0] == 2:          # entry point effect
                j = i + 2                                               # after PRKE, DATA
                if j < len(subs) and subs[j].sig == 'PRKC' and subs[j].data == b'\0':
                    k = j + 1
                    while k < len(subs) and subs[k].sig in ('CTDA', 'CIS1', 'CIS2'):
                        k += 1
                    subs.insert(k, ctda(kw))
                else:
                    subs[j:j] = [Subrecord('PRKC', b'\0'), ctda(kw)]
            i += 1
        rec.mark_dirty()
        for sp in perk_ability.get(pk, []):  # ability perks: condition every effect of the weapon spell
            spell = p.by_edid(wspell[sp])
            out_subs = []
            for k, sub in enumerate(spell.subrecords):
                out_subs.append(sub)
                nxt = spell.subrecords[k + 1].sig if k + 1 < len(spell.subrecords) else None
                if sub.sig in ('EFIT', 'CTDA', 'CIS1', 'CIS2') and nxt not in ('CTDA', 'CIS1', 'CIS2') and \
                        any(x.sig == 'EFIT' for x in out_subs):
                    out_subs.append(ctda(kw))
            spell.subrecords[:] = out_subs
            spell.mark_dirty()
    for om, g in grants.items():             # weapon OMODs use the weapon ENCH copies
        rec = p.by_edid(om)
        for ench, _, _ in g:
            swap(rec, fid(ench), fid(wench[ench]))
    p.save(data / MAIN)

    # 3. each weapon legendary adds the keywords of the perks it grants
    edits = ['# Generated by fix_weapon_perk_spread.py']
    for om, g in sorted(grants.items()):
        for pk in sorted({pk for _, _, pk in g}):
            edits.append(f'prop.add | {om} | Keywords | ADD | 431 | {KEYWORD_TEMPLATE_OMOD} | @{keyword[pk]}')
    path = HERE / 'fix_weapon_perk_spread_keywords.txt'
    path.write_text('\n'.join(edits) + '\n', encoding='utf8')
    out = run(ack, 'apply_edits', MAIN, '--save', '--timeout', '600', '--param', f'EDITS={path}')
    print((out / 'result.txt').read_text(encoding='utf8').splitlines()[0])



if __name__ == '__main__':
    main()
