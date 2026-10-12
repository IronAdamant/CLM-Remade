"""Medic's: half damage to enemies, none to companions (in-game test, 2026-10-12).

Its damage perk (A1ALMPERK_Legendary_Hidden_Weapon_DecreaseDamage_50P, only Medic's carries its keyword) multiplied
Mod Weapon Attack Damage by -1.5 instead of the 0.5 its text promises, and companions were shot like anyone else.
Now: x0.5, plus a second entry x0 while the target is a player teammate (GetPlayerTeammate, function 453; Skyrim's 555 is HasLoaded3D here), so the
heal-on-hit (Restore Health 50) is all a companion gets. Recruited companions already ignore friendly hits
(FollowersScript.CompanionDataToggle calls IgnoreFriendlyHits), so they do not turn hostile.

Its heal (and Full Invulnerability's heal-on-hit spell, the same kind of effect) had the Recover flag: on an instant
Restore Health that takes the health straight back when the effect ends. Vanilla's RestoreHealthGeneric has no
Recover flag; now neither do they.

Usage: python fix_medics.py <plugin.esp>   (edits in place; FO4Edit must not have it open)
"""
import struct
import sys

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin, Subrecord  # noqa: E402

PERK = 'A1ALMPERK_Legendary_Hidden_Weapon_DecreaseDamage_50P'
OMOD = 'A1ALMOMOD_Legendary_Weapon_Medics'
HEALS = ('A1ALMMGEF_FaF_Beneficial_Target_Custom_Effect_RestoreHealth', 'A1ALMMGEF_Target_Effect_Beneficial_RestoreHealth')
FLAG_RECOVER = 0x2
FN_GET_PLAYER_TEAMMATE, TAB_TARGET = 453, 2
DESC = ('Your shots heal whoever they hit by 50 health. Your weapon deals 50% less damage, and none to your '
        'companions: patch them up in the middle of a fight.')

path = sys.argv[1]
p = Plugin.load(path)
perk = p.by_edid(PERK)
subs = perk.subrecords
if sum(s.sig == 'PRKE' for s in subs) != 1:
    raise SystemExit(f'{PERK} already has more than one entry: already fixed?')
start = next(i for i, s in enumerate(subs) if s.sig == 'PRKE')
entry = [Subrecord(s.sig, bytes(s.data)) for s in subs[start:]]
next(s for s in subs if s.sig == 'EPFD').data = struct.pack('<f', 0.5)

# companion entry: same owner condition (Medic's keyword), target is a teammate, multiply by 0
for s in entry:
    if s.sig == 'EPFB':
        s.data = struct.pack('<H', 1)
    elif s.sig == 'EPFD':
        s.data = struct.pack('<f', 0.0)
teammate = struct.pack('<B3sfH2sIIIIi', 0, b'\0\0\0', 1.0, FN_GET_PLAYER_TEAMMATE, b'\0\0', 0, 0, 0, 0, -1)
at = next(i for i, s in enumerate(entry) if s.sig == 'EPFT')
entry[at:at] = [Subrecord('PRKC', bytes([TAB_TARGET])), Subrecord('CTDA', teammate)]
subs.extend(entry)
perk.mark_dirty()

for edid in HEALS:
    m = p.by_edid(edid)
    data = m.get('DATA')
    flags = struct.unpack('<I', data.data[:4])[0] & ~FLAG_RECOVER
    data.data = struct.pack('<I', flags) + data.data[4:]
    m.mark_dirty()

omod = p.by_edid(OMOD)
omod.set('DESC', DESC.encode('utf8') + b'\0')
p.save(path)
print(f'{PERK}: x0.5, x0 on teammates; {OMOD} description updated; Recover flag off: {", ".join(HEALS)}')
