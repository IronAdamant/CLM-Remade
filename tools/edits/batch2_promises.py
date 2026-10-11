"""Batch 2, raw part: Roid Ragin's new hidden perk deals x10 damage on a 25% roll per hit.

The perk is a copy of Suppressin's x3 perk (Mod Weapon Attack Damage, Multiply Value, no conditions); this sets the
multiplier to 10 and adds a perk-owner condition GetRandomPercent < 25, checked each time the damage is worked out.

Usage: python batch2_promises.py <plugin.esp>   (after batch2_promises.txt; FO4Edit must not have it open)
"""
import struct
import sys

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402
from ack.plugin.records import Subrecord  # noqa: E402

FN_GET_RANDOM_PERCENT, OP_LT = 77, 4
path = sys.argv[1]
p = Plugin.load(path)
perk = p.by_edid('A1ALMPERK_Legendary_Hidden_Weapon_IncreaseDamage_10x_RoidRaging')
subs = perk.subrecords
if not any(s.sig == 'CTDA' for s in subs):
    at = next(i for i, s in enumerate(subs) if s.sig == 'EPFT')
    cond = struct.pack('<B3sfH2sIIIIi', OP_LT << 5, b'\0\0\0', 25.0, FN_GET_RANDOM_PERCENT, b'\0\0', 0, 0, 0, 0, -1)
    subs[at:at] = [Subrecord('PRKC', b'\0'), Subrecord('CTDA', cond)]
next(s for s in subs if s.sig == 'EPFD').data = struct.pack('<f', 10.0)
perk.mark_dirty()
p.save(path)
print('Roid Ragin perk: x10 damage when GetRandomPercent < 25')
