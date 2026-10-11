"""Delete 1.09's dead-end records: unreferenced leftovers the author chose not to finish (2026-10-11), repeated until
no new orphans appear (deleting a draft legendary orphans the enchantment only it used, and so on).

    python tools/edits/cleanup_leftovers.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4" [--dry-run]

"Unreferenced" = no record in the main plugin or any add-on contains its form ID (scripts' properties included,
since VMAD is part of the record data). Never deleted: record types the game uses without a reference (recipes,
terminals, quests, globals, keywords, NPCs, notes) and the laser add-on nodes (ADDN: meshes use their index, not a
reference). Writes tools/edits/cleanup_leftovers.log with everything deleted.
"""
from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = 'Custom Legendary Modifications Remade.esp'
ADDONS = ['CLM - Automatron.esp', 'CLM - Far Harbor.esp', 'CLM - Nuka-World.esp', 'CLM - Contraptions.esp']
KEEP_SIGS = {'COBJ', 'TERM', 'QUST', 'NOTE', 'GLOB', 'KYWD', 'NPC_', 'ADDN'}


def orphans(data: Path) -> list[tuple[str, str]]:
    from ack.plugin import Plugin
    main = Plugin.load(data / MAIN)
    own = {r.formid: r for r in main.records() if main.is_own(r.formid)}
    used = set()
    for p in [main] + [Plugin.load(data / a) for a in ADDONS if (data / a).exists()]:
        idx = len(p.masters) if p is main else p.masters.index(MAIN)
        for r in p.records():
            d = r.data()
            for i in range(len(d) - 3):
                v = struct.unpack_from('<I', d, i)[0]
                if v >> 24 == idx:
                    k = (v & 0xFFFFFF) | (len(main.masters) << 24)
                    if k in own and k != r.formid:
                        used.add(k)
    return sorted((r.sig, r.edid) for f, r in own.items() if f not in used and r.sig not in KEEP_SIGS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    sys.path.insert(0, a.ack)
    data = Path(a.game) / 'Data'
    log = []
    for round_ in range(1, 10):
        found = orphans(data)
        if not found:
            break
        print(f'round {round_}: {len(found)} unreferenced')
        for sig, edid in found:
            print(f'   {sig} {edid}')
        log += [f'round {round_}: {sig} {edid}' for sig, edid in found]
        if a.dry_run:
            break
        edits = HERE / 'cleanup_round.txt'
        edits.write_text('\n'.join(f'rec.delete | {edid}' for _, edid in found) + '\n', encoding='utf8')
        r = subprocess.run([sys.executable, '-m', 'ack', 'xedit', 'run', 'apply_edits', MAIN, '--save', '--timeout',
                            '300', '--param', f'EDITS={edits}'], cwd=a.ack, capture_output=True, text=True)
        run = sorted((Path(a.ack) / 'private' / 'runs').glob('*-apply_edits'))[-1]
        first = (run / 'result.txt').read_text(encoding='utf8').splitlines()[0]
        print('  ', first)
        edits.unlink()
        if ' 0 errors' not in first:
            raise SystemExit(r.stdout + r.stderr)
    if not a.dry_run:
        (HERE / 'cleanup_leftovers.log').write_text('\n'.join(log) + '\n', encoding='utf8')
    print(f'{len(log)} records deleted' if not a.dry_run else 'dry run')


if __name__ == '__main__':
    main()
