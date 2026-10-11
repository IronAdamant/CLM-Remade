"""One-time recovery: rebuild the source of the author's A1ALMMGEF_OnMeleeCLMEffect (and its twin
dlc03_Legendary_OnMeleeCLMEffect) from the shipped .pex, and prove it by recompiling and comparing disassemblies.

The 2017 script is Far Harbor's dlc03_Legendary_OnMeleeEffect logic (see source/User/A1ALMMGEF_OnMeleeEffect.psc) with
the melee check widened to 46 weapon-type keywords, in the order of the .pex property group (the source order). The
.pex line markers fix where each statement sits (RegisterForHitEvent at 58, the keyword check at 64, ... 87), so
the header is padded to put the body at the same lines.

    python tools/papyrus/rebuild_melee_clm.py --game "D:/Steam/steamapps/common/Fallout 4" [--verify]
"""
from __future__ import annotations

from verify_recovered import verify

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KEYWORDS = ('HandtoHand Unarmed Melee1H Melee2H PossiblyVerySmallClipSize Pistol Rifle Automatic HeavyGun Thrown '
            'Explosive Laser Plasma Ballistic Mine Grenade AlienBlaster Sniper CryoMine PulseMine NukaMine PlasmaMine '
            'BottlecapMine CryoGrenade NukaGrenade PlasmaGrenade PulseGrenade Molotov MissileLauncher Fatman Minigun '
            'GatlingLaser Cryolater Flamer FlareGun GammaGun JunkJet RailwayRifle Syringer Broadsider Ripper Shishkebab '
            'LaserMusket Shotgun AssaultRifle GaussRifle').split()
# The check itself tests Grenade before Mine (declarations list Mine first).
CHECK_ORDER = KEYWORDS[:KEYWORDS.index('Mine')] + ['Grenade', 'Mine'] + KEYWORDS[KEYWORDS.index('Grenade') + 1:]
BODY_START = 56  # line of "Event OnEffectStart": its RegisterForHitEvent is two lines below, at 58


def source(name: str) -> str:
    # one-line doc: the 46 keywords and 6 other declarations must end by line 55
    head = [f'Scriptname {name} extends ActiveMagicEffect',
            '{CLM (2017, recovered 2026, compiles identical to 1.09): casts SpellToCast on whoever hits the wearer with '
            'any weapon type below (or on the wearer if IsSelfCast), with a ChanceToCast roll and a Cooldown in '
            "seconds. Far Harbor's dlc03_Legendary_OnMeleeEffect logic with a wider weapon check.}"]
    head += [f'Keyword Property WeaponType{k} const auto mandatory' for k in KEYWORDS]
    head += ['Spell Property SpellToCast const auto mandatory', 'float Property ChanceToCast = 1.0 const auto',
             'bool Property IsSelfCast = false const auto', 'float Property Cooldown = 60.00 const auto',
             'int TimerID = 1 const', 'bool OnCooldown = false']
    head += [''] * (BODY_START - 1 - len(head))
    check = ' || '.join(f'akSource.haskeyword(WeaponType{k})' for k in CHECK_ORDER)
    body = ['Event OnEffectStart(Actor akTarget, Actor akCaster)',                                  # 56
            '\t; Register for a hit event on successful melee.',
            '\tRegisterForHitEvent(akTarget)',                                                       # 58
            'EndEvent', '',
            'Event OnHit(ObjectReference akTarget, ObjectReference akAggressor, Form akSource, Projectile akProjectile, '
            'bool abPowerAttack, bool abSneakAttack, bool abBashAttack, bool abHitBlocked, string apMaterial)',
            '\t; If we are not on cooldown and this is a matching weapon,',
            '\t; we are GO!',
            f'\tif (!OnCooldown && ({check}))',                                                    # 64
            '',
            '\t\tif (ChanceToCast >= Utility.randomfloat(0.0, 1.0))',                              # 66
            '',
            '\t\t\tif !IsSelfCast',                                                                # 68
            '\t\t\t\t; Onto my attacker...',
            '\t\t\t\tSpellToCast.cast(akTarget, akAggressor)',                                     # 70
            '\t\t\telse',
            '\t\t\t\t; Onto myself...',
            '\t\t\t\tSpellToCast.cast(akTarget, akTarget)',                                        # 73
            '\t\t\tendif',
            '',
            '\t\t\tOnCooldown = true',                                                             # 76
            '\t\t\tStartTimer(Cooldown, TimerID)',                                                 # 77
            '\t\tendif',
            '\tendif',
            '',
            '\t; Re-register for a hit event on melee.',
            '\tRegisterForHitEvent(akTarget)',                                                     # 82
            'EndEvent', '',
            'Event OnTimer(int aiTimerID)',
            '\tIf aiTimerID == TimerID',                                                           # 86
            '\t\tOnCooldown = false',                                                              # 87
            '\tEndIf',
            'EndEvent', '']
    return '\n'.join(head + body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    a = ap.parse_args()
    game = Path(a.game)
    base = game / 'Data' / 'Scripts' / 'Source' / 'Base'
    compiler = game / 'Papyrus Compiler' / 'PapyrusCompiler.exe'
    for name in ('A1ALMMGEF_OnMeleeCLMEffect', 'dlc03_Legendary_OnMeleeCLMEffect'):
        psc = REPO / 'source' / 'User' / f'{name}.psc'
        psc.write_text(source(name), encoding='utf8', newline='\n')
        verify(game, name)

if __name__ == '__main__':
    main()
