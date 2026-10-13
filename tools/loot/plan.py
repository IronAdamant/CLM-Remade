"""Loot-mode plan: unlock families and rarity tiers for every legendary (the judgement calls live here).

    python tools/loot/plan.py        # after tools/loot/families.py has written legendaries.csv

Writes tools/loot/loot_plan.csv (what the generator reads) and docs/LOOT_PLAN.md (for review).

Families: one unlock holotape each. Editor IDs give most families (families.py); THEMES below merges single
legendaries and small families that do the same kind of thing, judged from their effects.
Tiers (author's decision, 2026-10-10): OP = the author's own OP flag (costly recipe requires Show OP);
everything else common / uncommon / rare by power:
- variant families with numbers (Jumpy 50-300%, Hurtin' 100-500%...): non-OP members split into thirds by strength;
- spawns: random creatures common, legendary ones uncommon, bosses and uniques rare;
- the rest: TIER below, else uncommon.
Recipe cost is not used: the author priced some items as statements (God Father's 11,700; Performance Center
5,000 but not OP; Mr. Freeze's 0 but OP).
Left out of loot: legendaries without recipes (unfinished drafts) and the author's test items (kept craftable).
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MAIN = 'Custom Legendary Modifications Remade.esp'

# (kind, family from editor ID) -> theme family name. Unlisted families keep their own name.
THEMES = {
    # --- weapons ---
    ('weapon', 'LesserBleed'): 'Bleeding', ('weapon', 'GreaterBleeding'): 'Bleeding',
    ('weapon', 'WoundinglyEnraging'): 'Bleeding', ('weapon', 'WoundinglyInstigating'): 'Bleeding',
    ('weapon', 'Acidic'): 'Poison and acid', ('weapon', 'NastierPoisoning'): 'Poison and acid',
    ('weapon', 'Burning'): 'Fire', ('weapon', 'IncendiaryStriking'): 'Fire', ('weapon', 'Hinokagutsuchi'): 'Fire',
    ('weapon', 'BurningHellish'): 'Fire',
    ('weapon', 'Chilling'): 'Cold', ('weapon', 'SlightFreeze'): 'Cold', ('weapon', 'MrFreezes'): 'Cold',
    ('weapon', 'HarshlyShocking'): 'Shock', ('weapon', 'Raydens'): 'Shock', ('weapon', 'ThorBlessed'): 'Shock',
    ('weapon', 'JupitersWrath'): 'Shock',
    ('weapon', 'ImprovedPlasmaIInfused'): 'Energy', ('weapon', 'Searing'): 'Energy',
    ('weapon', 'Apotheistic'): 'Energy',
    ('weapon', 'AlienTechd'): 'Alien tech', ('weapon', 'RasSpherical'): 'Alien tech',
    ('weapon', 'CompressedVortexSynthesized'): 'Gauss conversions',
    ('weapon', 'ExplosivelyStriking'): 'Gauss conversions', ('weapon', 'StreetCleaners'): 'Gauss conversions',
    ('weapon', 'TrueSeekerSilenced'): 'Gauss conversions',
    ('weapon', 'CrazilyExplosive'): 'Ordnance', ('weapon', 'MIRV'): 'Ordnance', ('weapon', 'Napalming'): 'Ordnance',
    ('weapon', 'Override'): 'Ordnance', ('weapon', 'GameCrashing'): 'Ordnance',
    ('weapon', 'HeavilyOrdnanced'): 'Spikes', ('weapon', 'SpikeSniper'): 'Spikes',
    ('weapon', 'FourShot'): 'Multi-shot', ('weapon', 'BirdShootin'): 'Multi-shot',
    ('weapon', 'Carbonatin'): 'Multi-shot', ('weapon', 'HighExplosive'): 'Multi-shot',
    ('weapon', 'PerformanceCenter'): 'Performance tuning',
    ('weapon', 'ImprovedPerformanceCenter'): 'Performance tuning',
    ('weapon', 'PrototypeOptimized'): 'Performance tuning', ('weapon', 'ManyBarrelledOptimized'): 'Performance tuning',
    ('weapon', 'Hustling'): 'Performance tuning', ('weapon', 'Compacted'): 'Performance tuning',
    ('weapon', 'Crippingly'): 'Performance tuning',
    ('weapon', 'Devastating'): 'Heavy hitters', ('weapon', 'Commandos'): 'Heavy hitters',
    ('weapon', 'WidowMaking'): 'Heavy hitters', ('weapon', 'Suppressing'): 'Heavy hitters',
    ('weapon', 'RoidRaging'): 'Heavy hitters', ('weapon', 'LucksDrawing'): 'Heavy hitters',
    ('weapon', 'Gunslangers'): 'Gunslingers', ('weapon', 'Gunslinger'): 'Gunslingers',
    ('weapon', 'Generically80sActionHero'): 'Gunslingers',
    ('weapon', 'ShockgunSurgeons'): 'ShotgunSurgeons', ('weapon', 'SuperShotgunning'): 'ShotgunSurgeons',
    ('weapon', 'EagleEyed'): 'Marksman', ('weapon', 'WidowMakers'): 'Marksman',
    ('weapon', 'HighVelocityFulllTitanium'): 'Marksman', ('weapon', 'VATasticallyPenetrating'): 'Marksman',
    ('weapon', 'Highlighting'): 'Marksman',
    ('weapon', 'AdvancedAmmunition'): 'Operators',
    ('weapon', 'Reclaimers'): 'Vampiric', ('weapon', 'Annihilating'): 'Vampiric',
    ('weapon', 'Raging'): 'Relentless', ('weapon', 'PurelyPurging'): 'Relentless',
    ('weapon', 'Communicating'): 'Relentless',
    ('weapon', 'GrandSlam'): 'Brawn', ('weapon', 'TitansWrath'): 'Brawn', ('weapon', 'FaceBusting'): 'Brawn',
    ('weapon', 'AngryNerds'): 'Curios', ('weapon', 'LorenzosLegendary'): 'Curios',
    ('weapon', 'Assaultrons'): 'Curios', ('weapon', 'LiarsCompedium'): 'Curios',
    ('weapon', 'BloodyMessMaxed'): 'Utility', ('weapon', 'Silenced'): 'Utility', ('weapon', 'Beginner'): 'Utility',
    ('weapon', 'DevilsDue'): 'Utility',
    ('weapon', 'InstantKilling'): 'Forbidden (weapon)', ('weapon', 'Medics'): 'Curios',
    ('weapon', 'Overcharging'): 'Energy', ('weapon', 'VATSPenetrating'): 'Marksman',
    ('weapon', 'Cheaters'): 'Forbidden (weapon)', ('weapon', 'ZeusCrafted'): 'Forbidden (weapon)',
    ('weapon', 'Suicidal'): 'Forbidden (weapon)',
    ('weapon', 'RapidFire'): 'Quicker', ('weapon', 'Crippling'): 'Performance tuning',   # 2.1 requests
    ('weapon', 'Bloodlust'): 'Heavy hitters', ('weapon', 'Blitzkrieg'): 'Marksman',
    ('weapon', 'NaturesWrath'): 'Elements',
    # --- armour ---
    ('armor', 'Immune'): 'Immunities', ('armor', 'BiologicalHazmat'): 'Immunities',
    ('armor', 'HawkinsExperimental'): 'Immunities', ('armor', 'CatTailed'): 'Immunities',
    ('armor', 'Waterbreathing'): 'Immunities',
    ('armor', 'Regenerative'): 'Healing', ('armor', 'StimpakSelfHeal'): 'Healing',
    ('armor', 'Longetivity'): 'Healing', ('armor', 'FusionAbsorption'): 'Healing',
    ('armor', 'CarryWeight'): 'Carrying', ('armor', 'SantaPriscas'): 'Carrying', ('armor', 'WarCarrying'): 'Carrying',
    ('armor', 'Stealth'): 'Undetectable', ('armor', 'Escapist'): 'Undetectable',
    ('armor', 'Camouflaged'): 'Undetectable',
    ('armor', 'HUDEffect'): 'Sight', ('armor', 'Widowmakers'): 'Sight', ('armor', 'Sensing'): 'Sight',
    ('armor', 'Chronos'): 'Speed', ('armor', 'Flash'): 'Speed', ('armor', 'Flying'): 'Jumpy',
    ('armor', 'Enlightened'): 'Enlightenment', ('armor', 'JackOfAllTrades'): 'Enlightenment',
    ('armor', 'Mightily'): 'Enlightenment', ('armor', 'ChemBoost'): 'Enlightenment',
    ('armor', 'SadisticBrawlers'): 'Brawlers', ('armor', 'Generically80sActionHero'): 'Brawlers',
    ('armor', 'NightlyTraining'): 'Brawlers', ('armor', 'Brutish'): 'Brawlers',
    ('armor', 'BurningRage'): 'Flaming', ('armor', 'FlamingCloaked'): 'Flaming',
    ('armor', 'Fiddling'): 'Handiwork', ('armor', 'Handy'): 'Handiwork',
    ('armor', 'SilverTonguedBusinessMan'): 'Handiwork', ('armor', 'DevilsDue'): 'Handiwork',
    ('armor', 'ReloadSpeed'): 'Steady aim', ('armor', 'Focused'): 'Steady aim',
    ('armor', 'MarathonRunning'): 'Speed',
    ('armor', 'AimStabilized'): 'Steady aim', ('armor', 'PinpointAccuracy'): 'Steady aim',
    ('armor', 'CriticallyHurtin'): 'Steady aim',
    ('armor', 'BallisticProtection'): 'Plating', ('armor', 'Titanium'): 'Plating', ('armor', 'Damage'): 'Plating',
    ('armor', 'PABattery'): 'Power armour', ('armor', 'WillofEndurance'): 'Power armour',
    ('armor', 'Brutal'): 'Juggernaut', ('armor', 'SuperTanking'): 'Juggernaut', ('armor', 'TrueSynth'): 'Juggernaut',
    ('armor', 'NanoCoated'): 'Juggernaut', ('armor', 'AlienNanoCoated'): 'Juggernaut',
    ('armor', 'GodsArmor'): 'Juggernaut', ('armor', 'YamamotosMighty'): 'Juggernaut', ('armor', 'NMU'): 'Juggernaut',
    ('armor', 'Staminator'): 'Speed', ('armor', 'WeaponMastery'): 'Steady aim',   # 2.1 requests
    # 2.1's own armour (tools/edits/gen_armour_set.py)
    ('armor', 'NightOwls'): 'Surroundings', ('armor', 'SunKissed'): 'Surroundings',
    ('armor', 'StormChasing'): 'Surroundings', ('armor', 'ShadowDwelling'): 'Surroundings',
    ('armor', 'Amphibious'): 'Surroundings', ('armor', 'Entrenched'): 'Surroundings', ('armor', 'HomeTurf'): 'Surroundings',
    ('armor', 'Underdogs'): 'Grit', ('armor', 'GlassCannon'): 'Grit', ('armor', 'Ironclad'): 'Grit',
    ('armor', 'GlowingHeart'): 'Grit', ('armor', 'Overcharged'): 'Power armour', ('armor', 'Scavengers'): 'Handiwork',
    ('armor', 'Phoenix'): 'Healing', ('armor', 'Bloodthirsty'): 'Healing', ('armor', 'Momentum'): 'Speed',
    ('armor', 'StaticCharged'): 'Untouchable',
    # 2.1 counterparts and the 2016 legendaries that went missing (tools/edits/gen_restore_21.py)
    ('armor', 'Resistance'): 'Immunities', ('armor', 'GheedsFortunate'): 'Handiwork',
    ('weapon', 'PoisonersNimble'): 'Poison and acid', ('weapon', 'OneManPunching'): 'Brawn', ('weapon', 'Flaming'): 'Fire',
    # 2.1: the old requests (tools/edits/gen_requests_21.py)
    ('armor', 'Stealthy'): 'Undetectable', ('armor', 'Jumpers'): 'Jumpy', ('armor', 'HelloNeighbour'): 'Handiwork',
    ('armor', 'NoBraking'): 'Brawlers', ('armor', 'Enraged'): 'Flaming', ('weapon', 'HealingBeam'): 'Curios',
    ('weapon', 'GodCreator'): 'Curios', ('weapon', 'CinematicExcellence'): 'Utility', ('weapon', 'CQC'): 'Automatic',
    ('weapon', 'DragonBlade'): 'Brawn', ('weapon', 'Decimating'): 'Heavy hitters',
    ('armor', 'Cheaters'): 'Forbidden (armour)', ('armor', 'GodFathers'): 'Forbidden (armour)',
}

# Splits by editor-ID fragment, checked before THEMES (Recoilless holds three different kinds of legendary).
EDID_THEMES = [
    ('Recoilless_Variant_Electrical_Str', 'Strikers'), ('Recoilless_Variant_Gauss_Striker', 'Strikers'),
    ('Recoilless_Variant_Harpoon_Strike', 'Strikers'),
    ('Recoilless_Limited_', 'Savage'), ('Recoilless_Variant_Savage', 'Savage'),
    ('Recoilless_Variant_DeathlySilence', 'Savage'), ('Recoilless_Variant_MurderouslySil', 'Savage'),
    ('Recoilless_Variant_SpecialOps', 'Savage'),
]

# Duplicates whose recipes 2.1 removed (tools/edits/balance_21.py); the legendaries stay for existing gear.
HIDDEN = {'A1ALMOMOD_Legendary_Armor_Camouflaged_All', 'A1ALMOMOD_Legendary_Armor_Camouflaged_Crouch'}

# Display names for families kept from editor IDs, where the ID is not the in-game name.
DISPLAY = {
    'IncreaseWeaponDamage': "Fisto's", 'DamageBoost': "Hurtin'", 'CriticalHitChance': "Lucky Hittin'",
    'Speed': 'Speedy', 'CombinedSpeedJump': 'Combined Speed and Jump', 'Contact': "Disintegratin'",
    'PaddleBall': 'Nuka-Infused', 'Firework': 'Pyrotechnical', 'Time': "Concentratin'",
    'Recoilless': 'Recoilless', 'ShotgunSurgeons': "Shotgun Surgeon's", 'Elements': 'Elemental',
    'KeltasFactorium': "Keltas' Factorium", 'SynthFactorium': 'Synthesised Factorium',
    'HydrasFang': "Hydra's Fang", 'LibertyPrime': "Liberty Prime's", 'MajesticSwagger': 'Majestically Swaggering',
    'UltimaHecate': "Ultima Hecate's", 'Garm': "Garm's", 'Destroyers': "Destroyer's", 'Operators': "Operator's",
    'LimbBreaker': "Limb Breaker's", 'Lobbing': "Lobbin'", 'Mine': 'Mine launchin\'', 'RainMan': "Rainman's",
    'Rocketing': "Rocketin'", 'Seeker': "Seekin'", 'Splintering': "Splinterin'", 'Trapping': "Trappin'",
    'WeatherAlter': 'Weather Altering', 'Thumping': "Thumpin'", 'Pushing': 'Pushing', 'Slayer': "Slayer's",
    'MobyDicks': "Moby-Dick's", 'BioReactive': 'BioReactive Explosive', 'ExplosiveMelee': "Shavka's Explosive Striking",
    'Backstabbing': 'Backstabbing', 'ImpactLanding': 'Impact Landing', 'FactionalDamage': 'Factional Damaging',
    'Untouchable': 'Untouchable', 'Punching': 'Punching', 'Bouncing': 'Bouncing and Jedi', 'Murderous': 'Murderous',
    'Refilling': 'Refilling', 'OnePunchMans': "One Punch Man's", 'Shield': 'Shields', 'Undetectable': 'Ghostly and Camouflaged',
    'Immune': 'Immunities',
    'Jumpy': 'Jumpy and Flyin\'', 'Radiating': "Radiatin'", 'CapShowering': "Cap Showerin'",
}

# Tiers for non-OP legendaries outside numbered variant families, by in-game name (without "CLM: ").
TIER = {
    # weapons
    'Beginner': 'common', 'Compacted': 'common', 'Pre-Suppressed': 'common', 'Lesser Bleeding': 'common',
    'Acidic': 'common', 'Burning': 'common', 'Incendiary Striking': 'common', 'Slightly Freezing': 'common',
    'Highlighting': 'common', 'Prototype Optimized': 'common', 'Improved Plasma Infused': 'common',
    "Devil's Due": 'common', 'Vatastically Penetrating': 'common', "Rayden's Fury": 'common',
    'Bloody Messy': 'common', 'Crippingly Rapid': 'common', 'Devastating': 'common', 'Greater Poisoning': 'common',
    'Searing': 'rare', 'Four Shot': 'rare', "Carbonatin'": 'rare', 'High Explosive': 'rare',
    "Gunslanger's": 'rare', "Alien-Tech'd": 'rare', "Face Bustin'": 'rare', 'Burning Hellish': 'rare',
    'Performance Center': 'rare',
    "Shotgun Surgeon's II": 'rare', "Institute Shotgun Surgeon's II": 'rare', "Plasma Shotgun Surgeon's II": 'rare',
    "Laser Shotgun Surgeon's II": 'rare',
    "Keltas' Flawed Factorium": 'common', "Keltas' Perfect Factorium": 'rare',
    'Synthesised Flawed Factorium': 'common', 'Synthesised Perfect Factorium': 'rare',
    'Automatic (Furious)': 'rare', "Viciously Thumpin'": 'rare', "Silent Slayer's": 'rare',
    'Pushing (Ranged)': 'common', "Operator's Enhanced Arsenal": 'rare', "Reaper's Embrace:": 'rare',
    # armour
    'Cat Tailed': 'common', 'Waterbreathing': 'common', "Fiddlin'": 'common', "Sensin'": 'common',
    'Aid Patch': 'common', 'Highlighting ': 'common', 'Titanium': 'common',
    'Ballistic Protection (Basic)': 'common', 'Ballistic Protection (Master-crafted)': 'rare',
    "Battery Regeneratin' (Slow)": 'common', "Tracker's Focused Sight": 'rare',
    "One Punch Man's": 'rare', "Tradin' Jack's": 'rare', 'Sadistic Brawlers': 'rare',
    # fun or cosmetic conversions
    'Paintball (Blue)': 'common', 'Paintball (Green)': 'common', 'Paintball (Orange)': 'common',
    'Paintball (Red)': 'common', 'Paintball (White)': 'common', 'Paintball (Yellow)': 'common',
    'Pyrotechnical (Minutemen Flare)': 'common', 'Pyrotechnical (Blue)': 'common', 'Pyrotechnical (Crackle)': 'common',
    'Pyrotechnical (Gold)': 'common', 'Pyrotechnical (Green)': 'common', 'Pyrotechnical (Pink)': 'common',
    'Pyrotechnical (Red)': 'common', 'Pyrotechnical (Silver)': 'common', 'Pyrotechnical (Yellow)': 'common',
    'Energized (Gauss)': 'common', 'Energized (Deep Blue Laser)': 'common', 'Energized (Gold Laser)': 'common',
    'Energized (Green Laser)': 'common', 'Energized (Blue Laser)': 'common', 'Energized (Orange Laser)': 'common',
    'Energized (Pink Laser)': 'common', 'Energized (Purple Laser)': 'common', 'Energized (Red Laser)': 'common',
    'Energized (Plasma)': 'common',
    'Recoilless': 'common', "Bone Crushin'": 'common', 'Savage': 'rare', 'Savage (Limited)': 'rare',
    'Silently Savage (Limited)': 'rare', 'Caged Savage': 'rare', 'Deathly Silenced': 'rare',
    'Murderously Silenced': 'rare', 'Havoc (Bullets)': 'rare', 'Havoc (Blue Laser)': 'rare', 'Havoc (Plasma)': 'rare',
    'Havoc (Red Laser)': 'rare',
    "Concentratin' (Brief)": 'common', "Time Father's Bashful (Brief)": 'common',
    # built from 1.09's unused pieces (2026-10-11)
    "Lobbin' (Nuke Mine)": 'rare', 'Focused (Brief)': 'common', "VATS Penetratin'": 'common',
    # 2.1's own armour: the everyday conditions common, the strongest rare
    "Night Owl's": 'common', 'Sun-Kissed': 'common', "Storm Chasin'": 'common', 'Home Turf': 'common',
    "Scavenger's": 'common', 'Phoenix': 'rare', "Underdog's": 'rare', "Radiatin' (Healing)": 'rare',
    # 2.1 counterparts and restorations
    'Ballistic Protection (Light)': 'common', 'Regenerative (Slow)': 'common', "Shotgun Surgeon's (Trainee)": 'common',
    "Gheed's Fortunate": 'common', "Keltas' Quick Draw Factorium": 'common', "Poisoner's Nimble": 'uncommon',
    "Cap Showerin' (Frag)": 'rare', "Cap Showerin' (Fire)": 'rare', "Cap Showerin' (Cryo)": 'rare',
    "Cap Showerin' (Plasma)": 'rare', 'Healing Beam': 'uncommon', 'Cinematic Excellence': 'common',
}
TIERS = ('common', 'uncommon', 'rare')
RARE_SPAWN = re.compile(r'Boss|Behemoth|Queen|King|Kellog|Courser|Ghoulrilla|PALegendary|Glowing One', re.I)


def strength(name: str) -> float:
    """The number in a variant name: "Jumpy (150%)" -> 150, "Murderous (x3)" -> 3; 0 when there is none."""
    m = re.search(r'\((?:x)?(\d+)(?:%|x)?\)', name)
    return float(m.group(1)) if m else 0.0


def clean(name: str) -> str:
    return re.sub(r'^(CLM|ZLM): ', '', name)


def main():
    rows = [r for r in csv.DictReader((HERE / 'legendaries.csv').open(encoding='utf8'))]
    excluded = [r for r in rows if r['recipes'] == '0' or r['family'] == 'Test']
    rows = [r for r in rows if r not in excluded]

    fam_of = {}
    for r in rows:
        fam = next((theme for frag, theme in EDID_THEMES if frag in r['edid']), None) or \
            THEMES.get((r['kind'], r['family']), r['family'])
        fam_of[r['edid']] = DISPLAY.get(fam, fam)
    members = defaultdict(list)
    for r in rows:
        members[(r['kind'], fam_of[r['edid']])].append(r)

    tier = {}
    for (kind, fam), xs in members.items():
        if fam.startswith('Spawn: '):
            for r in xs:
                creature = r['edid'].split('Spawning_', 1)[1]  # every editor ID starts with ..._Legendary_
                tier[r['edid']] = 'rare' if RARE_SPAWN.search(creature + ' ' + r['name']) else \
                    'uncommon' if 'Legendary' in creature else 'common'
            continue
        by_origin = defaultdict(list)
        for r in xs:
            by_origin[r['family']].append(r)
        for origin in by_origin.values():
            if not any(strength(clean(r['name'])) for r in origin):
                continue
            numbered = sorted((r for r in origin if r['op'] == '0'), key=lambda r: strength(clean(r['name'])))
            n = len(numbered)
            for i, r in enumerate(numbered):
                # one variant alone: uncommon; two: uncommon and rare; more: weakest third common, and so on
                tier[r['edid']] = 'uncommon' if n == 1 else ('uncommon', 'rare')[i] if n == 2 else \
                    TIERS[min(2, i * 3 // n)]
        for r in xs:
            if r['op'] == '1':
                tier[r['edid']] = 'OP'
            elif r['edid'] not in tier:
                tier[r['edid']] = TIER.get(clean(r['name']), 'uncommon')

    # Write the plan.
    with (HERE / 'loot_plan.csv').open('w', newline='', encoding='utf8') as f:
        w = csv.writer(f)
        w.writerow(['family', 'kind', 'holotape_plugin', 'edid', 'name', 'tier', 'plugin'])
        for (kind, fam), xs in sorted(members.items()):
            home = MAIN   # one plugin since the DLC add-ons were merged (2026-10-12)
            for r in sorted(xs, key=lambda r: (TIERS + ('OP',)).index(tier[r['edid']])):
                w.writerow([fam, kind, home, r['edid'], clean(r['name']), tier[r['edid']], r['plugin']])

    counts = defaultdict(int)
    for t in tier.values():
        counts[t] += 1
    lines = [
        '# Loot mode plan: families and tiers',
        '',
        'Generated by `tools/loot/plan.py` from the plugins. Each family below gets one **unlock holotape**: carrying',
        "it shows that family's recipes at the workbench. Each legendary can also drop as a **loose mod**. Tiers set",
        'how often it drops (common / uncommon / rare); **OP** legendaries also need the unique OP item for weapons or',
        'armour to craft.',
        '',
        f'**{len(rows)} legendaries in {len(members)} families.** Tiers: ' +
        ', '.join(f'{t} {counts[t]}' for t in TIERS + ('OP',)) + '.',
        '',
        'Left out of loot: ' + ', '.join(f"{clean(r['name'])} ({'test item, stays craftable' if r['family'] == 'Test' else 'duplicate, hidden in 2.1' if r['edid'] in HIDDEN else 'unfinished draft, no recipe'})"
                                          for r in excluded) + '.',
        '',
    ]
    for kind, title in (('weapon', 'Weapon families'), ('armor', 'Armour families')):
        lines += [f'## {title}', '', '| Family | Legendaries (tier) |', '|---|---|']
        for (k, fam), xs in sorted(members.items()):
            if k != kind:
                continue
            order = sorted(xs, key=lambda r: ((TIERS + ('OP',)).index(tier[r['edid']]), clean(r['name'])))
            items = '; '.join(f"{clean(r['name'])} ({tier[r['edid']]})" for r in order)
            lines.append(f'| {fam} | {items} |')
        lines.append('')
    (REPO / 'docs' / 'LOOT_PLAN.md').write_text('\n'.join(lines), encoding='utf8')
    print(f'{len(rows)} legendaries, {len(members)} families; ' + ', '.join(f'{t} {counts[t]}' for t in TIERS + ('OP',)))
    print(f'excluded: {[clean(r["name"]) for r in excluded]}')


if __name__ == '__main__':
    main()
