"""Scope stability on vanilla's scale (2016 report "Steady aim breaks scopes", found again triaging, 2026-10-11).

Vanilla's only use of "Mod Actor Scope Stability" (the Stabilized armour mod) multiplies stability by 1 + its
percentage. CLM's perks instead added a flat 1000 (100% / "completely stable": Aim Stabilized (100%), Widowmaker's
and Tracker's sights, Critically Hurtin', and the weapon copy) - far outside anything vanilla uses, the likely cause of
scopes "going out of control" - and Aim Stabilized (50%) multiplied by 0.5, making aim less stable. Now 50% = x1.5
and 100% = x2 (Multiply Value). In-game test (2026-10-12): x1.5 already stopped all sway (vanilla's Stabilized
lining is only about x1.01 per arm piece), so 50% was lowered to x1.25 afterwards. x1.25 still stopped all sway; the
author's own earlier testing found sway only returns below 1.0, so 50% is x0.75 (set 2026-10-12, edited raw).

Usage: python fix_scope_stability.py <plugin.esp>   (edits in place; FO4Edit must not have it open)
"""
import struct
import sys

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402

ENTRY_SCOPE_STABILITY, FN_MULTIPLY = 0x66, 3
path = sys.argv[1]
p = Plugin.load(path)
for perk in p.records('PERK'):
    subs = perk.subrecords
    changed = False
    for i, s in enumerate(subs):
        if s.sig == 'DATA' and len(s.data) == 3 and s.data[0] == ENTRY_SCOPE_STABILITY:
            epfd = next(x for x in subs[i:] if x.sig == 'EPFD')
            fn, value = s.data[1], struct.unpack('<f', epfd.data[:4])[0]
            new = 2.0 if (fn == 2 and value >= 100) else 1.5 if (fn == 3 and value == 0.5) else None
            if new is None:
                continue
            s.data = bytes([s.data[0], FN_MULTIPLY, s.data[2]])
            epfd.data = struct.pack('<f', new)
            changed = True
            print(f'{perk.edid}: {"Add" if fn == 2 else "Multiply"} {value:g} -> Multiply {new:g}')
    if changed:
        perk.mark_dirty()
p.save(path)
