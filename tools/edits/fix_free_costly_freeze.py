"""Give the five "Freeze" legendaries' costly recipes a cost (1.09 bug, found in loot-mode testing 2026-10-11).

Every costly recipe has components except these five, all freeze-themed, which cost nothing in Costly mode (and in
loot mode, whose unlocked recipes are copies of the costly ones). Each gets the components of its closest sibling:
    Untouchable (Freeze)               <- Untouchable (Fire)
    Concentratin' Intensely            <- Concentratin' Harder          (both 20 s, OP)
    Concentratin' Intensely (Brief)    <- Concentratin' (Brief)         (both 3 s)
    Slightly Freezing                  <- Chilling
    Mr. Freeze's                       <- Prometheus' Fiery             (OP elemental)
The unlocked (loot) copies get the same components; re-run tools/loot/generate.py --raw-only afterwards to add the
Legendary Core back to the OP ones.

Usage: python fix_free_costly_freeze.py <plugin.esp>   (edits in place; FO4Edit must not have it open)
"""
import sys

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402
from ack.plugin.records import Subrecord  # noqa: E402

PRE = 'co_A1ALMOMOD_Legendary_'
DONORS = {
    'Armor_PerkV_Untouchable_Freeze': 'Armor_PerkV_Untouchable_Fire',
    'Weapon_Time_Variant_Freeze_20s': 'Weapon_Time_Variant_Slow_20s',
    'Weapon_Time_Variant_Freeze_3s': 'Weapon_Time_Base_Slow_3s',
    'Weapon_SlightFreeze': 'Weapon_Chilling',
    'Weapon_MrFreezes': 'Weapon_Elements_Base_Fire',
}

path = sys.argv[1]
p = Plugin.load(path)
for target, donor in DONORS.items():
    fv = p.by_edid(PRE + donor).get('FVPA').data
    for edid in (PRE + target, PRE + target + '_Unlocked'):
        r = p.by_edid(edid)
        subs = [s for s in r.subrecords if s.sig != 'FVPA']
        subs.insert(1, Subrecord('FVPA', fv))  # components come right after EDID
        r.subrecords[:] = subs
        r.mark_dirty()
        print(f'{edid}: components of {donor} ({len(fv) // 8})')
p.save(path)
