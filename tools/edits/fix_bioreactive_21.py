"""2.1: BioReactive rounds (all six) and Singularity explode on every hit, not only on killing hits (reported on Nexus,
2026-10-15).

    python tools/edits/fix_bioreactive_21.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Their magic effects ran vanilla's FortuneFinderCapsScript, which only places its explosion if the target is already
dead when the effect ends: on any hit that did not kill, nothing exploded. They now run A1ALMMGEF_ExplodeOnHitEffect
(same explosion, every hit). PC and Xbox; the PlayStation build puts the vanilla script back (kills only) and says so.
Cap Showerin' and Carbonatin' keep the vanilla script: exploding on a kill is what they are for.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

MAIN = 'Custom Legendary Modifications Remade.esp'
SCRIPT = 'A1ALMMGEF_ExplodeOnHitEffect'
EFFECTS = ('A1ALMMGEF_Target_Effect_Hostile_Explosion_BioReactive_', 'A1ALMMGEF_Target_Effect_Hostile_Explosion_Singularity')


def vmad(script: str, prop: str, form: int) -> bytes:
    w = lambda s: struct.pack('<H', len(s)) + s.encode('ascii')
    return (struct.pack('<hhH', 6, 2, 1) + w(script) + b'\0' + struct.pack('<H', 1) + w(prop) + b'\x01\x01' +
            struct.pack('<HhI', 0, -1, form))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    sys.path.insert(0, a.ack)
    from ack.plugin import Plugin

    path = Path(a.game) / 'Data' / MAIN
    p = Plugin.load(path)
    blasts = {r.formid for r in p.records('EXPL') if p.is_own(r.formid)}
    done = []
    for r in p.records('MGEF'):
        if not (p.is_own(r.formid) and r.edid.startswith(EFFECTS)):
            continue
        data = r.get('VMAD').data
        found = {struct.unpack_from('<I', data, i)[0] for i in range(len(data) - 3)} & blasts
        assert len(found) == 1, r.edid
        r.set('VMAD', vmad(SCRIPT, 'Blast', found.pop()))
        r.mark_dirty()
        done.append(r.edid)
    p.save(path)
    print(f'{len(done)} effects explode on every hit:', ', '.join(e.split('_Explosion_')[-1] for e in done))


if __name__ == '__main__':
    main()
