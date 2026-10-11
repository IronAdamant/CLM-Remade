"""Chance-based effects that never fired (found triaging the Nexus complaints, 2026-10-11).

GetRandomPercent returns a whole number from 0 to 99. 1.09 tested it with "== fraction" (== 0.1 for 10%, == 0.25 for
25%), which is never true, or "== 40" for 40%, which is true 1% of the time. So Burning never set anything on fire,
Forcible never staggered, Lucky Drawin' never one-shot, Roid Ragin', Suppressin', Slightly Freezing, Angry Nerd's
and others never (or almost never) triggered their chances. Every "GetRandomPercent ==" condition becomes
"GetRandomPercent < percent" (fractions times 100), keeping its OR flag. Conditions already using <, <=, >, >= are
left alone. Runs on the main plugin and every add-on.

Usage: python fix_random_chances.py <Data folder>   (edits in place; FO4Edit must not have the plugins open)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402

PLUGINS = ['Custom Legendary Modifications Remade.esp', 'CLM - Automatron.esp', 'CLM - Far Harbor.esp',
           'CLM - Nuka-World.esp', 'CLM - Contraptions.esp']
FN_GET_RANDOM_PERCENT = 77
OP_EQ, OP_LT = 0, 4

data = Path(sys.argv[1])
for name in PLUGINS:
    if not (data / name).exists():
        continue
    p = Plugin.load(data / name)
    changed = 0
    for r in p.records():
        if not p.is_own(r.formid):
            continue
        dirty = False
        for s in r.subrecords:
            if s.sig != 'CTDA' or struct.unpack_from('<H', s.data, 8)[0] != FN_GET_RANDOM_PERCENT:
                continue
            t = s.data[0]
            if t >> 5 != OP_EQ:
                continue
            value = struct.unpack_from('<f', s.data, 4)[0]
            percent = round(value * 100, 4) if value < 1 else value
            d = bytearray(s.data)
            d[0] = (OP_LT << 5) | (t & 0x1F)
            struct.pack_into('<f', d, 4, percent)
            s.data = bytes(d)
            dirty = True
            changed += 1
            print(f'{name}: {r.edid}: GetRandomPercent == {value:g} -> < {percent:g}')
        if dirty:
            r.mark_dirty()
    if changed:
        p.save(data / name)
    print(f'{name}: {changed} conditions fixed')
