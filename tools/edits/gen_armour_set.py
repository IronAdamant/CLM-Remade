"""2.1's own armour legendaries (docs/PLAN_2.1.md 5): effects that are new to Fallout 4, designed against the base
game's legendaries (read from Fallout4.esm and the DLC, 2026-10-13).

    python tools/edits/gen_armour_set.py --ack "D:/Coding Projects/AgentCreationKit" --game "D:/Steam/steamapps/common/Fallout 4"

Works on the main plugin in the game's Data folder (FO4Edit must not have it open), in two steps:
1. tools/edits/armour_set.txt (apply_edits): every record is a copy of a working one. Legendaries copy Ballistic
   Protection (Basic) and its recipes (balanced; the OP one copies Brutal's), enchantments copy its enchantment,
   perks copy Marathon Runnin''s chain (hidden perk -> "Perk to Apply" magic effect), auras copy Nuka-World's
   Overboss tesla coil (a cloak effect and the spell it puts on everyone nearby).
2. What apply_edits cannot write, written directly: conditions on enchantment effects, perk entry points, the
   abilities of the scripted ones, script properties, aura flags and conditions.

Records only (all platforms), except Phoenix, Bloodthirsty, Momentum and Static Charged, which use the scripts
A1ALMMGEF_OnHitArmourEffect / A1ALMMGEF_OnKillArmourEffect (PC and Xbox; the PlayStation build notes it). Those run
from a perk's ability, and every perk-based effect counts once however many pieces carry it; value effects
(resistances, SPECIAL, speed, healing) add up per piece, as the base game's do (Sentinel's: 15% per piece).

Condition function and entry point IDs were read from the official masters with FO4Edit (name and number side by
side). Time of day uses GameHour as vanilla Solar Powered does; darkness uses vanilla's own threshold (PlayerPerk:
GetLightLevel < 50).
"""
from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = 'Custom Legendary Modifications Remade.esp'
OM = 'A1ALMOMOD_Legendary_'
CO = 'co_A1ALMOMOD_Legendary_'
PROP1 = 'DATA\\Properties\\[0]\\Value 1'
TEMPLATE = 'Armor_BallisticProtection_50P'          # balanced, plain, one Enchantments property
OP_RECIPES = 'Armor_Brutal'                        # OP, plain
ENCH_TEMPLATE = 'A1ALMEnch_Constant_Effect_Custom_Effect_BallisticProtection_50P'
PERK_TEMPLATE = 'A1ALMPERK_Legendary_Hidden_Armor_SprintReduceAPCost_75P'
PERK_MGEF_TEMPLATE = 'A1ALMMGEF_Constant_Effect_Custom_Effect_Perk_SprintReduceAPCost_75P'
SCRIPT_MGEF_TEMPLATE = 'A1ALMMGEF_Constant_Effect_OnMeleeHits_Spook'
ABILITY_TEMPLATE = 'AbPerkSolarPowered'
CLOAK_TEMPLATE = 'DLC04pa_mod_Lining_FieldGen_Radiation_CloakEffect'
AURA_SPELL_TEMPLATE = 'DLC04_mod_Lining_FieldGen_EMP_Spell'
AURA_MGEF_TEMPLATE = 'DLC04mod_Lining_FieldGen_EMP_MagicEffect'

# Fallout4.esm form IDs
PLAYER_REF, GAME_HOUR, RADS, HEALTH = 0x14, 0x38, 0x2E1, 0x2D4
ARMOR_TYPE_POWER, RADSTORM, GENERIC_BRAWL = 0x4D8A1, 0x1C3D5E, 0xAC06B
LL_SCROUNGER, LL_FORTUNE_FINDER = 0x1081B9, 0x585A6      # vanilla Scrounger / Fortune Finder drop lists

# condition functions
GET_VALUE, IS_MOVING, IS_RAINING, GET_GLOBAL, GET_IS_WEATHER = 14, 25, 62, 74, 149
IS_SNEAKING, IN_COMBAT, IS_INTERIOR, LEVEL_MINUS_PC = 286, 289, 300, 578
GET_LIGHT, IS_HOSTILE, WORN_HAS_KEYWORD, OWNED_WORKSHOP, IN_WATER = 711, 719, 682, 788, 801
GET_IN_FACTION = 71
EQ, NE, GT, GE, LT, LE = range(6)
OR = 1

# perk entry points: (id, condition tabs); functions
INCOMING_DAMAGE = (36, 3)        # tabs: owner, attacker, attacker's weapon
WEAPON_DAMAGE = (35, 3)          # tabs: owner, weapon, target
INCOMING_STAGGER = (33, 2)
INCOMING_LIMB = (4, 3)
SCOPE_STABILITY = (102, 1)
DETECTION_LIGHT = (47, 2)
LEVELED_LIST_ON_DEATH = (9, 2)   # CLM's own loot perk uses it (function 8, data type LVLI)
SET, ADD, MUL, ADD_LEVELED_LIST = 1, 2, 3, 8


def C(fn, op=EQ, value=1.0, param=0, flags=0):
    return (fn, op, value, param, flags)


NIGHT = [C(GET_GLOBAL, GE, 20, GAME_HOUR, OR), C(GET_GLOBAL, LT, 6, GAME_HOUR)]
DAY_OUTDOORS = [C(IS_INTERIOR, EQ, 0), C(GET_GLOBAL, GE, 6, GAME_HOUR), C(GET_GLOBAL, LT, 20, GAME_HOUR),
                C(IS_RAINING, EQ, 0)]
STORM = [C(IS_RAINING, EQ, 1, 0, OR), C(GET_IS_WEATHER, EQ, 1, RADSTORM)]
DARK = [C(GET_LIGHT, LT, 50)]
IN_WATER_ = [C(IN_WATER, EQ, 1)]
DUG_IN = [C(IS_SNEAKING, EQ, 1), C(IS_MOVING, EQ, 0)]
HOME = [C(OWNED_WORKSHOP, EQ, 1)]
POWER_ARMOUR = [C(WORN_HAS_KEYWORD, EQ, 1, ARMOR_TYPE_POWER)]

MG = 'A1ALMMGEF_Fortify_'
DR, ER, RAD_RES = MG + 'Resistance_Damage', MG + 'Resistance_Energy', MG + 'Resistance_Radiation_Exposure'
STR, PER, CHA, AGI, LCK = (MG + 'SPECIAL_' + s for s in ('Strength', 'Perception', 'Charisma', 'Agility', 'Luck'))
SPEED, HEAL, UNRAD = MG + 'Effect_Movement_Speed_Mult', MG + 'Effect_Health_Regen', MG + 'Effect_RestoreRads'
BATTERY, AP_REGEN = MG + 'Effect_Power_Armor_Battery_Regen', MG + 'Effect_Action_Point_Regen'

# key -> in-game name, description, value effects [(magic effect, magnitude, conditions)], perk entries
#        [(entry point, function, value, {tab: conditions})], options
LEGENDARIES = {
    # --- Surroundings: the time, place and weather decide ---
    'NightOwls': ("CLM: Night Owl's",
                  'From 8pm to 6am: +1 Perception, +1 Agility and +10 damage and energy resistance.',
                  [(PER, 1, NIGHT), (AGI, 1, NIGHT), (DR, 10, NIGHT), (ER, 10, NIGHT)], [], {}),
    'SunKissed': ('CLM: Sun-Kissed',
                  'Outdoors from 6am to 8pm, when it is not raining: you heal 1 health and lose 1 rad every second.',
                  [(HEAL, 1, DAY_OUTDOORS), (UNRAD, 1, DAY_OUTDOORS)], [], {}),
    'StormChasing': ("CLM: Storm Chasin'",
                     'In rain or a radstorm: +20 energy and radiation resistance, and you move 5% faster.',
                     [(ER, 20, STORM), (RAD_RES, 20, STORM), (SPEED, 5, STORM)], [], {}),
    'ShadowDwelling': ("CLM: Shadow Dwellin'",
                       'In the dark: +1 Agility and +1 Luck, and enemies find it 25% harder to see you (that part '
                       'counts once, however many pieces have it).',
                       [(AGI, 1, DARK), (LCK, 1, DARK)],
                       [(DETECTION_LIGHT, MUL, 0.75, {0: DARK})], {}),
    'Amphibious': ('CLM: Amphibious',
                   'You can breathe underwater. In water you move 10% faster and take 25% less damage (the damage '
                   'part counts once, however many pieces have it).',
                   [(SPEED, 10, IN_WATER_)], [(INCOMING_DAMAGE, MUL, 0.75, {0: IN_WATER_})],
                   {'water_breathing': True}),
    'Entrenched': ('CLM: Entrenched',
                   'Crouched and not moving: +25 damage and energy resistance, and your aim holds steady (the aim '
                   'part counts once, however many pieces have it).',
                   [(DR, 25, DUG_IN), (ER, 25, DUG_IN)], [(SCOPE_STABILITY, MUL, 1.25, {0: DUG_IN})], {}),
    'HomeTurf': ('CLM: Home Turf',
                 'In a settlement you own: +25 damage and energy resistance and +1 Charisma.',
                 [(DR, 25, HOME), (ER, 25, HOME), (CHA, 1, HOME)], [], {}),
    # --- Grit: trade-offs and long odds ---
    'Underdogs': ("CLM: Underdog's",
                  'Enemies of a higher level than you deal 25% less damage to you and take 25% more from you. '
                  'Counts once, however many pieces have it.',
                  [], [(INCOMING_DAMAGE, MUL, 0.75, {1: [C(LEVEL_MINUS_PC, GT, 0)]}),
                       (WEAPON_DAMAGE, MUL, 1.25, {2: [C(LEVEL_MINUS_PC, GT, 0)]})], {}),
    'GlassCannon': ('CLM: Glass Cannon',
                    'You deal 25% more damage, and take 25% more. Counts once, however many pieces have it.',
                    [], [(WEAPON_DAMAGE, MUL, 1.25, {}), (INCOMING_DAMAGE, MUL, 1.25, {})], {}),
    'Ironclad': ('CLM: Ironclad',
                 'You cannot be staggered and take 50% less limb damage (counts once), but every piece with it '
                 'makes you 5% slower.',
                 [(SPEED, -5, [])], [(INCOMING_STAGGER, MUL, 0.0, {}), (INCOMING_LIMB, MUL, 0.5, {})], {}),
    'GlowingHeart': ('CLM: Glowing Heart',
                     'The more rads you carry, the tougher you are: +5 damage and energy resistance for every 100 '
                     'rads, up to +30 at 600 rads.',
                     [(av, 5, [C(GET_VALUE, GE, 100 * n, RADS)]) for n in range(1, 7) for av in (DR, ER)], [], {}),
    'Overcharged': ('CLM: Overcharged',
                    'In power armour: +2 Strength and +25 damage and energy resistance, but your fusion core drains '
                    'faster.',
                    [(STR, 2, POWER_ARMOUR), (DR, 25, POWER_ARMOUR), (ER, 25, POWER_ARMOUR),
                     (BATTERY, -0.2, POWER_ARMOUR)], [], {}),
    # --- Scavenging ---
    'Scavengers': ("CLM: Scavenger's",
                   'Enemies you kill carry extra ammo and a few extra caps (as the Scrounger and Fortune Finder '
                   'perks find). Counts once, however many pieces have it.',
                   [], [(LEVELED_LIST_ON_DEATH, ADD_LEVELED_LIST, LL_SCROUNGER, {}),
                        (LEVELED_LIST_ON_DEATH, ADD_LEVELED_LIST, LL_FORTUNE_FINDER, {})], {}),
}

# Radiatin' (auras): variant -> name, description, aura magic effect (made below), magnitude per second, radius, OP
AURAS = {
    'Fire': ("CLM: Radiatin' (Fire)", 'Enemies near you burn: 5 fire damage per second.', 'Fire', 5, 10, False),
    'Shock': ("CLM: Radiatin' (Shock)", 'Enemies near you are shocked: 5 electrical damage per second.', 'Shock', 5,
              10, False),
    'Rads': ("CLM: Radiatin' (Rads)", 'Enemies near you are irradiated: 10 rads per second.', 'Rads', 10, 10, False),
    'Cryo': ("CLM: Radiatin' (Cryo)", 'Enemies near you are chilled and move 30% slower.', 'Slow', 30, 10, False),
    'Healing': ("CLM: Radiatin' (Healing)", 'Your companions and anyone else not hostile to you heal 3 health per '
                'second while they fight near you.', 'Heal', 3, 10, False),
    'Inferno': ("CLM: Radiatin' (Inferno)", 'Enemies anywhere around you burn: 30 fire damage per second.', 'Fire',
                30, 20, True),
}
# aura magic effects: key -> (name, damage type or actor value, hit shader, hostile)
AURA_EFFECTS = {
    'Fire': ('CLM: Aura [Fire]', '@dtFire', '@FireHitFXS', True),
    'Shock': ('CLM: Aura [Shock]', '@dtElectrical', None, True),
    'Rads': ('CLM: Aura [Rads]', '@dtRadiationExposure', None, True),
    'Slow': ('CLM: Aura [Cryo slow]', 'SpeedMult', '@CryoDamageFXS', True),     # an actor value: Value Modifier
    'Heal': ('CLM: Aura [Healing]', 'Health', None, False),
}

# scripted (PC and Xbox): key -> name, description, script, properties, spells to build
SCRIPTED = {
    'Phoenix': ('CLM: Phoenix',
                'Once every 3 minutes, when you are hit at 15% health or less: you heal 40% of your health and your '
                'attacker bursts into flames for 50 fire damage. Counts once, however many pieces have it.',
                'A1ALMMGEF_OnHitArmourEffect',
                [('AttackerSpell', 'spell', 'A1ALMSPEL_Armor_Phoenix_Flames'), ('LowHealthPercentage', 'float', 0.15),
                 ('RestoreHealthPercent', 'float', 0.4), ('Cooldown', 'float', 180.0)]),
    'StaticCharged': ('CLM: Static Charged',
                      'Whenever anything hits you, 20% chance to shock your attacker for 40 electrical damage, at '
                      'most once every 5 seconds. Melee, ranged and explosions all count. Counts once, however many '
                      'pieces have it.',
                      'A1ALMMGEF_OnHitArmourEffect',
                      [('AttackerSpell', 'spell', 'A1ALMSPEL_Armor_StaticCharged_Arc'), ('ChanceToCast', 'float', 0.2),
                       ('Cooldown', 'float', 5.0)]),
    'Bloodthirsty': ('CLM: Bloodthirsty', 'Every kill heals you 10% of your health. Counts once, however many pieces '
                     'have it.', 'A1ALMMGEF_OnKillArmourEffect', [('RestoreHealthPercent', 'float', 0.1)]),
    'Momentum': ('CLM: Momentum', 'Every kill makes you move 20% faster and regain Action Points faster for 10 '
                 'seconds. Counts once, however many pieces have it.', 'A1ALMMGEF_OnKillArmourEffect',
                 [('SelfSpell', 'spell', 'A1ALMSPEL_Armor_Momentum_Rush')]),
}


def ench_edid(key: str) -> str:
    return f'A1ALMEnch_Constant_Effect_Custom_Effect_{key}'


def perk_edid(key: str) -> str:
    return f'A1ALMPERK_Legendary_Hidden_Armor_{key}'


def perk_mgef_edid(key: str) -> str:
    return f'A1ALMMGEF_Constant_Effect_Custom_Effect_Perk_{key}'


def edits() -> list[str]:
    lines = ['# Generated by gen_armour_set.py - edit that, not this file.']

    def legendary(key, name, desc, ench, op=False):
        new, recipes = f'Armor_{key}', OP_RECIPES if op else TEMPLATE
        lines.extend([f'rec.copy | {OM}{TEMPLATE} | {OM}{new}', f'text.set | {OM}{new} | FULL | {name}',
                      f'text.set | {OM}{new} | DESC | {desc}', f'field.set | {OM}{new} | {PROP1} | @{ench}',
                      f'rec.copy | {CO}{recipes} | {CO}{new}', f'rec.copy | {CO}{recipes}FREE | {CO}{new}FREE',
                      f'field.set | {CO}{new} | CNAM | @{OM}{new}', f'field.set | {CO}{new}FREE | CNAM | @{OM}{new}'])

    def enchantment(edid, name, effects):
        """effects: [(magic effect, magnitude)]; conditions are written afterwards (write_raw)."""
        lines.extend([f'rec.copy | {ENCH_TEMPLATE} | {edid}', f'text.set | {edid} | FULL | {name}'])
        for i, (mgef, mag) in enumerate(effects):
            if i:
                lines.append(f'effect.add | {edid} | 0 | @{mgef}')
            else:
                lines.append(f'field.set | {edid} | Effects\\[0]\\EFID | @{mgef}')
            lines.append(f'effect.magnitude | {edid} | {i} | {mag}')

    def perk(key, name, desc):
        lines.extend([f'rec.copy | {PERK_TEMPLATE} | {perk_edid(key)}', f'text.set | {perk_edid(key)} | FULL | {name}',
                      f'text.set | {perk_edid(key)} | DESC | {desc}',
                      f'rec.copy | {PERK_MGEF_TEMPLATE} | {perk_mgef_edid(key)}',
                      f'text.set | {perk_mgef_edid(key)} | FULL | {name}',
                      f'field.set | {perk_mgef_edid(key)} | Magic Effect Data\\DATA\\Perk to Apply | @{perk_edid(key)}'])

    for key, (name, desc, values, entries, opts) in LEGENDARIES.items():
        effects = [(m, mag) for m, mag, _ in values]
        if entries:
            perk(key, name.replace('CLM:', 'CLM Perk:'), desc)
            effects.append((perk_mgef_edid(key), 0))
        enchantment(ench_edid(key), name, effects)
        legendary(key, name, desc, ench_edid(key))
        if opts.get('water_breathing'):
            lines.append(f'prop.add | {OM}Armor_{key} | Enchantments | ADD | 431 | {OM}Armor_Staminator | '
                         f'@EnchWaterBreathing')

    # --- Radiatin': a cloak on the wearer puts a spell on everyone within the radius, once a second ---
    for kind, (name, target, shader, hostile) in AURA_EFFECTS.items():
        e = f'A1ALMMGEF_Aura_{kind}'
        lines += [f'rec.copy | {AURA_MGEF_TEMPLATE} | {e}', f'text.set | {e} | FULL | {name}',
                  f'field.remove | {e} | . | KWDA', f'field.remove | {e} | . | KSIZ']
        if target.startswith('@'):                   # "Damage" archetype: the damage type is the associated item
            lines.append(f'field.set | {e} | Magic Effect Data\\DATA\\Assoc. Item | {target}')
        else:
            lines += [f'field.set | {e} | Magic Effect Data\\DATA\\Archetype | Value Modifier',
                      f'field.set | {e} | Magic Effect Data\\DATA\\Assoc. Item | 00000000',
                      f'field.set | {e} | Magic Effect Data\\DATA\\Actor Value | @{target}']
        lines.append(f'field.set | {e} | Magic Effect Data\\DATA\\Hit Shader | {shader or "00000000"}')
    for variant, (name, desc, kind, mag, radius, op) in AURAS.items():
        spell, cloak, key = f'A1ALMSPEL_Aura_Radiating_{variant}', f'A1ALMMGEF_Cloak_Radiating_{variant}', \
            f'Radiating_{variant}'
        lines += [f'rec.copy | {AURA_SPELL_TEMPLATE} | {spell}', f'text.set | {spell} | FULL | {name}',
                  f'field.set | {spell} | Effects\\[0]\\EFID | @A1ALMMGEF_Aura_{kind}',
                  f'effect.magnitude | {spell} | 0 | {mag}',
                  f'rec.copy | {CLOAK_TEMPLATE} | {cloak}', f'text.set | {cloak} | FULL | {name}',
                  f'field.set | {cloak} | Magic Effect Data\\DATA\\Assoc. Item | @{spell}']
        enchantment(ench_edid(key), name, [(cloak, radius)])
        legendary(key, name, desc, ench_edid(key), op)

    # --- scripted: the script's magic effect sits in an ability that a hidden perk gives (once) ---
    for target, element, mag in (('Phoenix_Flames', 'Fire', 50), ('StaticCharged_Arc', 'Electrical', 40)):
        mgef, spell = f'A1ALMMGEF_Target_Effect_Hostile_{element}_TargetActor', f'A1ALMSPEL_Armor_{target}'
        lines += [f'rec.copy | A1ALMMGEF_Target_Effect_Hostile_{element} | {mgef}',
                  f'field.set | {mgef} | Magic Effect Data\\DATA\\Delivery | Target Actor',
                  f'rec.copy | {AURA_SPELL_TEMPLATE} | {spell}', f'text.set | {spell} | FULL | CLM: {element} burst',
                  f'field.set | {spell} | SPIT\\Cast Type | Fire and Forget',
                  f'field.set | {spell} | SPIT\\Target Type | Target Actor',
                  f'field.set | {spell} | Effects\\[0]\\EFID | @{mgef}', f'effect.magnitude | {spell} | 0 | {mag}',
                  f'field.set | {spell} | Effects\\[0]\\EFIT\\Duration | 0']
    rush = 'A1ALMSPEL_Armor_Momentum_Rush'
    lines += [f'rec.copy | {AURA_SPELL_TEMPLATE} | {rush}', f'text.set | {rush} | FULL | CLM: Momentum',
              f'field.set | {rush} | SPIT\\Cast Type | Fire and Forget', f'field.set | {rush} | SPIT\\Target Type | Self']
    for i, (src, mag, what) in enumerate(((SPEED, 20, 'speed'), (AP_REGEN, 25, 'Action Points'))):
        mgef = f'{src}_Timed'
        lines += [f'rec.copy | {src} | {mgef}', f'text.set | {mgef} | FULL | CLM: Momentum ({what})',
                  f'field.set | {mgef} | Magic Effect Data\\DATA\\Casting Type | Fire and Forget']
        lines.append(f'field.set | {rush} | Effects\\[0]\\EFID | @{mgef}' if i == 0 else
                     f'effect.add | {rush} | 0 | @{mgef}')
        lines += [f'effect.magnitude | {rush} | {i} | {mag}', f'field.set | {rush} | Effects\\[{i}]\\EFIT\\Duration | 10']
    for key, (name, desc, script, _) in SCRIPTED.items():
        mgef, ability = f'A1ALMMGEF_Constant_Effect_Armor_{key}', f'A1ALMSPEL_Ability_Armor_{key}'
        lines += [f'rec.copy | {SCRIPT_MGEF_TEMPLATE} | {mgef}', f'text.set | {mgef} | FULL | {name}',
                  f'rec.copy | {ABILITY_TEMPLATE} | {ability}', f'text.set | {ability} | FULL | {name}']
        perk(key, name.replace('CLM:', 'CLM Perk:'), desc)
        enchantment(ench_edid(key), name, [(perk_mgef_edid(key), 0)])
        legendary(key, name, desc, ench_edid(key))
    return lines


# ---------------------------------------------------------------- step 2: written directly
def write_raw(data: Path, ack: Path) -> None:
    sys.path.insert(0, str(ack))
    from ack.plugin import Plugin
    from ack.plugin.records import Subrecord

    p = Plugin.load(data / MAIN)
    own = len(p.masters) << 24

    def fid(edid: str) -> int:
        r = p.by_edid(edid)
        assert r is not None, edid
        return r.formid

    def ctda(fn, op, value, param=0, flags=0) -> Subrecord:
        return Subrecord('CTDA', struct.pack('<B3sfH2sIIIIi', (op << 5) | flags, b'\0\0\0', value, fn, b'\0\0',
                                             param, 0, 0, 0, -1))

    def effect_conditions(edid: str, conds_per_effect: list[list]) -> None:
        """Replace the conditions of each effect (in order) of an enchantment or spell."""
        r = p.by_edid(edid)
        out, n = [], -1
        for s in r.subrecords:
            if s.sig == 'CTDA':
                continue
            out.append(s)
            if s.sig == 'EFID':
                n += 1
            if s.sig == 'EFIT':
                out += [ctda(*c) for c in conds_per_effect[n]]
        r.subrecords[:] = out
        r.mark_dirty()

    def perk_entries(edid: str, entries) -> None:
        r = p.by_edid(edid)
        subs = r.subrecords
        del subs[next(i for i, s in enumerate(subs) if s.sig == 'PRKE'):]
        for n, ((ep, tabs), fn, value, conds) in enumerate(entries):
            subs += [Subrecord('PRKE', struct.pack('<BBB', 2, 0, 50)), Subrecord('DATA', struct.pack('<BBB', ep, fn, tabs))]
            for tab, cs in sorted(conds.items()):
                subs += [Subrecord('PRKC', bytes([tab]))] + [ctda(*c) for c in cs]
            if fn == ADD_LEVELED_LIST:
                subs += [Subrecord('EPFT', b'\x03'), Subrecord('EPFB', struct.pack('<H', n)),
                         Subrecord('EPFD', struct.pack('<I', value))]
            else:
                subs += [Subrecord('EPFT', b'\x01'), Subrecord('EPFB', struct.pack('<H', n)),
                         Subrecord('EPFD', struct.pack('<f', value))]
            subs.append(Subrecord('PRKF', b''))
        r.mark_dirty()

    def ability_perk(edid: str, ability: str) -> None:
        r = p.by_edid(edid)
        subs = r.subrecords
        del subs[next(i for i, s in enumerate(subs) if s.sig == 'PRKE'):]
        subs += [Subrecord('PRKE', struct.pack('<BBB', 1, 0, 0)), Subrecord('DATA', struct.pack('<I', fid(ability))),
                 Subrecord('PRKF', b'')]
        r.mark_dirty()

    def single_effect(edid: str, mgef: str) -> None:
        """An ability with one unconditioned effect."""
        r = p.by_edid(edid)
        subs = r.subrecords
        first = next(i for i, s in enumerate(subs) if s.sig == 'EFID')
        r.subrecords[:] = subs[:first] + [Subrecord('EFID', struct.pack('<I', fid(mgef))),
                                          Subrecord('EFIT', struct.pack('<fII', 0.0, 0, 0))]
        r.mark_dirty()

    def wstr(s: str) -> bytes:
        return struct.pack('<H', len(s)) + s.encode('ascii')

    def vmad(script: str, props) -> bytes:
        out = struct.pack('<hhH', 6, 2, 1) + wstr(script) + b'\0' + struct.pack('<H', len(props))
        for name, kind, value in props:
            out += wstr(name)
            if kind in ('spell', 'av'):
                out += b'\x01\x01' + struct.pack('<HhI', 0, -1, fid(value) if kind == 'spell' else value)
            elif kind == 'float':
                out += b'\x04\x01' + struct.pack('<f', value)
        return out

    # value effects' conditions
    for key, (_, _, values, entries, _) in LEGENDARIES.items():
        effect_conditions(ench_edid(key), [c for _, _, c in values] + ([[]] if entries else []))
        if entries:
            perk_entries(perk_edid(key), entries)
    # auras: the spells' own conditions (not in a brawl, in combat) stay; the effects' are set here
    for kind, (_, _, _, hostile) in AURA_EFFECTS.items():
        r = p.by_edid(f'A1ALMMGEF_Aura_{kind}')
        dat = bytearray(r.get('DATA').data)
        flags = struct.unpack_from('<I', dat, 0)[0]
        struct.pack_into('<I', dat, 0, flags if hostile else flags & ~0b101)    # Hostile, Detrimental
        r.set('DATA', bytes(dat))
        r.subrecords[:] = [s for s in r.subrecords if s.sig != 'CTDA'] + [
            ctda(IS_HOSTILE, EQ, 1.0 if hostile else 0.0, PLAYER_REF), ctda(GET_IN_FACTION, EQ, 0.0, GENERIC_BRAWL)]
        r.mark_dirty()
    # self and targeted spells: no conditions
    for edid in ('A1ALMSPEL_Armor_Phoenix_Flames', 'A1ALMSPEL_Armor_StaticCharged_Arc', 'A1ALMSPEL_Armor_Momentum_Rush'):
        r = p.by_edid(edid)
        r.subrecords[:] = [s for s in r.subrecords if s.sig != 'CTDA']
        r.mark_dirty()
    # scripted: script on the magic effect, magic effect in the ability, ability in the perk
    for key, (_, _, script, props) in SCRIPTED.items():
        mgef = p.by_edid(f'A1ALMMGEF_Constant_Effect_Armor_{key}')
        mgef.set('VMAD', vmad(script, [('Health', 'av', HEALTH)] + props))
        mgef.mark_dirty()
        single_effect(f'A1ALMSPEL_Ability_Armor_{key}', f'A1ALMMGEF_Constant_Effect_Armor_{key}')
        ability_perk(perk_edid(key), f'A1ALMSPEL_Ability_Armor_{key}')
        effect_conditions(ench_edid(key), [[]])
    for variant in AURAS:
        effect_conditions(ench_edid(f'Radiating_{variant}'), [[]])
    assert own  # plugin has masters
    p.save(data / MAIN)
    print(f'{len(LEGENDARIES) + len(AURAS) + len(SCRIPTED)} armour legendaries written')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True)
    ap.add_argument('--game', required=True)
    ap.add_argument('--raw-only', action='store_true', help='step 2 only (step 1 already applied)')
    a = ap.parse_args()
    ack, data = Path(a.ack), Path(a.game) / 'Data'
    if a.raw_only:
        return write_raw(data, ack)
    path = HERE / 'armour_set.txt'
    path.write_text('\n'.join(edits()) + '\n', encoding='utf8')
    r = subprocess.run([sys.executable, '-m', 'ack', 'xedit', 'run', 'apply_edits', MAIN, '--save', '--timeout', '900',
                        '--param', f'EDITS={path}'], cwd=ack, capture_output=True, text=True)
    run = sorted((ack / 'private' / 'runs').glob('*-apply_edits'))[-1]
    result = (run / 'result.txt').read_text(encoding='utf8')
    print(result.splitlines()[0])
    if ' 0 errors' not in result.splitlines()[0]:
        raise SystemExit('\n'.join(l for l in result.splitlines() if l.startswith('ERROR')) + r.stderr)
    write_raw(data, ack)


if __name__ == '__main__':
    main()
