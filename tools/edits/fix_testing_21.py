"""2.1: fixes from the author's in-game testing (2026-10-15).

    python tools/edits/fix_testing_21.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

- Energizin': the Absorb archetype gave no Action Points. It now runs the base game's own "refill AP" effect (vanilla
  ModLegendaryOnCritHitRefillAPScript, which PlayStation keeps) on 5% of hits: a full refill, as vanilla's legendary
  does on critical hits. Papyrus cannot be told an amount for it, so "+3 per hit" is not possible without a CLM script.
- Rallyin' and Disheartenin' (and Shrinkin', which uses Disheartenin's effect): Peak Value Modifier did nothing in
  game. They are Value Modifiers with the Recover flag now (the value comes back when the effect ends), as
  God Creator's working +1000 resistance is.
- Necromancer's: the risen joined PlayerAllyFaction, which raiders and the like are not hostile to, so nobody fought.
  They now join PlayerFaction and turn aggressive (A1ALMMGEF_RisenEffect).
- Singularity: a negative explosion force does not pull. A1ALMMGEF_ImplodeEffect sets off the blast and pushes each
  nearby enemy from a marker beyond it, towards the target (PC and Xbox; PlayStation keeps the kill-only blast).
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
GET_RANDOM, LT = 77, 4
RECOVER = 1 << 1
PLAYER_FACTION, AGGRESSION, XMARKER = 0x1C21C, 0x2BC, 0x3B
ACTOR_TYPES = [0x13794, 0x13795, 0x13798, 0x2CB73, 0x6D7B6, 0xEAFB7, 0xB2BF3, 0x2CB71, 0x10C3CE, 0x317AA]
ENERGIZE = 'A1ALMEnch_FaF_Contact_Target_Hostile_Energizing'
# effect -> its actor value (changing the archetype clears it; written back in step 2)
VALUE_MODIFIERS = {'A1ALMMGEF_Aura_Rally_DamageResist': 0x2E3, 'A1ALMMGEF_Aura_Rally_EnergyResist': 0x2EB,
                   'A1ALMMGEF_Aura_Rally_AttackDamageMult': 0x357, 'A1ALMMGEF_Target_Effect_Hostile_Dishearten': 0x357}
EDITS = [
    f'field.set | {ENERGIZE} | Effects\\[0]\\EFID | @ModLegendaryOnCritHitEffect_RefillAP',
    f'effect.magnitude | {ENERGIZE} | 0 | 0',
    f"text.set | {OM}Weapon_Energizing | DESC | Each hit has a 5% chance to refill your Action Points completely (as the "
    "base game's legendary does on critical hits).",
    *[f'field.set | {m} | Magic Effect Data\\DATA\\Archetype | Value Modifier' for m in VALUE_MODIFIERS],
    'field.set | A1ALMEXP_Singularity | DATA\\Force | 0',
    f'text.set | {OM}Weapon_Singularity | DESC | Hits implode: enemies within 7 metres are pulled towards the target and '
    'knocked down, and the implosion deals 60 damage. (The pull is PC and Xbox only.)',
]


def write_raw(data: Path, ack: Path) -> None:
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord

    p = Plugin.load(data / MAIN)
    fid = lambda e: e if isinstance(e, int) else p.by_edid(e).formid

    def wstr(s):
        return struct.pack('<H', len(s)) + s.encode('ascii')

    def vmad(script, props):
        out = struct.pack('<hhH', 6, 2, 1) + wstr(script) + b'\0' + struct.pack('<H', len(props))
        for name, kind, value in props:
            out += wstr(name)
            if kind == 'form':
                out += b'\x01\x01' + struct.pack('<HhI', 0, -1, fid(value))
            elif kind == 'objects':
                out += b'\x0b\x01' + struct.pack('<I', len(value)) + b''.join(struct.pack('<HhI', 0, -1, v) for v in value)
            elif kind == 'float':
                out += b'\x04\x01' + struct.pack('<f', value)
        return out

    # Energizin': one hit in twenty
    r = p.by_edid(ENERGIZE)
    out = [s for s in r.subrecords if s.sig != 'CTDA']
    at = next(i for i, s in enumerate(out) if s.sig == 'EFIT') + 1
    out[at:at] = [Subrecord('CTDA', struct.pack('<B3sfH2sIIIIi', LT << 5, b'\0\0\0', 5.0, GET_RANDOM, b'\0\0', 0, 0, 0, 0, -1))]
    r.subrecords[:] = out
    r.mark_dirty()
    for m, av in VALUE_MODIFIERS.items():
        r = p.by_edid(m)
        d = bytearray(r.get('DATA').data)
        struct.pack_into('<I', d, 0, struct.unpack_from('<I', d, 0)[0] | RECOVER)
        assert struct.unpack_from('<I', d, 64)[0] == 0, m           # archetype 0 = Value Modifier
        struct.pack_into('<I', d, 68, av)
        r.set('DATA', bytes(d))
        r.mark_dirty()
    r = p.by_edid('A1ALMMGEF_Target_Effect_Risen')
    r.set('VMAD', vmad('A1ALMMGEF_RisenEffect', [('AllyFaction', 'form', PLAYER_FACTION), ('Aggression', 'form', AGGRESSION)]))
    r.mark_dirty()
    r = p.by_edid('A1ALMMGEF_Target_Effect_Hostile_Explosion_Singularity')
    r.set('VMAD', vmad('A1ALMMGEF_ImplodeEffect', [('Blast', 'form', 'A1ALMEXP_Singularity'), ('ActorTypes', 'objects', ACTOR_TYPES),
                                                  ('Marker', 'form', XMARKER), ('Radius', 'float', 500.0),
                                                  ('Force', 'float', 3.0)]))
    r.mark_dirty()
    p.save(data / MAIN)
    print('Energizin\', Rallyin\', Disheartenin\', Necromancer\'s and Singularity fixed')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    path = HERE / 'fix_testing_21.txt'
    path.write_text('# Generated by fix_testing_21.py - edit that, not this file.\n' + '\n'.join(EDITS) + '\n', encoding='utf8')
    r = subprocess.run([sys.executable, '-m', 'ack', 'xedit', 'run', 'apply_edits', MAIN, '--save', '--timeout', '900',
                        '--param', f'EDITS={path}'], cwd=ack, capture_output=True, text=True)
    result = (sorted((ack / 'private' / 'runs').glob('*-apply_edits'))[-1] / 'result.txt').read_text(encoding='utf8')
    print(result.splitlines()[0])
    if ' 0 errors' not in result.splitlines()[0]:
        raise SystemExit('\n'.join(l for l in result.splitlines() if l.startswith('ERROR')) + r.stderr)
    write_raw(data, ack)


if __name__ == '__main__':
    main()
