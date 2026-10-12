"""2.1 requests built from perk entry points (docs/PLAN_2.1.md 1): Bloodlust, Blitzkrieg, Nature's Wrath, Staminator
and Weapon Mastery (the "OP Weapon Skills" request). Records only, so they work on every platform.

    python tools/edits/gen_req2_perks.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Works on the main plugin in the game's Data folder (FO4Edit must not have it open), in two steps:
1. tools/edits/req2_perk_legendaries.txt (apply_edits): each legendary is a copy of its closest sibling (legendary and
   recipes, so it keeps the mod's naming, config categories and OP flag); each perk is a copy of Marathon Runnin''s
   chain (hidden perk -> "Perk to Apply" magic effect -> constant enchantment).
2. The perks' entry points, written directly (ENTRIES below). Weapon perks follow 2.0's rule (fix_weapon_perk_spread.py):
   each has its own keyword, the legendary adds it to the weapon, and every entry requires WornHasKeyword(it).

Entry point IDs, functions and condition tab counts were read from Fallout4.esm's perks (their FO4Edit names next to
the raw values). Values follow vanilla's scales: crit chance in points (Fortify Crit Chance chem: +25), crit damage
mult (Better Criticals: +0.5), crit charge (Hancock: x1.2), scope stability (x1.25 already stops all sway, 2.0 test).
No entry point changes weapon draw or scope zoom speed, so Weapon Mastery leaves those out.
"""
from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = 'Custom Legendary Modifications Remade.esp'
OM = 'A1ALMOMOD_Legendary_'
CO = 'co_A1ALMOMOD_Legendary_'
PROP1 = 'DATA\\Properties\\[0]\\Value 1'
KEYWORD_TEMPLATE_OMOD = 'A1ALMOMOD_Legendary_Weapon_Recoilless_Variant_Electrical_Striker'  # has a Keywords property

# entry point: (id, condition tabs); Fallout4.esm names
CRIT_CHANCE = (1, 3)          # Mod My Critical Hit Chance
CRIT_DAMAGE = (2, 3)          # Mod My Critical Hit Damage Mult
POWER_ATTACK_AP = (27, 2)     # Mod Power Attack Action Points
WEAPON_DAMAGE = (35, 3)       # Mod Weapon Attack Damage
VATS_ATTACK_AP = (79, 3)      # Mod VATS Attack Action Points
SPRINT_AP = (96, 1)           # Mod Sprint AP Drain Rate
SCOPE_STABILITY = (102, 1)    # Mod Actor Scope Stability
VATS_RELOAD_AP = (117, 1)     # Mod VATS Reload Action Points
VATS_CRIT_CHARGE = (119, 1)   # Mod VATS Critical Charge
VATS_HIT = (123, 1)           # Mod VATS Hit Chance
GUN_RANGE = (141, 2)          # Mod Gun Range Mult
HOLD_BREATH_AP = (142, 1)     # Mod Scope Hold Breath AP Drain Mult
BASH_CRIT = (154, 2)          # Mod Bash Critical Chance
SET, ADD, MUL = 1, 2, 3
FN_GET_HEALTH_PERCENTAGE, FN_WORN_HAS_KEYWORD = 430, 682
OP_LT = 4

# name -> (weapon?, entries); an entry is (entry point, function, value, health below or None)
# Staminator: V.A.T.S. attacks x0.01, not 0, in case a zero cost breaks V.A.T.S.'s shots-per-AP count.
ENTRIES = {
    'Bloodlust': (True, [(WEAPON_DAMAGE, ADD, 10.0, 1 - k / 10) for k in range(1, 10)]),
    'Blitzkrieg': (True, [(VATS_HIT, MUL, 1.6, None), (GUN_RANGE, MUL, 1.6, None), (VATS_ATTACK_AP, MUL, 0.05, None),
                          (CRIT_DAMAGE, MUL, 2.0, None), (VATS_CRIT_CHARGE, MUL, 2.0, None)]),
    'Staminator': (False, [(SPRINT_AP, SET, 0.0, None), (POWER_ATTACK_AP, SET, 0.0, None),
                           (HOLD_BREATH_AP, SET, 0.0, None), (VATS_RELOAD_AP, SET, 0.0, None),
                           (VATS_ATTACK_AP, MUL, 0.01, None)]),
    'WeaponMastery': (False, [(CRIT_CHANCE, ADD, 20.0, None), (CRIT_DAMAGE, ADD, 1.0, None),
                              (VATS_CRIT_CHARGE, MUL, 2.0, None), (BASH_CRIT, ADD, 20.0, None),
                              (SCOPE_STABILITY, MUL, 1.25, None), (VATS_ATTACK_AP, MUL, 0.75, None)]),
}
# name -> (in-game name, description, recipe template, perk name)
LEGENDARIES = {
    'Bloodlust': ("CLM: Bloodlust", 'The lower your health, the harder you hit: +10 damage for every 10% of health '
                  'you have lost, up to +90.', 'Weapon_Vampiric', 'CLM Perk: Bloodlust'),
    'Blitzkrieg': ("CLM: Blitzkrieg", '+60% V.A.T.S. accuracy and range, V.A.T.S. attacks cost 95% less Action '
                   'Points, critical hits do double damage and your critical meter fills twice as fast.',
                   'Weapon_Custom_EagleEyed', 'CLM Perk: Blitzkrieg'),
    'Staminator': ("CLM: Staminator", 'Sprinting, power attacks, holding your breath with a scope and reloading in '
                   'V.A.T.S. cost no Action Points, and V.A.T.S. attacks almost none. You can breathe underwater.',
                   'Armor_NanoCoated', 'CLM Perk: Staminator'),
    'WeaponMastery': ("CLM: Weapon Mastery", '+20% critical hit chance, +100% critical damage, your critical meter '
                      'fills twice as fast, +20% bash critical chance, steady scopes and V.A.T.S. attacks cost 25% '
                      'less Action Points. No weapon damage bonus.', 'Armor_NanoCoated', 'CLM Perk: Weapon Mastery'),
}


def edits() -> list[str]:
    lines = ['# Generated by gen_req2_perks.py - edit that, not this file.']

    def legendary(new, template, recipes, name, desc):
        lines.extend([f'rec.copy | {OM}{template} | {OM}{new}', f'text.set | {OM}{new} | FULL | {name}',
                      f'text.set | {OM}{new} | DESC | {desc}', f'rec.copy | {CO}{recipes} | {CO}{new}',
                      f'rec.copy | {CO}{recipes}FREE | {CO}{new}FREE', f'field.set | {CO}{new} | CNAM | @{OM}{new}',
                      f'field.set | {CO}{new}FREE | CNAM | @{OM}{new}'])

    for key, (weapon, _) in ENTRIES.items():
        name, desc, recipes, perk_name = LEGENDARIES[key]
        side = 'Weapon' if weapon else 'Armor'
        perk, mgef, ench = perk_edid(key), f'A1ALMMGEF_Constant_Effect_Custom_Effect_Perk_{key}', \
            f'A1ALMEnch_Constant_Effect_Custom_Effect_{key}'
        lines += [f'rec.copy | A1ALMPERK_Legendary_Hidden_Armor_SprintReduceAPCost_75P | {perk}',
                  f'text.set | {perk} | FULL | {perk_name}',
                  f'text.set | {perk} | DESC | {desc}',
                  f'rec.copy | A1ALMMGEF_Constant_Effect_Custom_Effect_Perk_SprintReduceAPCost_75P | {mgef}',
                  f'text.set | {mgef} | FULL | {perk_name}',
                  f'field.set | {mgef} | Magic Effect Data\\DATA\\Perk to Apply | @{perk}',
                  f'rec.copy | A1ALMEnch_Constant_Effect_Custom_Effect_SprintReduceAPCost_75P | {ench}',
                  f'text.set | {ench} | FULL | {name}',
                  f'field.set | {ench} | Effects\\[0]\\EFID | @{mgef}']
        template = 'Weapon_Chilling' if weapon else 'Armor_PerkV_MarathonRunning'
        legendary(f'{side}_{key}', template, recipes, name, desc)
        lines.append(f'field.set | {OM}{side}_{key} | {PROP1} | @{ench}')
        if weapon:
            lines += [f'rec.copy | A1ALMKW_WeaponPerk_Armor_VatsPenetrator_100P | {keyword_edid(key)}',
                      f'prop.add | {OM}{side}_{key} | Keywords | ADD | 431 | {KEYWORD_TEMPLATE_OMOD} | '
                      f'@{keyword_edid(key)}']
    lines.append(f'prop.add | {OM}Armor_Staminator | Enchantments | ADD | 431 | {OM}Armor_Staminator | '
                 f'@EnchWaterBreathing')

    # --- Nature's Wrath: Angry Nerd's chance-based elements, four of them at 10% each, and +25% fire rate ---
    cryo = 'A1ALMMGEF_Target_Effect_Hostile_CryoDamage'      # CLM's "Cold" only slows: a cryo copy of Fire
    lines += [f'rec.copy | A1ALMMGEF_Target_Effect_Hostile_Fire | {cryo}',
              f'text.set | {cryo} | FULL | CLM: Hostile Effect [Cryo Damage]',
              f'field.set | {cryo} | Magic Effect Data\\DATA\\Hit Shader | @CryoDamageFXS',
              f'field.set | {cryo} | KWDA\\[0] | @DamageTypeCyro']
    ench = 'A1ALMEnch_FaF_Contact_Custom_Effect_Target_Hostile_NaturesWrath'
    lines += [f'rec.copy | A1ALMEnch_FaF_Contact_Custom_Effect_Target_Hostile_AngryNerds | {ench}',
              f"text.set | {ench} | FULL | CLM: Nature's Wrath",
              f'effect.add | {ench} | 2 | @A1ALMMGEF_Target_Effect_Hostile_Electrical',
              f'effect.remove | {ench} | 3',                   # Angry Nerd's cripple
              f'field.set | {ench} | Effects\\[1]\\EFID | @{cryo}']
    for i in range(4):                                       # poison, cryo, fire, electrical: 10 a second for 2 s
        lines += [f'effect.magnitude | {ench} | {i} | 10',
                  f'field.set | {ench} | Effects\\[{i}]\\EFIT\\Duration | 2',
                  f'field.set | {ench} | Effects\\[{i}]\\Conditions\\[0]\\CTDA\\Comparison Value | 10']
    legendary('Weapon_NaturesWrath', 'Weapon_Chilling', 'Weapon_Vampiric', "CLM: Nature's Wrath",
              'Each hit has a 10% chance each to deal 20 fire, cryo, poison and electrical damage over two seconds. '
              'Your weapon fires 25% faster.')
    lines += [f'field.set | {OM}Weapon_NaturesWrath | {PROP1} | @{ench}',
              f'prop.add | {OM}Weapon_NaturesWrath | Speed | MUL+ADD | 0.25 | {OM}Weapon_Quicker_Base']
    return lines


def perk_edid(key: str) -> str:
    return f'A1ALMPERK_Legendary_Hidden_{"Weapon" if ENTRIES[key][0] else "Armor"}_{key}'


def keyword_edid(key: str) -> str:
    return f'A1ALMKW_WeaponPerk_Weapon_{key}'


def write_entries(data: Path, ack: Path) -> None:
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord

    def ctda(fn: int, value: float, param: int = 0, op: int = 0) -> Subrecord:
        return Subrecord('CTDA', struct.pack('<B3sfH2sIIIIi', op << 5, b'\0\0\0', value, fn, b'\0\0', param, 0, 0, 0,
                                             -1))

    p = Plugin.load(data / MAIN)
    for key, (weapon, entries) in ENTRIES.items():
        perk = p.by_edid(perk_edid(key))
        subs = perk.subrecords
        del subs[next(i for i, s in enumerate(subs) if s.sig == 'PRKE'):]
        for n, ((ep, tabs), fn, value, health_below) in enumerate(entries):
            conds = [ctda(FN_WORN_HAS_KEYWORD, 1.0, p.by_edid(keyword_edid(key)).formid)] if weapon else []
            if health_below is not None:
                conds.append(ctda(FN_GET_HEALTH_PERCENTAGE, round(health_below, 2), op=OP_LT))
            subs += [Subrecord('PRKE', struct.pack('<BBB', 2, 0, 50)), Subrecord('DATA', struct.pack('<BBB', ep, fn, tabs))]
            if conds:
                subs += [Subrecord('PRKC', b'\0')] + conds
            subs += [Subrecord('EPFT', b'\x01'), Subrecord('EPFB', struct.pack('<H', n)),
                     Subrecord('EPFD', struct.pack('<f', value)), Subrecord('PRKF', b'')]
        perk.mark_dirty()
        print(f'{perk_edid(key)}: {len(entries)} entries')
    p.save(data / MAIN)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    path = HERE / 'req2_perk_legendaries.txt'
    lines = edits()
    path.write_text('\n'.join(lines) + '\n', encoding='utf8')
    r = subprocess.run([sys.executable, '-m', 'ack', 'xedit', 'run', 'apply_edits', MAIN, '--save', '--timeout', '600',
                        '--param', f'EDITS={path}'], cwd=ack, capture_output=True, text=True)
    run = sorted((ack / 'private' / 'runs').glob('*-apply_edits'))[-1]
    result = (run / 'result.txt').read_text(encoding='utf8')
    print(result.splitlines()[0])
    if ' 0 errors' not in result.splitlines()[0]:
        raise SystemExit('\n'.join(l for l in result.splitlines() if l.startswith('ERROR')) + r.stderr)
    write_entries(data, ack)


if __name__ == '__main__':
    main()
