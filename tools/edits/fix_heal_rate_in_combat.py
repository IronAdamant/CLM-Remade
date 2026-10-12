"""Health regeneration that also works in combat (found testing the PlayStation build, 2026-10-12).

Brutal, Super-Tankin', Burning Rage and Constantly Flamin' Cloaked regenerate health through heal rate
(A1ALMMGEF_Fortify_Effect_Heal_Rate, unchanged since 1.09), which does nothing in combat: vanilla's
fCombatHealthRegenRateMult is 0. Their effect now uses vanilla RegenerateHealthAbility (Jack Cabot's regeneration:
restore health per second, also in combat) with the same amount, e.g. Brutal's "50 hp regeneration".

Usage: python fix_heal_rate_in_combat.py <plugin.esp>   (edits in place; FO4Edit must not have it open)
"""
import struct
import sys

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402

HEAL_RATE = 'A1ALMMGEF_Fortify_Effect_Heal_Rate'
REGENERATE_HEALTH = 0x00102149           # Fallout4.esm RegenerateHealthAbility
path = sys.argv[1]
p = Plugin.load(path)
heal_rate = struct.pack('<I', p.by_edid(HEAL_RATE).formid)
for sig in ('ENCH', 'SPEL'):
    for r in p.records(sig):
        hits = [s for s in r.subrecords if s.sig == 'EFID' and s.data == heal_rate]
        for s in hits:
            s.data = struct.pack('<I', REGENERATE_HEALTH)
        if hits:
            r.mark_dirty()
            print(f'{r.edid}: heal rate -> RegenerateHealthAbility')
p.save(path)
