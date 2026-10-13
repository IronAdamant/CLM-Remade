"""2.1: Fisto's tiers no longer multiply (docs/PLAN_2.1.md 2, author's decision 2026-10-13).

    python tools/edits/fix_fistos_stacking.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Each Fisto's tier is its own hidden perk (A1ALMPERK_Legendary_Hidden_Weapon_IncreaseDamage_<N>P) with one
"Mod Weapon Attack Damage" x(1 + N/100) entry and no conditions. A perk applies once however many pieces give it,
but different tiers are different perks, so Fisto's (20%) to (150%) on five pieces multiplied to about x11. Now each
tier's entry also requires "does not have any higher tier", so only the best piece counts. Records only. The 25%
perk is shared with the four Factional Damaging armours; they keep working (one perk, as before).

Works on the main plugin in the game's Data folder. Safe to re-run: earlier conditions are replaced.
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

MAIN = 'Custom Legendary Modifications Remade.esp'
TIER = re.compile(r'A1ALMPERK_Legendary_Hidden_Weapon_IncreaseDamage_(\d+)P$')
FN_HAS_PERK, OP_EQ = 448, 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    sys.path.insert(0, a.ack)
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord

    path = Path(a.game) / 'Data' / MAIN
    p = Plugin.load(path)
    tiers = sorted(((int(m.group(1)), r) for r in p.records('PERK') if (m := TIER.match(r.edid or ''))),
                   key=lambda t: t[0])
    for pct, perk in tiers:
        higher = [r.formid for n, r in tiers if n > pct]
        subs = [s for s in perk.subrecords if s.sig not in ('PRKC', 'CTDA')]
        at = next(i for i, s in enumerate(subs) if s.sig == 'EPFT')
        conds = [Subrecord('CTDA', struct.pack('<B3sfH2sIIIIi', OP_EQ << 5, b'\0\0\0', 0.0, FN_HAS_PERK, b'\0\0',
                                               f, 0, 0, 0, -1)) for f in higher]
        perk.subrecords[:] = subs[:at] + ([Subrecord('PRKC', b'\0')] + conds if conds else []) + subs[at:]
        perk.mark_dirty()
        print(f'Fisto\'s ({pct}%): counts unless one of {len(higher)} higher tiers is worn')
    p.save(path)


if __name__ == '__main__':
    main()
