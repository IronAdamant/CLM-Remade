"""Merge the four DLC add-ons back into the main plugin (author's decision, 2026-10-12).

    python tools/addons/merge_into_main.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Most players own every DLC by now, and one plugin is easier to maintain than five. The main plugin gains the four
DLC masters (Automatron, Far Harbor, Contraptions Workshop, Nuka-World) and every add-on record except each add-on's
own loot plumbing (A1ALM<DLC>LL_* drop lists, A1ALM<DLC>QUST_Loot, A1ALM<DLC>PERK_Loot): tools/loot/generate.py
rebuilds the main plugin's drop lists with the merged legendaries in them.

Records that were in the main plugin before tools/xedit/move_to_addon.pas moved them (all from 1.09) get their old
object IDs back, so a 1.09 save keeps those legendaries; records made since get new IDs. Works on the game's Data
folder; all five plugins are saved first to work/merge_backup, the add-ons are put back afterwards (FO4Edit edits them
in memory) and the main plugin too if FO4Edit reports an error. Afterwards move the add-ons out of Data.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAIN = 'Custom Legendary Modifications Remade.esp'
ADDONS = {'CLM - Automatron.esp': 'Automatron', 'CLM - Far Harbor.esp': 'FarHarbor',
          'CLM - Nuka-World.esp': 'NukaWorld', 'CLM - Contraptions.esp': 'Contraptions'}
DLC_MASTERS = ['DLCRobot.esm', 'DLCCoast.esm', 'DLCworkshop02.esm', 'DLCNukaWorld.esm']
BEFORE_MOVES = ['ad1db92^', '155eb8d^']     # the main plugin before each move_to_addon.pas run


def old_ids(Plugin) -> dict[str, int]:
    """editor ID -> object ID in the main plugin before the moves (1.09's first, then later records)."""
    first = subprocess.run(['git', '-C', str(REPO), 'rev-list', '--max-parents=0', 'HEAD'],
                           capture_output=True, text=True, check=True).stdout.split()[0]
    ids: dict[str, int] = {}
    with tempfile.TemporaryDirectory() as tmp:
        for commit in [first, *BEFORE_MOVES]:
            path = Path(tmp) / f'{len(ids)}.esp'
            path.write_bytes(subprocess.run(['git', '-C', str(REPO), 'show', f'{commit}:data/{MAIN}'],
                                            capture_output=True, check=True).stdout)
            p = Plugin.load(path)
            for r in p.records():
                if p.is_own(r.formid) and r.edid:
                    ids.setdefault(r.edid, r.formid & 0xFFFFFF)
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin

    main_p = Plugin.load(data / MAIN)
    if set(DLC_MASTERS) <= set(main_p.masters):
        raise SystemExit(f'{MAIN} already has the DLC masters: already merged?')
    used = {r.formid & 0xFFFFFF for r in main_p.records() if main_p.is_own(r.formid)}
    ids = old_ids(Plugin)
    lines, restored = [], 0
    for name, tag in ADDONS.items():
        p = Plugin.load(data / name)
        for r in p.records():
            if not p.is_own(r.formid) or re.match(f'A1ALM{tag}(LL|QUST|PERK)_', r.edid):
                continue
            oid = ids.get(r.edid)
            if oid is not None and oid in used:
                raise SystemExit(f'{r.edid}: its old ID {oid:06X} is taken in {MAIN}')
            lines.append(f'{r.edid}\t{oid:06X}' if oid is not None else f'{r.edid}\t')
            restored += oid is not None
    records = REPO / 'work' / 'merge_records.txt'
    records.parent.mkdir(exist_ok=True)
    records.write_text('\n'.join(lines) + '\n', encoding='utf8')
    print(f'{len(lines)} records to merge, {restored} with their old IDs')

    backup = REPO / 'work' / 'merge_backup'
    backup.mkdir(exist_ok=True)
    for name in [MAIN, *ADDONS]:
        shutil.copy2(data / name, backup / name)
    cmd = [sys.executable, '-m', 'ack', 'xedit', 'run', str(REPO / 'tools' / 'xedit' / 'merge_addons.pas'), MAIN,
           '--save', '--timeout', '1800', '--param', f'RECORDS={records}', '--param', f'MASTERS={",".join(DLC_MASTERS)}']
    for name in ADDONS:
        cmd += ['--also-load', name]
    r = subprocess.run(cmd, cwd=ack, capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    run = sorted((ack / 'private' / 'runs').glob('*-merge_addons'))[-1]
    result = (run / 'result.txt').read_text(encoding='utf8') if (run / 'result.txt').exists() else 'no result'
    print(result)
    for name in ADDONS:
        shutil.copy2(backup / name, data / name)
    if not result.startswith('0 errors'):
        shutil.copy2(backup / MAIN, data / MAIN)
        raise SystemExit(f'errors: {MAIN} restored from {backup}')


if __name__ == '__main__':
    main()
