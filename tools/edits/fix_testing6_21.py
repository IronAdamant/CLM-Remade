"""2.1: sixth round of fixes from the author's in-game testing and video (2026-10-16).

    python tools/edits/fix_testing6_21.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

- Necromancer's: resurrected bodies came back with their combat AI not working (they stood still in the open world
  too, video). The body now turns to ash with its loot in the pile, and a fresh copy of it fights for the player, then
  crumbles to an empty ash pile (its own gear removed). Author's design, 2026-10-16.
- Jumper's / Momentum (scripts only): the ability stayed on in a save where the armour was already worn (the timer
  used a variable such effects never set); they now remove it from GetTargetActor().
- DragonBlade (script only): SetPosition also put up a loading screen; the dash is a TranslateTo now.
Script properties only (records unchanged otherwise).
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

MAIN = 'Custom Legendary Modifications Remade.esp'
PLAYER_FACTION, AGGRESSION, CONFIDENCE = 0x1C21C, 0x2BC, 0x2BD
ASH_PILE, ASH_SHADER = 0x9142E, 0x139F8E          # Fallout4.esm AshPile01, CritLaserFXS (Disintegratin' (Red)'s)
ACTOR_TYPES = [0x13794, 0x13795, 0x13798, 0x2CB73, 0x6D7B6, 0xEAFB7, 0xB2BF3, 0x2CB71, 0x10C3CE, 0x317AA]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    sys.path.insert(0, a.ack)
    from ack.plugin import Plugin

    path = Path(a.game) / 'Data' / MAIN
    p = Plugin.load(path)
    w = lambda s: struct.pack('<H', len(s)) + s.encode('ascii')
    obj = lambda f: b'\x01\x01' + struct.pack('<HhI', 0, -1, f)
    objs = lambda fs: b'\x0b\x01' + struct.pack('<I', len(fs)) + b''.join(struct.pack('<HhI', 0, -1, f) for f in fs)

    def vmad(script, props):
        return struct.pack('<hhH', 6, 2, 1) + w(script) + b'\0' + struct.pack('<H', len(props)) + \
            b''.join(w(n) + v for n, v in props)

    r = p.by_edid('A1ALMMGEF_Constant_Effect_Weapon_Necromancers')
    r.set('VMAD', vmad('A1ALMMGEF_NecromancerEffect', [
        ('RisenSpell', obj(p.by_edid('A1ALMSPEL_Weapon_Necromancers_Risen').formid)),
        ('AshPile', obj(ASH_PILE)), ('AshShader', obj(ASH_SHADER))]))
    r.mark_dirty()
    r = p.by_edid('A1ALMMGEF_Target_Effect_Risen')
    r.set('VMAD', vmad('A1ALMMGEF_RisenEffect', [
        ('AllyFaction', obj(PLAYER_FACTION)), ('Aggression', obj(AGGRESSION)), ('Confidence', obj(CONFIDENCE)),
        ('ActorTypes', objs(ACTOR_TYPES)), ('AshPile', obj(ASH_PILE)), ('AshShader', obj(ASH_SHADER))]))
    r.mark_dirty()
    p.save(path)
    print("Necromancer's raises an ash copy")


if __name__ == '__main__':
    main()
