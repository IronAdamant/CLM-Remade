"""2.1: weak or broken balanced legendaries brought up to the base game's own (reported on Nexus, 2026-10-15; the
author's go-ahead the same day). Baselines per hit: Wounding 25 bleed, Incendiary 15 fire, Poisoner's 30 poison,
Explosive +15 splash, Two Shot +1 projectile and +100% damage (an extra projectile alone splits the same damage).

    python tools/edits/buff_weak_21.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Step 1 (apply_edits): properties, magnitudes, durations, descriptions, Elemental Strikin's own enchantment.
Step 2 (written directly): conditions and perk values.
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
EN = 'A1ALMEnch_'
BOOST = f'{OM}Weapon_DamageBoost_1x'          # template for an AttackDamage MUL+ADD property
HEALTH_PCT, IS_SPRINTING, GET_RANDOM = 430, 568, 77
EQ, LT, LE = 0, 4, 5

EDITS = [
    # extra projectiles that only split the same damage: give them the damage, as Two Shot has
    *[f'prop.add | {OM}Weapon_{k} | AttackDamage | MUL+ADD | 1 | {BOOST}'
      for k in ('Scattering_Base_RedLaser', 'Scattering_Variant_LtBlueLaser', 'Scattering_Variant_Plasma',
                'Generically80sActionHero')],
    f'prop.add | {OM}Weapon_Carbonatin | AttackDamage | MUL+ADD | 0.5 | {BOOST}',
    f'prop.add | {OM}Weapon_ShotgunSurgeons_Trainee | AttackDamage | MUL+ADD | 0.5 | {BOOST}',
    f"text.set | {OM}Weapon_Carbonatin | DESC | Fires one more projectile with every shot (+50% damage in all). "
    "Critical kills can burst into a shower of caps.",
    f"text.set | {OM}Weapon_ShotgunSurgeons_Trainee | DESC | Your weapon fires 3 more pellets (+50% damage in all), with "
    "a 30% wider spread.",
    f"text.set | {OM}Weapon_Generically80sActionHero | DESC | Four shot (+100% damage in all). -30% fire rate, 50% "
    "magazine size, -30% recoil, -25% accuracy. While you stand still you take 30% less damage.",
    # Thumpin': the base game's Explosive, without halving the fire rate
    f'prop.remove | {OM}Weapon_Thumping_Base | Speed',
    f"text.set | {OM}Weapon_Thumping_Base | DESC | Turns your rounds into explosives (15 extra damage around the impact, "
    "like the base game's Explosive) with massively increased range.",
    # damage over time up to the base game's
    f'field.set | {EN}Constant_Effect_Custom_Effect_Weapon_Burning | Effects\\[0]\\EFIT\\Duration | 3',
    f"text.set | {OM}Weapon_Burning | DESC | Sets your targets on fire for 15 damage over 3 seconds, like Incendiary. One "
    "hit in ten burns hotter, for 25 more, and can turn them to ash.",
    f'effect.magnitude | {EN}FaF_Contact_Target_Acid_Acidic | 0 | 6',
    f'text.set | {OM}Weapon_Acidic | DESC | Your hits burn with acid: 30 acid damage over 5 seconds.',
    f'effect.magnitude | {EN}FaF_Contact_Effect_Target_Hostile_Bleed_LesserBleeding | 0 | 4',
    f'field.set | {EN}FaF_Contact_Effect_Target_Hostile_Bleed_LesserBleeding | Effects\\[0]\\EFIT\\Duration | 5',
    f'text.set | {OM}Weapon_LesserBleed | DESC | Targets bleed for 20 points of additional damage over 5 seconds.',
    f'effect.magnitude | {EN}FaF_Contact_Effect_Target_Hostile_Electrical_Raydens | 0 | 75',
    f"text.set | {OM}Weapon_Raydens | DESC | Critical hits deal 75 extra shock damage.",
    f'effect.magnitude | {EN}FaF_Contact_Effect_Target_Hostile_Hinokagutsuchi | 1 | 5',
    f"text.set | {OM}Weapon_Hinokagutsuchi | DESC | Shishkebab meets Grognak's Axe: hits deal 25 extra damage over 5 "
    "seconds and stagger, and burning targets can turn to ash.",
    # Elemental Strikin': its own enchantment (it shared Nature's Wrath's), 20% each
    f'rec.copy | {EN}FaF_Contact_Custom_Effect_Target_Hostile_NaturesWrath | {EN}FaF_Contact_Custom_Effect_Target_Hostile_ElementalStriking',
    f"text.set | {EN}FaF_Contact_Custom_Effect_Target_Hostile_ElementalStriking | FULL | CLM: Elemental Strikin'",
    f'field.set | {OM}Weapon_ElementalStriking | DATA\\Properties\\[0]\\Value 1 | @{EN}FaF_Contact_Custom_Effect_Target_Hostile_ElementalStriking',
    f"text.set | {OM}Weapon_ElementalStriking | DESC | Each hit has a 20% chance each to deal 20 fire, cryo, poison and "
    "electrical damage over two seconds.",
    # handling
    f'prop.set | {OM}Weapon_Compacted | AmmoCapacity | MUL+ADD | 0.5',
    f'text.set | {OM}Weapon_Compacted | DESC | 50% greater ammo capacity.',
    *[f'prop.set | {OM}Weapon_Beginner | {p} | MUL+ADD | 0.1' for p in ('Speed', 'AttackDamage', 'ReloadSpeed')],
    *[f'prop.set | {OM}Weapon_Beginner | {p} | MUL+ADD | -0.1'
      for p in ('AimModelRecoilMaxDegPerShot', 'AimModelRecoilMinDegPerShot', 'AimModelRecoilArcDeg',
                'AimModelRecoilArcRotateDeg')],
    f'text.set | {OM}Weapon_Beginner | DESC | Your starting weapon legendary effect! 10% more damage, fire rate and '
    'reload speed, and 10% less recoil.',
    # armour
    f'text.set | {OM}Armor_PerkV_Refilling_Base_10P | FULL | CLM: Refilling (25%)',
    f'text.set | {OM}Armor_PerkV_Refilling_Base_10P | DESC | When you fire the last round in your magazine, there is a '
    "25% chance it refills by itself, as with the Scrounger perk's top rank. (Scrounger rank 4 uses the same chance, so "
    'the two do not add up.)',
    f'text.set | {OM}Armor_PerkV_Bouncing_Sprint30P | DESC | While you sprint, 30% of the projectiles coming at you '
    'bounce off.',
    f'text.set | {OM}Armor_Escapist | DESC | Below 30% health you turn invisible while you sprint; it ends when you stop '
    'or your health recovers.',
    # numbers that were stronger than described
    f'effect.magnitude | {EN}FaF_Contact_Effect_Target_Hostile_Incendiary_15DT | 0 | 3',
    f'field.set | {EN}FaF_Contact_Effect_Target_Hostile_Incendiary_15DT | Effects\\[0]\\EFIT\\Duration | 5',
    f"text.set | {OM}Weapon_NastierPoisoning | DESC | 90 points of poison damage over 10 seconds: a nastier Poisoner's "
    '(30).',
]

# step 2: perk values and conditions
PERK_VALUES = {'A1ALMPERK_Legendary_Hidden_Armor_AimStabilize_50P': (1.1, 1.5),
               'A1ALMPERK_Legendary_Hidden_Armor_Refilling10P': (10.0, 25.0),
               'A1ALMPERK_Legendary_Hidden_Armor_NegateDamageWhileNotMoving30P_W': (0.3, 0.7)}


def write_raw(data: Path, ack: Path) -> None:
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord

    p = Plugin.load(data / MAIN)

    def ctda(fn, op, value):
        return Subrecord('CTDA', struct.pack('<B3sfH2sIIIIi', op << 5, b'\0\0\0', value, fn, b'\0\0', 0, 0, 0, 0, -1))

    def per_effect(r, conds):
        out, n = [], -1
        for s in r.subrecords:
            if s.sig == 'CTDA':
                continue
            out.append(s)
            n += s.sig == 'EFID'
            if s.sig == 'EFIT':
                out += [ctda(*c) for c in conds[n]]
        r.subrecords[:] = out
        r.mark_dirty()

    for edid, (old, new) in PERK_VALUES.items():
        r = p.by_edid(edid)
        hits = [i for i, s in enumerate(r.subrecords) if s.sig == 'EPFD' and len(s.data) == 4 and
                round(struct.unpack('<f', s.data)[0], 3) == old]
        assert len(hits) == 1, edid
        r.subrecords[hits[0]] = Subrecord('EPFD', struct.pack('<f', new))
        r.mark_dirty()

    # Bullet Escapist: it checked health >= 30% (the opposite of its text); now while sprinting, any health
    r = p.by_edid('A1ALMPERK_Legendary_Hidden_Armor_Bouncing_Condition_Sprint30P')
    before = len(r.subrecords)
    r.subrecords[:] = [s for s in r.subrecords if not (s.sig == 'CTDA' and struct.unpack_from('<H', s.data, 8)[0] == HEALTH_PCT)]
    assert len(r.subrecords) == before - 1
    r.mark_dirty()
    # Escapist's: health == 15% (never, in practice) -> health <= 30%
    r = p.by_edid('A1ALMEnch_Constant_Effect_Custom_Effect_Escapist')
    n = 0
    for i, s in enumerate(r.subrecords):
        if s.sig == 'CTDA' and struct.unpack_from('<H', s.data, 8)[0] == HEALTH_PCT:
            d = bytearray(s.data)
            d[0] = (LE << 5) | (d[0] & 31)
            struct.pack_into('<f', d, 4, 0.30)
            r.subrecords[i] = Subrecord('CTDA', bytes(d))
            n += 1
    assert n == 5
    r.mark_dirty()
    # Burning: the first burn every hit, the hotter one and the ash one in ten
    one_in_ten = [(GET_RANDOM, LT, 10.0)]
    per_effect(p.by_edid('A1ALMEnch_Constant_Effect_Custom_Effect_Weapon_Burning'), [[], one_in_ten, one_in_ten])
    # Elemental Strikin': 20% each
    per_effect(p.by_edid('A1ALMEnch_FaF_Contact_Custom_Effect_Target_Hostile_ElementalStriking'),
               [[(GET_RANDOM, LT, 20.0)]] * 4)
    p.save(data / MAIN)
    print('perk values, Bullet Escapist, Escapist\'s, Burning and Elemental Strikin\' conditions written')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    path = HERE / 'buff_weak_21.txt'
    path.write_text('# Generated by buff_weak_21.py - edit that, not this file.\n' + '\n'.join(EDITS) + '\n', encoding='utf8')
    r = subprocess.run([sys.executable, '-m', 'ack', 'xedit', 'run', 'apply_edits', MAIN, '--save', '--timeout', '900',
                        '--param', f'EDITS={path}'], cwd=ack, capture_output=True, text=True)
    result = (sorted((ack / 'private' / 'runs').glob('*-apply_edits'))[-1] / 'result.txt').read_text(encoding='utf8')
    print(result.splitlines()[0])
    if ' 0 errors' not in result.splitlines()[0]:
        raise SystemExit('\n'.join(l for l in result.splitlines() if l.startswith('ERROR')) + r.stderr)
    write_raw(data, ack)


if __name__ == '__main__':
    main()
