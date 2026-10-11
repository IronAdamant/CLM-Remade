"""Loot mode prototype, round 3: the unlocked Jumpy recipes check for the family's holotape item.

Every co_..._Jumpy_N_Unlocked recipe gets exactly these conditions (run on the player):
    GetItemCount(A1ALMMISC_Unlock_Jumpy) >= 1
and Jumpy (100%), which has a loose mod, shows with either:
    GetItemCount(A1ALMMISC_Unlock_Jumpy) >= 1   OR
    GetItemCount(A1ALMMISC_LooseMod_Armor_PerkV_Fortify_Jumpy_100) >= 1
The 200-300% recipes lose their copied A1ALMABALANCED check: in loot mode OP legendaries will be gated by the OP
catalyst instead (not built yet).

Usage: python loot0c_conditions.py <plugin.esp>   (edits in place; FO4Edit must not have it open)
"""
import struct
import sys

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402
from ack.plugin.records import Subrecord  # noqa: E402

FN_GET_ITEM_COUNT = 47
OP_GE, FLAG_OR = 3 << 5, 0x01


def ctda(op_flags: int, value: float, function: int, param1: int) -> Subrecord:
    # type, unused, comparison value, function, unused, param 1, param 2, run on (0 = subject), reference, param 3
    return Subrecord('CTDA', struct.pack('<B3sfH2sIIIIi', op_flags, b'\0\0\0', value, function, b'\0\0', param1, 0,
                                         0, 0, -1))


path = sys.argv[1]
p = Plugin.load(path)
holotape = p.by_edid('A1ALMMISC_Unlock_Jumpy').formid
for n in (50, 100, 150, 200, 250, 300):
    r = p.by_edid(f'co_A1ALMOMOD_Legendary_Armor_PerkV_Fortify_Jumpy_{n}_Unlocked')
    subs = r.subrecords
    first = next(i for i, s in enumerate(subs) if s.sig == 'CTDA')
    subs[:] = [s for s in subs if s.sig != 'CTDA']
    if n == 100:
        loose = p.by_edid('A1ALMMISC_LooseMod_Armor_PerkV_Fortify_Jumpy_100').formid
        new = [ctda(OP_GE | FLAG_OR, 1.0, FN_GET_ITEM_COUNT, holotape), ctda(OP_GE, 1.0, FN_GET_ITEM_COUNT, loose)]
    else:
        new = [ctda(OP_GE, 1.0, FN_GET_ITEM_COUNT, holotape)]
    subs[first:first] = new
    r.mark_dirty()
    print(f'Jumpy {n}%: {len(new)} condition(s)')
p.save(path)
