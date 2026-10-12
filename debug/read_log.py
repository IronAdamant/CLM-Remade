"""Print the CLM debug recorder's log with form IDs translated to editor IDs and names.

    python debug/read_log.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4" [--old N]

Reads Documents/My Games/Fallout4/Logs/Script/User/CLM.0.log (--old 1 for the session before, and so on).
Papyrus prints forms like "[MiscObject < (084AC2BC)>]"; the load-order byte varies, so forms are matched by their
object ID among the records of the main plugin and its add-ons (and Fallout4.esm for 00xxxxxx).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LOG_DIR = Path.home() / 'Documents' / 'My Games' / 'Fallout4' / 'Logs' / 'Script' / 'User'
PLUGINS = ['Custom Legendary Modifications Remade.esp']   # the DLC add-ons were merged into it (2026-10-12)
FORM = re.compile(r'\[(\w+) <[^>]*\(([0-9A-Fa-f]{8})\)>\]')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    ap.add_argument('--old', type=int, default=0, help='0 = latest session, 1 = the one before, ...')
    a = ap.parse_args()
    sys.path.insert(0, a.ack)
    from ack.plugin import Plugin

    data = Path(a.game) / 'Data'
    names: dict[tuple[str, int], str] = {}   # (plugin kind, object id) -> label
    for plugin in PLUGINS:
        if not (data / plugin).exists():
            continue
        p = Plugin.load(data / plugin)
        for r in p.records():
            if p.is_own(r.formid):
                full = r.get('FULL')
                label = r.edid + (f' "{full.zstring}"' if full and full.zstring else '')
                # ESL add-ons: 12-bit object IDs; regular plugins: 24-bit
                names.setdefault(('esl' if plugin != PLUGINS[0] else 'esp', r.formid & 0xFFFFFF), label)

    def label(m: re.Match) -> str:
        fid = int(m.group(2), 16)
        found = names.get(('esp', fid & 0xFFFFFF)) if fid >> 24 != 0xFE else names.get(('esl', fid & 0xFFF))
        return f'{found} [{m.group(1)} {m.group(2)}]' if found else m.group(0)

    log = LOG_DIR / f'CLM.{a.old}.log'
    if not log.exists():
        raise SystemExit(f'no log at {log} - is Papyrus logging on (python -m ack papyrus-log on) and the recorder '
                         f'plugin enabled?')
    for line in log.read_text(encoding='utf8', errors='replace').splitlines():
        print(FORM.sub(label, line))


if __name__ == '__main__':
    main()
