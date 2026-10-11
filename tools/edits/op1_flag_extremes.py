"""Flag the extreme legendaries as OP (author's decision, 2026-10-11).

These were not flagged OP but are as strong as OP legendaries (docs/LOOT_PLAN.md): Savage family, all eight Havocs,
Performance Center, Burning Hellish, Face Bustin', One Punch Man's, Searing. OP in CLM means both recipes (costly and
FREE) also require GetGlobalValue(A1ALMABALANCED) == 1, so "Balanced only" hides them; this appends that condition
the same way the author's OP recipes have it (last condition, equal to 1).

Usage: python op1_flag_extremes.py <plugin.esp>   (edits in place; FO4Edit must not have it open)
"""
import struct
import sys

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402
from ack.plugin.records import Subrecord  # noqa: E402

FN_GET_GLOBAL_VALUE = 74
LEGENDARIES = [
    'A1ALMOMOD_Legendary_Weapon_Recoilless_Variant_Savage',
    'A1ALMOMOD_Legendary_Weapon_Recoilless_Variant_DeathlySilenced',
    'A1ALMOMOD_Legendary_Weapon_Recoilless_Variant_MurderouslySilenced',
    'Recoilless_Limited_',            # Savage (Limited), Silently Savage (Limited), Caged Savage
    'A1ALMOMOD_Legendary_Weapon_Havoc_',
    'A1ALMOMOD_Legendary_Weapon_Custom_PerformanceCenter',
    'A1ALMOMOD_Legendary_Weapon_BurningHellish',
    'A1ALMOMOD_Legendary_Weapon_FaceBusting',
    'A1ALMOMOD_Legendary_Armor_OnePunchMans',
    'A1ALMOMOD_Legendary_Weapon_Searing',
]

path = sys.argv[1]
p = Plugin.load(path)
balanced = p.by_edid('A1ALMABALANCED').formid
omods = {r.formid: r for r in p.records('OMOD') if any(
    r.edid == x or (x.endswith('_') and x in r.edid) or r.edid.startswith(x + '_') for x in LEGENDARIES)}
assert len(omods) == 19, sorted(r.edid for r in omods.values())  # 3 + 3 limited + 8 Havoc + 5 singles
done = 0
for c in p.records('COBJ'):
    cnam = c.get('CNAM')
    if not cnam or struct.unpack('<I', cnam.data)[0] not in omods or c.edid.endswith('_Unlocked'):
        continue
    conds = [s for s in c.subrecords if s.sig == 'CTDA']
    if any(struct.unpack_from('<HxxI', s.data, 8) == (FN_GET_GLOBAL_VALUE, balanced) for s in conds):
        continue  # already OP
    last = max(i for i, s in enumerate(c.subrecords) if s.sig == 'CTDA')
    c.subrecords.insert(last + 1, Subrecord('CTDA', struct.pack('<B3sfH2sIIIIi', 0, b'\0\0\0', 1.0, FN_GET_GLOBAL_VALUE,
                                                                b'\0\0', balanced, 0, 0, 0, -1)))
    c.mark_dirty()
    done += 1
    print('OP:', c.edid)
print(f'{done} recipes flagged OP for {len(omods)} legendaries')
p.save(path)
