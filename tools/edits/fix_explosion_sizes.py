"""Per-bullet explosions down to vanilla size (Nexus complaint #5, author's option A, 2026-10-11).

These legendaries put an explosion on every bullet or beam, but used missile-sized blasts (500 units, about 7 m;
Jupiter's Wrathful 300, BioReactive (Nuclear) a Fat Man's 850), so any shot at something close caught the shooter. Vanilla's Explosive legendary uses an
outer radius of 200. Each blast below is used only by these legendaries (checked: no grenade or launcher shares
them); damage is unchanged, the outer radius becomes 200 and the full-damage inner radius at most 100.

Usage: python fix_explosion_sizes.py <plugin.esp>   (edits in place; FO4Edit must not have it open)
"""
import struct
import sys

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402

OUTER, INNER_MAX = 200.0, 100.0
EXPLOSIONS = {
    'A1AMLEXP_Missile_Explosion_Custom_Effect_HighExplosive':
        "High Explosive, Viciously Thumpin', Explosively Penetratin'",
    'A1ALMEXP_Havoc_Explosion_Variant_MissileExplosion_Impact': 'Havoc (Bullets)',
    'A1ALMEXP_Havoc_Explosion_Variant_MolotovCTailExplosion_Impact': 'Havoc (Red Laser)',
    'A1ALMEXP_Havoc_Explosion_Variant_PulseExplosion_Impact': 'Havoc (Blue Laser)',
    'A1AMLEXP_Missile_Explosion_Custom_Effect_Hecate': "Ultima Hecate's",
    'A1ALMEXP_Garm_Cryo_Explosion': "Garm's",
    'A1ALMEXP_ExplosivelyStriking_Gauss_Explosion': 'Explosively Striking',
    'A1ALMEXP_Custom_Explosion_TeleportFX_Variant_JupitersWrath': "Jupiter's Wrathful",
    # BioReactive: explodes the corpse when a hit kills (vanilla FortuneFinderCapsScript), so close kills hit you
    'A1ALMEXP_BioReactive_Base_MissileExplosion': 'BioReactive Explosive (Explosive)',
    'A1ALMEXP_BioReactive_Variant_Cryo': 'BioReactive Explosive (Cryo)',
    'A1ALMEXP_BioReactive_Variant_Fire': 'BioReactive Explosive (Fire)',
    'A1ALMEXP_BioReactive_Variant_Plasma': 'BioReactive Explosive (Plasma)',
    'A1ALMEXP_BioReactive_Variant_Pulse': 'BioReactive Explosive (Pulse)',
    'A1ALMEXP_BioReactive_Variant_FatmanExplosion': 'BioReactive Explosive (Nuclear)',
}

path = sys.argv[1]
p = Plugin.load(path)
for edid, users in EXPLOSIONS.items():
    r = p.by_edid(edid)
    d = bytearray(r.get('DATA').data)
    force, dmg, inner, outer = struct.unpack_from('<ffff', d, 24)
    struct.pack_into('<ff', d, 32, min(inner, INNER_MAX), OUTER)
    r.get('DATA').data = bytes(d)
    r.mark_dirty()
    print(f'{users}: damage {dmg:g}, radius {inner:g}/{outer:g} -> {min(inner, INNER_MAX):g}/{OUTER:g}')
p.save(path)
