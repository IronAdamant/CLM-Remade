# CLM 2.1 plan: balance, armour, lost legendaries and the old requests

2.0 fixed the bugs (Grok's scrape, `docs/COMPLAINTS_TRIAGE.md`). 2.1 is the content update:

1. **A balance pass.** "Balanced" gets a written rule (below), and the legendaries that break it move to OP.
2. **Balanced counterparts** for the families that move: lower tiers, so balanced players keep the family.
3. **New armour legendaries**, CLM's own: effects the base game does not have, with a real choice in them.
4. **The 2016 legendaries that went missing** before 1.09, refurbished.
5. **The 2016-17 requests** marked "not possible", "delayed" or "no time".
6. **Names and descriptions** that are wrong or clash.

No changes to the loot system, settings or costly / free recipes. Loot tiers, picker families and the MCM follow
the OP flags automatically when they are regenerated (`tools/loot/families.py`, `plan.py`, `generate.py`,
`tools/config/picker.py`, `mcm.py`).

Platforms, as in 2.0: legendaries built from records only go everywhere, PlayStation included. Legendaries that need
a script are PC and Xbox only; the PlayStation build (`tools/release/playstation.py`) keeps them with a note or
leaves them out.

## Sources (read 2026-10-13)

The author's 2016-17 documents are in `docs/private logs/`: **local only, never committed** (excluded in
`.git/info/exclude`; the repo is public). If that folder is missing, ask the author for it.

- `CK Requests.docx`: the request log behind both Google Docs on the old mod page ("Requests in progress" and
  "Requests he could not complete"). Its text colours were the status: red = impossible then, blue = done, orange =
  unsure, green = in progress, black = to do. A plain-text copy without colours is in AgentCreationKit
  `private/logs_text/`.
- `Custom Legendary Modifications (Mods done).xlsx`: updated 2026-10-13 from the 2.1 plugin. Tab "Current (2.1)"
  lists all 591 legendaries with credits; tab "2016 list (original)" is the old sheet, with each entry's current name
  or "Not in 2.1" (the list behind section 5).
- `Custom Legendary Modifications ideas.docx`, `Place for IDEAS.docx`: the author's own ideas.
- `Remade System plans.docx`: the global-variable settings design that 2.0 already implements.

Requests already in CLM, nothing to do: Caged Savage, Gunslinger's, Gauss legendaries (YamatoNCC-1701), triple
damage (Triplet: in the damage families), paddleball Quantum (mademost), Thor's power-attack explosion, Bloody Messy,
lobber arrow mines (2.0's Lobbin' mines), healing others (2.0's Medic's), loot-list injection (2.0's loot mode), One
Punch (fixed in 2.0).

## 1. Done so far

- Jumpy (10%) / (25%), Rapid Fire (100%), Rapid Hurtin', Crippling (100%) (`tools/edits/gen_req1_simple.py`).
- Bloodlust, Blitzkrieg, Nature's Wrath, Staminator and Weapon Mastery (`tools/edits/gen_req2_perks.py`).
- The 23 armour legendaries of section 5 (`tools/edits/gen_armour_set.py`, 2026-10-13); loot plan, picker, MCM page
  and debug recorder regenerated: 614 legendaries in 115 families. FO4Edit: 0 errors. Not yet tested in game.
- Fisto's stacking fix (section 2, `tools/edits/fix_fistos_stacking.py`): only the best Fisto's piece counts.
- Balance moves (section 3, `tools/edits/balance_21.py`): 56 legendaries to OP, 2 to balanced, the duplicate
  Camouflaged pair's recipes removed.
- Names and descriptions (section 8, `tools/edits/names_21.py`): 85 legendaries.
- Balanced counterparts (section 4) and the 2016 legendaries (section 6) (`tools/edits/gen_restore_21.py`): 31 new.
  Plugin now 643 legendaries in 117 families; FO4Edit 0 errors. Not yet tested in game.
- The old requests (section 7, `tools/edits/gen_requests_21.py`): 17 new, Brutish and Advanced Titanium changed,
  PlayStation perk magazines. Plugin now 660 legendaries in 118 families; FO4Edit 0 errors. Loot pools over 255
  entries are now split into equal parts (`tools/loot/generate.py`; the OP pool reached 256).
- In-game test checklist: `docs/TEST_CHECKLIST_2.1.md`.

Author's decisions (2026-10-13): explosive conversions keep their fire rate (no halving); the Fisto's stacking fix
goes ahead; the OP list is accepted, measured against the base game (below); CLM may design and build its own
armour legendaries, without scripts where possible, scripted ones for PC and Xbox.

## 2. The base game, and the balance rule

### What the base game's legendaries do

Read from Fallout4.esm and the four DLC with FO4Edit (2026-10-13): 89 legendary mods, their enchantments and the
perks behind them (`ModLegendaryCommonPerk` and friends). Numbers are exact.

**Weapons**

| Kind | Legendaries | Size |
|---|---|---|
| Damage, always | Two Shot | +1 projectile at full damage (wider spread): about double damage |
| Damage, conditional | Instigating; Bloodied; Berserker's; Nocturnal; Junkie's; Furious; Defiant; Hitman's | x2 on full-health targets; up to +95% at low health; up to +200% at 0 damage resistance; x2 at midnight but x0.33 by day; +15% per addiction; +15% per consecutive hit; x2 for the last round; +10% aiming |
| Damage vs one enemy type | Assassin's, Exterminator's, Ghoul Slayer's, Hunter's, Mutant Slayer's, Troubleshooter's | +50% |
| Fire rate | Rapid | +25%, reload +15% |
| Ammo | Never Ending | Never reloads |
| Extra damage | Explosive; Wounding; Poisoner's; Incendiary; Freezing; Plasma Infused; Irradiated | +15 area damage per projectile (per pellet on shotguns); 25 bleed; 30 poison over 10 s; 15 fire; +10 cryo; +10 energy; 50 rads |
| Control | Staggering; Kneecapper; Enraging; Freezing | Stagger chance; 20% leg cripple; frenzy on critical; freeze on critical |
| V.A.T.S. | V.A.T.S. Enhanced; Quickdraw; Stalker's; Relentless; Lucky | -25% / -40% AP; -25% AP; accuracy out of combat; criticals refill AP; x2 critical damage, meter +15% |
| Far Harbor | Blazing, Charged, Frigid, Duelist's (on block); Resilient; Steadfast; Deadeye; Resolute | 25% for 50 fire, 10% for 100 electrical, 20% freeze, 25% disarm; +150 DR reloading; +50 DR aiming; slow time aiming / last round |

**Armour** (per piece; a player wears five, six in power armour, and they add up)

| Kind | Legendaries | Size per piece |
|---|---|---|
| Less damage, conditional | Sentinel's (standing still), Cavalier's (blocking or sprinting) | 15%; five pieces 75% |
| Less damage from one enemy type | Assassin's, Exterminator's, Ghoul Slayer's, Hunter's, Mutant Slayer's, Troubleshooter's | 15% |
| Resistance | Bolstering; Poisoner's | up to +35 damage and energy resistance at low health; +25 poison |
| SPECIAL | Lucky; Fortifying, Sharp, Cunning; Unyielding; Rad Powered | +2 Luck; +1 to two stats; +3 to all at 25% health or less; Strength with rads |
| Movement and AP | Sprinter's; Powered; V.A.T.S. Enhanced | +10% speed; +5 AP regeneration; -10% AP |
| Stealth and utility | Chameleon; Acrobat's; Freefall; Safecracker's | invisible sneaking and still; half / no fall damage; easier locks |
| Reactions | Punishing; Duelist's; Martyr's; Far Harbor's Cryogenic, Incendiary, Cloaking, Auto Stim (scripted) | 10% melee reflect; 10% disarm; slow time at 20% health; freeze / ignite melee attackers, stealth field on melee hit, stimpak at 25% health, each with a 20-60 s cooldown |
| Power armour (Nuka-World) | Overboss tesla coils; Quantum and Nuka-Cola paint | 4 energy damage a second to everyone near; AP regeneration / +3 Agility with every piece |

**What the base game never does on armour:** raise weapon damage; react to the time, the weather, darkness, water,
settlements or the enemy's level; auras (one power armour torso aside); heal others; act on a kill; trade-offs (more
damage for more risk). That is the space CLM's own armour fills (section 5).

### The rule

**Balanced = no stronger than the base game's strongest of the same kind.** The first draft of this rule was
stricter than the base game in places (it capped damage at +50%, while Two Shot is +100%); this version follows the
game:

| | Balanced (per weapon / per armour piece) | OP | Base-game yardstick |
|---|---|---|---|
| Damage | +100% always, +200% under a real condition (aiming does not count: guns are always aimed) | More | Two Shot, Berserker's |
| Fire rate | +50% | More | Rapid +25% |
| Extra damage per hit | +25 points, or a damage-over-time of the same size | More | Wounding, Explosive |
| Projectiles | +1 | +2 or more, shotgun conversions | Two Shot |
| Ammo | Bigger magazines, never reloading, chances to refill | Never using ammo | Never Ending |
| Armour: less damage | 15-25% under a condition | More, or always | Sentinel's |
| Armour: resistances | +50 | More | Bolstering +35 |
| Armour: SPECIAL | +2 always, +3 conditional | More | Lucky, Unyielding |
| Armour: speed / jump | +25% speed, +100% jump | More | Sprinter's +10% |
| Armour: damage bonus | +50%, one piece only (needs the Fisto's fix below) | More | none |
| Healing | about 1% of health per second, or conditional, or on a cooldown | More | Auto Stim |
| Immunity | 50% less from a damage type | Full immunity | Acrobat's / Freefall |
| Control | Chances, short stuns, staggers, cooldowns | Always paralysing or pacifying, permanent invisibility | Duelist's, Cryogenic |
| Resources | Cheaper | Free: no AP, no battery drain, no buy price | V.A.T.S. Enhanced |

**Stacking.** Value effects in an armour enchantment (resistances, SPECIAL, speed) add up per piece, as the base
game's do. A perk applies once however many pieces give it, but different tiers are different perks, so they
multiply: Fisto's (20%) to (150%) on five pieces is about x11 damage. **Fisto's fix (approved):** each Fisto's perk
entry gets "does not have a higher Fisto's perk", so only the best piece counts (records only).

**Explosive conversions** (Rocketin', Rainman's, Lobbin', the mines, Splinterin', BioReactive, Thumpin') stay as they
are: they are CLM's character (author, 2026-10-13). Only the nuclear ones move to OP (section 3).

## 3. Balance moves

Moving to OP adds the Show OP check that every OP recipe carries (the setting item or its global,
`tools/config/settings.py`) to the costly and FREE recipes, as `tools/edits/op1_flag_extremes.py` did in 2.0. Items
players already own keep working; with Show OP off the recipe is hidden; in loot mode they become OP tier.

### To OP: weapons (33)

| Legendary | Why |
|---|---|
| Hurtin' (150%), (200%) | Above Two Shot's +100%, always on |
| Devil's Due (weapon) | Damage set to 666 |
| Hustlin', Rapid Fire (100%), Quicker (75%), Quicker (100%), Gunslanger's | Fire rate above +50% |
| Four Shot, High Explosive, Slayer's, Silent Slayer's, Bird Shootin' | 2 to 9 extra projectiles |
| Shotgun Surgeon's I and II (all 8) | Shotgun conversion: up to +11 pellets on any weapon |
| Shockgun Surgeon's | +4 lightning beams and +130 electrical damage |
| Thor Blessed, Overchargin' | +90 and +50 energy damage per hit |
| Alien-Tech'd | 20-minute damage-over-time, always cripples |
| Keltas' Perfect Factorium | Never Ending, Two Shot's damage and Rapid in one |
| Synthesised Rapid / Specialised / Perfect Factorium | Never use ammo (Flawed stays: -25% fire rate, -50% damage) |
| Lobbin' (Nuke Mine), Sticky Nuke Mine launchin', BioReactive Explosive (Nuclear), Shavka's Explosive Striking (Nuclear) | A nuclear blast on every shot |

Measured against the base game these stay balanced (the first draft moved them): **Hurtin' (100%)** and
**Widowmakin'** (x2 = Two Shot), **Commando's** (+50%, x3 sneak attacks: a sneak attack is a first hit, like
Instigating's), **Keltas' Rapid** and **Specialised Factorium** (Never Ending with a bigger magazine or perfect
accuracy). **Viciously Thumpin'** stays too (an explosive conversion).

### To OP: armour (23)

| Legendary | Why |
|---|---|
| Fisto's (100%), (150%) | All weapon damage x2 / x2.5 (Fisto's (50%) stays, with the fix) |
| Ballistic Protection (Advanced), (Master-crafted) | +100 / +150 resistance per piece (Bolstering: +35) |
| Advanced Titanium | 9x power armour health and 5% less damage |
| Tradin' Jack's | +5 SPECIAL always, +200 rad resistance per piece (Unyielding: +3, at low health) |
| Regenerative | 5 health per second, always |
| Speedy (50%), (100%), (150%); Combined Speed and Jump Boosts (50%), (100%), (150%); Nimble (100%), (150%) | Speed above +25% per piece (Sprinter's: +10%) |
| Jumpy (150%) | Jump above +100% |
| Lucky Hittin' (25%) | +25% critical chance on every hit |
| Sadistic Brawlers | Reflects all damage, disarms everyone |
| Untouchable (Paralyzed), (Pacify); Punching (Paralyze) | Melee enemies can never touch you |
| Devil's Due (armour) | Defence set to 666 |
| Shavka's Explosive Striking (Nuclear) | Nuclear blast on every punch |

### To balanced (2)

**Majestically Swaggering** (does 1% damage; a knock-back toy) and **Aim Stabilized (100%)** (steady aim only, like
a perk rank).

### Duplicates to hide

Camouflaged (Always) and Camouflaged (Crouch) exist as both `Armor_Camouflaged_*` and
`Armor_Undetectable_Variant_Camouflaged_*`. Keep the `Undetectable` pair (its family); the other pair loses its
recipes and loot entries, but the records stay so existing gear keeps working.

## 4. Balanced counterparts

Families that lose their balanced members get small tiers, the way Jumpy got (10%) and (25%). All records only.

| New legendary | Effect | Replaces in balanced |
|---|---|---|
| Hurtin' (25%), (50%) | Damage +25 / 50% | Hurtin' (150%, 200%) |
| Speedy (10%), (25%) | Movement speed (Leylanee's 2016 Speedy was 25%) | Speedy (50-150%) |
| Combined Speed and Jump Boosts (10%), (25%) | Both (Leylanee's 2016 Speedily Jumpy) | Combined (50-150%) |
| Nimble (25%) | Move faster while aiming | Nimble (100%, 150%) |
| Ballistic Protection (Light) | +25 damage resistance | Advanced / Master-crafted |
| Regenerative (Slow) | 1 health per second, 2 out of combat | Regenerative |
| Resistance (Acid / Electric / Explosion / Poison / Radiation / Limb Damage) | 50% less of that damage | The six OP Immunities |
| Gheed's Fortunate | Buy 20% cheaper, sell 20% higher (forgrif's 2016 request) | Silver-Tongued Businessman (95%) |
| Shotgun Surgeon's (Trainee) | +3 pellets, 30% wider spread | Shotgun Surgeon's family |
| Quick Draw Factorium | Refills the magazine 25% of the time it runs dry | Synthesised Factoriums |

## 5. CLM's own armour (built 2026-10-13)

Designed into the gaps of the table in section 2: effects the base game has nowhere, each with a condition, a
trade-off or a cooldown, so picking one is a choice. Value effects add up per piece; the perk-based parts count
once. Names follow CLM's conventions (possessives and dropped g's: Storm Chasin', Radiatin', Underdog's). 22
balanced, 1 OP. New loot / picker families: Surroundings, Grit, Radiatin'; the rest joined Healing, Speedy,
Untouchable, Power armour and Handiwork.

| Legendary | Effect | How | Check in game |
|---|---|---|---|
| **Night Owl's** | 8pm-6am: +1 Perception, +1 Agility, +10 damage and energy resistance | GameHour conditions | `set gamehour to 22` |
| **Sun-Kissed** | Outdoors 6am-8pm, not raining: heal 1 health and lose 1 rad a second | GameHour, IsInInterior, IsRaining | Heals in combat too? |
| **Storm Chasin'** | Rain or radstorm: +20 energy and radiation resistance, 5% faster | IsRaining or GetIsCurrentWeather(radstorm) | `fw 1c3d5e`; a radstorm counts? |
| **Shadow Dwellin'** | In the dark: +1 Agility, +1 Luck; 25% harder to see (once) | GetLightLevel < 50; Mod Detection Light | Night outdoors vs lit interiors |
| **Amphibious** | Breathe underwater; in water 10% faster, 25% less damage (once) | IsInWater; water breathing enchantment | Wading counts? |
| **Entrenched** | Crouched and still: +25 damage and energy resistance; steady aim (once) | IsSneaking, IsMoving | - |
| **Home Turf** | In your own settlements: +25 damage and energy resistance, +1 Charisma | LocationHasPlayerOwnedWorkshop | Sanctuary yes, Diamond City no |
| **Underdog's** | Enemies above your level deal 25% less and take 25% more (once) | LevelMinusPCLevel on the attacker / target tab | Low-level character vs a Deathclaw |
| **Glass Cannon** | 25% more damage dealt and taken (once) | Perk | - |
| **Ironclad** | Cannot be staggered, half limb damage (once); 5% slower per piece | Mod Incoming Stagger x0 | Knockdowns still happen? |
| **Glowing Heart** | +5 damage and energy resistance per 100 rads, up to +30 | GetValue(Rads) bands | - |
| **Overcharged** | Power armour: +2 Strength, +25 damage and energy resistance; fusion core drains faster | WornHasKeyword(ArmorTypePower); battery -0.2 | Drain rate sensible? |
| **Scavenger's** | Enemies you kill carry extra ammo and caps (once) | Add Leveled List On Death: vanilla Scrounger and Fortune Finder lists | - |
| **Radiatin' (Fire)**, **(Shock)**, **(Rads)**, **(Cryo)** | Aura: 5 fire / 5 electrical a second, 10 rads a second, 30% slower | Cloak (Overboss tesla coil pattern), radius 10; hostile and in combat only | Radius; neutrals and companions untouched |
| **Radiatin' (Healing)** | Companions and allies heal 3 health a second while fighting near you | Cloak, non-hostile targets | Heals settlers in a raid |
| **Radiatin' (Inferno)** (OP) | 30 fire a second, twice the radius | Cloak | - |
| **Phoenix** (PC/Xbox) | Once every 3 minutes, hit at 15% health or less: heal 40%, attacker set on fire (50) | Script `A1ALMMGEF_OnHitArmourEffect` in a perk ability | Two pieces still trigger once |
| **Static Charged** (PC/Xbox) | Anything that hits you: 20% chance to shock the attacker for 40, at most every 5 s | Same script | Works on ranged attackers |
| **Bloodthirsty** (PC/Xbox) | Every kill heals 10% | Script `A1ALMMGEF_OnKillArmourEffect` | - |
| **Momentum** (PC/Xbox) | Every kill: 20% faster and faster AP regeneration for 10 s | Same script | - |

On PlayStation the four scripted ones get the usual "needs a script" note from `tools/release/playstation.py`.

Ideas from the first draft that were dropped after the base-game research: Bulwark (Cavalier's already reduces
damage while blocking), Last Stand (Bolstering and Unyielding), Barbed (Punishing), Lone Wanderer's, Inspiring,
Pharmacist's, Iron Stomach, Core Saver, Executioner's (copies of vanilla perks), Berserker's (a vanilla weapon name),
Kinetic (Powered). Stealthy Armour (Doom1993) stays in section 7.

## 6. The 2016 legendaries that went missing

**Built 2026-10-13** as decided below, except: Shockingly Lobbin' uses Automatron's chain lightning explosion
(check it arcs from a grenade); the spawns are Random Minuteman, Random Children of Atom cultist, Random Robobrain and
Rust Devil Boss: the base game has no boss Assaultron (the Legendary Assaultron spawn stays the nearest). Flamin'
(the flamer stream on other weapons), MIRV's Impactin' (bursting on impact) and Concentratin' (Constant) (a constant
slow-time effect) need an in-game check. No Brakin' stays in section 7; Resettin' waits for the unequip test.

From the updated sheet: 23 entries of the 2016 list are not in the plugin. Two need nothing: the current Joker's
Gas and Backstabbing have no infinite ammo, so they already are the 2016 "(Limited)" versions.

| 2016 legendary (by) | Decision | Balanced / OP |
|---|---|---|
| Poisoner's Nimble (Erierth) | New weapon legendary: move 50% faster while aiming it, +25 poison damage over 5 seconds | Balanced |
| Zeus Crafted (Limited) (thobro2015, Cidion77) | Restore: the limited-ammo version, like every other Elemental | OP |
| Shockingly Lobbin' | Lobbin' (Lightning): the lobbed grenade bursts into the Tesla rifle's arc. Check the Tesla explosion works on a grenade projectile | Balanced |
| Gheed's Fortunate (forgrif) | Section 4 | Balanced |
| MIRV's Impactin' (DavidH) | MIRV Converted variant that splits on impact; keep the self-damage warning | OP |
| (Bottlecap) Mine layin' | Sticky Bottlecap Mine launchin' (vanilla bottlecap mine) | Balanced |
| One Man Punchin' (OnePunchMonk) | Weapon version of One Punch Man's for fists and melee: huge damage, enemies burst on death (Bloody Mess explosion) | OP |
| Speedy (Leylanee) | Speedy (25%), section 4 | Balanced |
| Speedily Jumpy (Leylanee) | Combined Speed and Jump Boosts (25%), section 4 | Balanced |
| Highly / Insanely Speedy (75%, 125%) | Not restored: 50 / 100 / 150% cover them | - |
| No Brakin' (H3xx) | Section 7, investigation | OP |
| Flamin' | Flamer conversion. Check: the flamer's projectile as an override on other weapons | Balanced if it works |
| Resettin' | Only if the unequip test (section 8) fails: it was a workaround for stuck speed and jump | - |
| Constant Slow Time | Concentratin' (Constant): time slows for as long as you aim. Check: an aiming condition on the slow-time spell | OP |
| Spawns (Maiqtheliar84): Assaultron Boss, Non-Mech Automatron RoboBrain, Minuteman, Legendary Rust Devil, Child of Atom cultist | Restore in the spawn system. The Minuteman behaves like the Brotherhood spawns (side by your standing); find each leveled list in FO4Edit | Spawning |
| Plated Titanium (FL4CKTROOPER) | Restore with his 2017 correction: 8x power armour health, regeneration only out of combat or below 20% health | OP |

## 7. The old requests

**Built 2026-10-13** (`tools/edits/gen_requests_21.py`; scripts in `source/User`), each sized against the base game:

| Request (by) | Built as | How | Balanced / OP |
|---|---|---|---|
| **Friendly Mirelurk Queen** (LandH) | Spawn: Creature/Friendly - Mirelurk Queen | Copy of LvlMirelurkQueen with its own factions (PlayerAllyFaction) and AI (Aggressive); no hatchling script | OP |
| **Stealthy Armour** (Doom1993) | Stealthy | Camouflaged (Crouch) perk, Stealth Boy field, shadowed/muffled while sneaking; +50 PER/LCK/AGI/END; power armour targeting HUD; Mod Pickpocket Chance 100. +5000 stats and remote pickpocketing left out (said in the description) | OP |
| **Brutish** (FL4CKTROOPER) | Brutish fixed | Its fire on hits: 100 + disintegration at 80% health -> 5, below 50% (Burning Rage's trigger); the melee-attacker burn removed | OP (as before) |
| **Fortune Finder explosions** (author) | Cap Showerin' (Frag / Fire / Cryo / Plasma / Nuclear) | Fortune Finder rank 4's own entry and vanilla script at 15%, its money-shot explosion with grenade damage and enchantments | Balanced; Nuclear OP |
| **PlayStation perks** (author) | "CLM Perk" magazines, PlayStation build only | `tools/release/playstation.py`: one BOOK per perk of the perk holotape (110), made at the chemistry station | - |
| **% of health damage** (ViscousVitriol) | Decimatin' | Script on hit: 10% of the target's base health | OP |
| **Hello Neighbour!** (stephen4000) | Hello Neighbour! | Script: GunnerFaction.SetPlayerEnemy(false) while worn | OP |
| **Advanced Titanium reflect** (FL4CKTROOPER) | Advanced Titanium | ReflectDamage 5 (the base game's Punishing mechanism) added; the 5% cut stays | OP (as before) |
| **CQC** (DarkArcher045) | CQC | Script: on "weaponFire", Weapon.Fire twice more, one round each | OP (+2 projectiles per shot) |
| **Jumper's** (Heavy & Ze Medic) | Jumper's | 50% explosion resistance, no fall damage; script: your own explosion gives a 4x jump for 3 s. The player cannot be thrown by physics, so the player jumps | Balanced |
| **Cinematic Excellence** (Tjonbrown24) | Cinematic Excellence | Script on kill (10%): slow time 2 s and third-person camera (first-person players only). No kill camera outside V.A.T.S. exists | Balanced |
| **Flight** (Wickedcircle, Heavy & Ze Medic) | Not built | Real flight needs F4SE; CLM does not use F4SE. Flyin' stays | - |
| **Healing Beam / God Creator** (Heavy & Ze Medic) | Healing Beam, God Creator | Medic's chain with no damage; heal 10 + 20/20/30 below 75/50/25% health; God Creator adds +1000 DR/ER for 10 s | Healing Beam balanced, God Creator OP |
| **DragonBlade** (AgentSmithGSOM) | DragonBlade | +200 damage; Jedi Reflexible Sprint ricochet; script: swing -> MoveTo the nearest hostile ahead within 15 m (2 s cooldown). No crosshair reference without F4SE | OP |
| **No Brakin'** (H3xx) | No Brakin' | Pain Train's cloak and its top-rank knockback (75 damage) with the power armour and perk conditions removed; sprinting only | OP |
| **Enraged** (author) | Enraged | +15% speed and +20% AnimationMult in combat; below 50% health a cloak burns (10/s) and frightens (Demoralize) nearby enemies | OP |
| **2LM / 3LM** (matzman666, Marelo) | README points to LEO | - | - |

Requests the author refused on purpose stay refused (GigaByteWide's Demon of the Divide set, "not in the spirit of
the mod").

## 8. Names and descriptions

**Done 2026-10-13** (`tools/edits/names_21.py`), with one rule from the author: many names are his own references or
the requester's words, so only clashes and plain typos changed. Kept on purpose: Gunslanger's, Convert Operator's,
Yamamoto's Mighty. The two Alien Nano-Coated became Alien Nano-Coated (+250) and Alien Enhanced Nano-Coated (+500),
the author's 2016 names.

In-game names that clash or are misspelt:

| Now | 2.1 |
|---|---|
| Havoc (Bullets / Plasma / Blue Laser / Red Laser), limited versions | Havoc (Bullets, Limited) etc.: today both versions share one name |
| Prometheus' Fiery, limited version | Prometheus' Fiery (Limited) |
| Alien Nano-Coated (the +250 one, `Armor_NanoCoated`) | Nano-Coated (the +500 one keeps Alien Nano-Coated; 2016: "Alien nano-coated" / "Alien Enhanced Nano-Coated") |
| Random Yaoi Guai, Random Legendary Yaoi Guai | Yao Guai |
| Convert Operator's | Covert Operator's |
| Silenced Eletrical Striker | Silenced Electrical Striker |
| Mightly Nearly Unbreakable | Mighty Nearly Unbreakable |
| Yamamoto's Mighty | Yamato's Mighty (YamatoNCC-1701's request) |
| Liar's Compedium | Liar's Compendium |
| Reaper's Embrace: / Hydra's Fanged. / Compressed Vortex Synthesized. | Without the stray colon and full stops |

Descriptions that say the wrong thing or nothing: Combined Speed and Jump Boosts (mentions jump only), Fisto's (no
number, and it boosts all weapon damage, not just fists), Nimble (no number), Santa Prisca's (+75 carry weight, not
75%), the Concentratin' family (trailing commas), plus typos (victom, laucher, re;pads). Run
`tools/audit/promises.py` after the edits so every description matches its effect.

## 9. Loose ends from 2.0

- [ ] Test in game: Speedy and Combined Speed and Jump reset on unequip (triage #1; Jumpy already passed). Decides
      whether Resettin' comes back.
- [ ] Toxic Blood, Slow Aim, Pain Train on armour, Silenced Electrical Striker in V.A.T.S.: 1.09 reported them not
      working. Find out whether they were renamed, removed or never built.
- [ ] `A1ALMQuestConfigInit` logs "Cannot clear a non-optional alias" once per new game: harmless; make the alias
      optional or drop the Clear().
- [ ] `docs/COMPLAINTS_TRIAGE.md` #16-18 still describe the DLC add-ons; 2.0 merged them back (four DLC, one
      plugin). Update the wording.

## 10. Order of work

1. Names and descriptions (section 8): done.
2. Balance moves (section 3) and the Fisto's fix: done.
3. Counterparts (section 4) and the missing 2016 legendaries (section 6): done.
4. New armour (section 5): built; in-game test outstanding.
5. Old requests (section 7): done.
6. Regenerate loot, picker and MCM; catalog and promise check: done. In-game test: `docs/TEST_CHECKLIST_2.1.md`.

## 11. Release

Same pipeline as 2.0 (`docs/release/BETHESDA_NET.md`): `package.py --version 2.1.0`, CK uploads (PC, Xbox page,
PlayStation), Nexus zip. Every new legendary gets a catalog entry, a loot pool (`tools/loot/plan.py`), a picker
family if it starts a new one, its requester in the changelog, and an in-game test checklist before release. The
changelog lists every legendary that moved to OP, and says how to get them back (carry the "Show OP" setting).
