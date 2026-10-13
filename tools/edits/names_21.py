"""2.1 name and description fixes (docs/PLAN_2.1.md 8).

    python tools/edits/names_21.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

The author named many legendaries after his own references or the requester's wording, so names are only touched
where two legendaries share one name, or for plain typos and stray punctuation. Unusual names that may be references
stay as they are (Gunslanger's, Convert Operator's, Yamamoto's Mighty...). Descriptions are fixed where they state
the wrong effect or none. Writes the main plugin in the game's Data folder directly; safe to re-run. Re-run
tools/loot/generate.py afterwards (loose mods and holotapes copy the names).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAIN = 'Custom Legendary Modifications Remade.esp'
OM = 'A1ALMOMOD_Legendary_'

# editor ID (without the prefix) -> new in-game name
NAMES = {
    # two legendaries shared each of these names: the limited-ammo versions get "(Limited)" like the other Elementals
    'Weapon_Havoc_Base_Bullets_Limited': 'CLM: Havoc (Bullets, Limited)',
    'Weapon_Havoc_Variant_Plasma_Limited': 'CLM: Havoc (Plasma, Limited)',
    'Weapon_Havoc_Variant_LtBlueLaser_Limited': 'CLM: Havoc (Blue Laser, Limited)',
    'Weapon_Havoc_Variant_RedLaser_Limited': 'CLM: Havoc (Red Laser, Limited)',
    'Weapon_Elements_Base_Limited_Fire': "CLM: Prometheus' Fiery (Limited)",
    # the +500 one; the author's 2016 sheet: "Alien nano-coated" (+250) and "Alien Enhanced Nano-Coated" (+500)
    'Armor_AlienNanoCoated': 'CLM: Alien Enhanced Nano-Coated',
    # typos and stray punctuation
    'Weapon_Recoilless_Variant_Electrical_Striker': 'CLM: Silenced Electrical Striker',
    'Armor_NMU': 'CLM: Mighty Nearly Unbreakable',
    'Weapon_LiarsCompedium': "CLM: Liar's Compendium",
    'Weapon_CompressedVortexSynthesized': 'CLM: Compressed Vortex Synthesized',
    'Weapon_HydrasFang_Base': "CLM: Hydra's Fanged",
    'Weapon_Vampiric_Variant_ReapersEmbrace': "CLM: Reaper's Embrace",
}
NAME_REPLACE = [('Yaoi Guai', 'Yao Guai')]

FISTOS = re.compile(r'Armor_IncreaseWeaponDamage_(\d+)P$')
FISTOS_DESC = ('When you want to give your damage a little... boost. All your weapons do {n}% more damage. Only your '
               "best Fisto's piece counts.")
NIMBLE = re.compile(r'Armor_Nimble_(\d+)$')
COMBINED = re.compile(r'Armor_PerkV_Fortify_CombinedSpeedJump_(\d+)$')
DESCRIPTIONS = {'Armour_SantaPriscas': 'Increases carry weight by 75.'}
DESC_REPLACE = [('victom', 'victim'), ('laucher', 'launcher'), ('after each re;pads', 'after each reload'),
                ('nevending', 'never-ending'), ('  ', ' '), (' .', '.')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    sys.path.insert(0, a.ack)
    from ack.plugin import Plugin

    path = Path(a.game) / 'Data' / MAIN
    p = Plugin.load(path)
    assert not p.is_localized
    text = lambda r, sig: r.get(sig).zstring if r.get(sig) else ''
    put = lambda r, sig, s: r.set(sig, s.encode('cp1252') + b'\0')
    changed = []
    for r in p.records('OMOD'):
        if not (r.edid or '').startswith(OM):
            continue
        key = r.edid[len(OM):]
        name, desc = text(r, 'FULL'), text(r, 'DESC')
        new_name = NAMES.get(key, name)
        for old, new in NAME_REPLACE:
            new_name = new_name.replace(old, new)
        new_desc = DESCRIPTIONS.get(key, desc)
        if m := FISTOS.match(key):
            new_desc = FISTOS_DESC.format(n=m.group(1))
        elif m := NIMBLE.match(key):
            new_desc = f'You move {m.group(1)}% faster while you aim.'
        elif m := COMBINED.match(key):
            new_desc = f'This mod increases your movement speed and your jump height by {m.group(1)}%.'
        for old, new in DESC_REPLACE:
            while old in new_desc:
                new_desc = new_desc.replace(old, new)
        if new_desc.endswith(','):                    # the Concentratin' family
            new_desc = new_desc[:-1] + '.'
        if (new_name, new_desc) != (name, desc):
            if new_name != name:
                put(r, 'FULL', new_name)
            if new_desc != desc:
                put(r, 'DESC', new_desc)
            r.mark_dirty()
            changed.append(f'{name}' + (f' -> {new_name}' if new_name != name else '') +
                           (' (description)' if new_desc != desc else ''))
    p.save(path)
    print('\n'.join(changed))
    print(f'{len(changed)} legendaries renamed or redescribed')


if __name__ == '__main__':
    main()
