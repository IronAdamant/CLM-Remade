"""2.1: third round of fixes from the author's in-game testing (2026-10-16).

    python tools/edits/fix_testing3_21.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

- CQC, DragonBlade, Cinematic Excellence did nothing: they were copied from Critically Concentratin', an armour-type
  mod, and turned into weapon mods afterwards. An OMOD property is stored as an index whose meaning depends on the
  form type, so their armour "Enchantments" became a weapon "Speed" (and DragonBlade's +200 damage too). The bad
  properties are replaced with real Enchantments / AttackDamage ones (no other legendary had this: catalog audit).
- Hello Neighbour!: SetPlayerEnemy(false) alone did not calm Gunners; the script also makes them neutral to the
  player's faction (A1ALMMGEF_FactionFriendEffect's new PlayerFaction property).
- Flamin': the flamer stream fired one puff per trigger pull; the weapon is now automatic, so holding fires a stream.
- Shockingly Lobbin': the Lightning Gun's chain explosion has no damage and only arcs from the gun itself, so the
  grenade did nothing. It now bursts with the pulse grenade's explosion and 100 damage.
- Radiatin' (Elements): raised so it can be felt (3 fire, 3 shock, 5 rads a second, 20% slower).
- Necromancer's (script only): each body rises once.
- Rallyin': it only worked on allies in combat (a condition inherited from Radiatin' (Healing)); now whenever they
  are near you, which is also how it was tested.
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
EN = 'A1ALMEnch_Constant_Effect_Custom_Effect_'
GUNNER_FACTION, PLAYER_FACTION = 0x58303, 0x1C21C
IS_IN_COMBAT = 289
SHOCK = 'A1ALMEXP_Lobbing_Variant_Lobber_Impact_Lightning'
EDITS = [
    # weapon mods whose properties were armour indices
    f'prop.remove | {OM}Weapon_CQC | Speed',
    f'prop.add | {OM}Weapon_CQC | Enchantments | ADD | 431 | {OM}Weapon_Bloodlust | @{EN}CQC',
    f'prop.remove | {OM}Weapon_CinematicExcellence | Speed',
    f'prop.add | {OM}Weapon_CinematicExcellence | Enchantments | ADD | 431 | {OM}Weapon_Bloodlust | @{EN}CinematicExcellence',
    f'prop.remove | {OM}Weapon_DragonBlade | Speed',
    f'prop.remove | {OM}Weapon_DragonBlade | Speed',
    f'prop.add | {OM}Weapon_DragonBlade | Enchantments | ADD | 431 | {OM}Weapon_Bloodlust | @{EN}DragonBlade',
    f'prop.add | {OM}Weapon_DragonBlade | AttackDamage | ADD | 200 | {OM}Weapon_DamageBoost_1x',
    # Flamin': hold to fire the stream
    f'prop.add | {OM}Weapon_Flaming | IsAutomatic | SET | True | {OM}Weapon_Automatic_Base',
    f"text.set | {OM}Weapon_Flaming | DESC | This mod turns your weapon into one of the favourite tools in the "
    "pyromaniac's arsenal: it shoots a flamer stream, fully automatic, so hold the trigger. Your ammo does not change.",
    # Shockingly Lobbin': a real explosion
    f'rec.copy | A1ALMEXP_Lobbing_Variant_Lobber_Impact_Electrical | {SHOCK}',
    f'field.set | {SHOCK} | DATA\\Damage | 100',
    f'field.set | A1ALMPROJ_Lobbing_Variant_Lobber_Impact_Lightning | DNAM\\Explosion | @{SHOCK}',
    f"text.set | {OM}Weapon_Lobbing_Variant_Impact_Lightning | DESC | Your weapon is converted into a shock grenade "
    "launcher: the grenade bursts in an electrical blast (100 damage) that also scrambles robots, like a pulse "
    "grenade. Your ammo does not change.",
    # Radiatin' (Elements): noticeable
    *[f'effect.magnitude | A1ALMSPEL_Aura_Radiating_Elements | {i} | {m}' for i, m in enumerate((3, 3, 5, 20))],
    f"text.set | {OM}Armor_Radiating_Elements | DESC | Enemies near you burn and are shocked (3 damage a second each), "
    'are irradiated (5 rads a second) and move 20% slower.',
]


def write_raw(data: Path, ack: Path) -> None:
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin

    p = Plugin.load(data / MAIN)
    w = lambda s: struct.pack('<H', len(s)) + s.encode('ascii')
    obj = lambda f: b'\x01\x01' + struct.pack('<HhI', 0, -1, f)
    r = p.by_edid('A1ALMMGEF_Constant_Effect_Armor_HelloNeighbour')
    r.set('VMAD', struct.pack('<hhH', 6, 2, 1) + w('A1ALMMGEF_FactionFriendEffect') + b'\0' + struct.pack('<H', 2) +
          w('FriendlyFaction') + obj(GUNNER_FACTION) + w('PlayerFaction') + obj(PLAYER_FACTION))
    r.mark_dirty()
    # Rallyin': inherited Radiatin' (Healing)'s "ally in combat" condition; a rally works whenever allies are near
    r = p.by_edid('A1ALMSPEL_Aura_Rallying')
    r.subrecords[:] = [x for x in r.subrecords if not (x.sig == 'CTDA' and struct.unpack_from('<H', x.data, 8)[0] == IS_IN_COMBAT)]
    r.mark_dirty()
    p.save(data / MAIN)
    print("Hello Neighbour! knows the player faction; Rallyin' works out of combat too")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    path = HERE / 'fix_testing3_21.txt'
    path.write_text('# Generated by fix_testing3_21.py - edit that, not this file.\n' + '\n'.join(EDITS) + '\n', encoding='utf8')
    r = subprocess.run([sys.executable, '-m', 'ack', 'xedit', 'run', 'apply_edits', MAIN, '--save', '--timeout', '900',
                        '--param', f'EDITS={path}'], cwd=ack, capture_output=True, text=True)
    result = (sorted((ack / 'private' / 'runs').glob('*-apply_edits'))[-1] / 'result.txt').read_text(encoding='utf8')
    print(result.splitlines()[0])
    if ' 0 errors' not in result.splitlines()[0]:
        raise SystemExit('\n'.join(l for l in result.splitlines() if l.startswith('ERROR')) + r.stderr)
    write_raw(data, ack)


if __name__ == '__main__':
    main()
