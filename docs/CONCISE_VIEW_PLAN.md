# Concise view (2.1)

A Nexus user found too many legendaries that feel the same. The workbench now shows one **balanced** legendary per
group of similar effects; the rest of each group is hidden until the player shows it. Nothing is deleted: hidden
legendaries stay in the plugin and gear that has them keeps working. Variants (Show variants) and OP legendaries
(Show OP) are not part of this: their own settings already handle them. Built by `tools/config/concise.py` from
`tools/config/concise_groups.py` (edit the groups there and re-run it).

Author's decisions (2026-10-14): show whole groups instead of requesters (no requester names in the game);
existing saves keep everything shown, as before; loot mode gets an option for the hidden legendaries.

## Settings

| Setting | Off (default for new games) | On |
|---|---|---|
| **CLM Setting: Show all legendaries** | Concise view: one legendary per group | Every legendary, as before 2.1 |
| **CLM Group: <group>** (category CLM Groups, one per group) | The group shows its representative | The whole group |
| **CLM Setting: Hidden legendaries drop too** (loot mode) | Hidden legendaries neither drop nor unlock | They drop and unlock too |

- Chemistry station (every platform), configuration holotape (Show all; drop setting on the loot page; PC and Xbox),
  F4SE menu (Settings page switches, "Concise view" page with a switch per group).
- **Existing saves**: a start-game quest (PC/Xbox) gives "Show all legendaries" to any save past the Vault 111 exit,
  so nothing disappears after updating. New games start concise. PlayStation cannot run it: players there craft "Show
  all legendaries" to keep the full list (say so in the PlayStation description).
- **Loot mode**: two drop chains. The concise chain leaves out the hidden legendaries; the full chain (as before) is
  used while "Hidden legendaries drop too" or "Show all legendaries" is on. Drop rates per kill are the same.
- **Spawns**: each creature's Legendary and Boss spawns form one group (48 spawns); the plain Random spawns stay.

## Mascots

Where no member stood for its group, a new balanced legendary does (`tools/edits/gen_mascots_21.py`). A mascot
that triggers on several conditions is on more often than a member that needs one, so its numbers are lower.

| Mascot | Group | Effect |
|---|---|---|
| **Opportunist's** | Situational damage | +40% damage on a sneak attack, against a full-health target, or below half health; one at a time |
| **Elemental Strikin'** | Elemental hits | 10% each for 20 fire, cryo, poison and electrical damage over 2 s (Nature's Wrath without its fire rate) |
| **Double Tappin'** | Extra projectiles | +1 projectile at full damage, 30% wider spread (the base game's Two Shot) |
| **Resistance (All)** | Resistances | 25% less from all six damage types (the single ones: 50%) |
| **Vitality** | Healing | 1 health a second, 3 below 25% health |
| **Untouchable (Elements)** | Melee reactions | Melee attackers: 20% each to be frozen, burned, shocked (PC and Xbox, like every Untouchable) |
| **Radiatin' (Elements)** | Damaging auras | 2 fire and 2 shock a second, 3 rads a second, 15% slower |

Merged: Bleeding, Poison and acid, Fire on hit, Cold, Energy damage and Crippling into Elemental hits; Speed,
Moving while aiming and Jumping into Movement (shown: Combined Speed and Jump Boosts (25%)); Steady and Emergency
healing into Healing.

Counts (new game, balanced, main variants): 149 shown (38 weapon, 45 armour, 66 spawns) against 317 with Show all.

## Weapons: 31 shown, 63 hidden

| Group | Feels alike because | Shown | Hidden in the concise view |
|---|---|---|---|
| More damage | flat damage up, with or without a fire-rate cost | **Hurtin' (50%)** | Hurtin' (25%), Hurtin' (100%), Devastating, Beginner |
| Situational damage | more damage under one condition (low health, sneaking, full-health targets, aiming, streaks, luck) | **Opportunist's** | Bloodlust, Commando's, Widowmakin', Communicatin', Lucky Drawin' |
| Elemental hits | extra fire, cold, poison, acid, energy, shock or bleeding damage on hit, or crippled limbs | **Elemental Strikin'** | Greater Bleeding, Lesser Bleeding, Woundingly Enraging, Woundingly Instigating, Greater Poisoning, Acidic, Poisoner's Nimble, Incendiary Striking, Burning, Hinokagutsuchi, Fiery Operator's, Chilling, Slightly Freezing, Improved Plasma Infused, Disintegratin' (Red), Crippling (100%), Crippingly Rapid, Nature's Wrath, Rayden's Fury |
| Lightning guns | turns the weapon into a lightning gun | **Harshly Shocking** | Jupiter's Wrathful |
| Handling | fire rate, reload and magazine | **Prototype Optimized** | Quicker, Compacted, Operator's Balanced, Operator's Enhanced Arsenal |
| Recoil and range | no recoil, longer range | **Recoilless** | Dangerously Recoilless, High Velocity Full Titanium |
| Armour piercing | ignores armour or cover | **Vatastically Penetrating** | VATS Penetratin' |
| Extra projectiles | more projectiles per shot | **Double Tappin'** | Carbonatin', Scattering (Red Laser), Generically 80s Action Hero's, Shotgun Surgeon's (Trainee) |
| Self-loading ammo | the weapon makes its own ammo | **Keltas' Flawed Factorium** | Synthesised Flawed Factorium |
| Explosive rounds | rounds explode on hit | **BioReactive Explosive (Explosive)** | Thumpin' |
| Missiles | turns the weapon into a missile launcher | **Rocketin'** | Rainman's, Seekin', Splinterin' |
| Grenades and mines | lobs grenades or lays mines | **Lobbin' (Frag Grenade)** | Lobbin' (Cryo Mine), Lobbin' (Frag Mine), Lobbin' (Plasma Mine), Lobbin' (Pulse Mine), Sticky Frag Mine launchin', Sticky Bottlecap Mine launchin' |
| Traps | throws traps | **Trappin' (Bear Trap)** | Trappin' (Caltrop) |
| Laser conversions | the same conversion in seven colours | **Energized (Red Laser)** | Energized (Deep Blue Laser), Energized (Gold Laser), Energized (Green Laser), Energized (Orange Laser), Energized (Pink Laser), Energized (Purple Laser) |
| Weather | changes the weather | **Weather Altering (Rain)** | Weather Altering (Clear), Weather Altering (RadStorm) |
| Frenzy | turns enemies on each other | **Joker's Gas** | Backstabbing |
| Knockback | pushes targets away | **Pushing (Ranged)** | Majestically Swaggering |
| Healing others | shots heal | **Medic's** | Healing Beam |

Always shown (nothing similar among the balanced ones): Automatic (Furious), Forcible, Rebounding (Bullet), Vampiric, Pre-Suppressed, Bloody Messy, Cinematic Excellence, Lorenzo's Legendary Artificial, Salvaged Assaultron's Beaming, Moby-Dick's, Heavily Ordnanced, Pyrotechnical (Minutemen Flare), Shavka's Explosive Striking.

## Armour: 42 shown, 56 hidden

| Group | Feels alike because | Shown | Hidden in the concise view |
|---|---|---|---|
| Damage resistance | flat damage resistance | **Ballistic Protection (Basic)** | Ballistic Protection (Light) |
| Healing | health over time, faster or automatic when it runs low | **Vitality** | Regenerative (Slow), Sun-Kissed, Auto-Medical, Aid Patch, Phoenix |
| Healing on a kill | kills heal or speed you up | **Bloodthirsty** | Momentum |
| Resistances | less damage from one damage type | **Resistance (All)** | Resistance (Acid), Resistance (Electric), Resistance (Explosion), Resistance (Limb Damage), Resistance (Poison), Resistance (Radiation) |
| Movement | faster, higher jumps, faster while aiming | **Combined Speed and Jump Boosts (25%)** | Speedy (10%), Speedy (25%), Combined Speed and Jump Boosts (10%), Nimble (25%), Nimble (50%), Jumpy (10%), Jumpy (25%), Jumpy (50%), Jumpy (100%), Jumper's |
| Slow time | time slows when you aim, crit or sprint | **Concentratin' (Brief)** | Focused (Brief), Critically Concentratin', Chronos' |
| Steady aim | steadier aim | **Aim Stabilized (100%)** | Aim Stabilized (50%), Critically Hurtin' |
| Damage (armour) | more weapon damage from armour | **Fisto's (20%)** | Brotherhood of Steel's Damaging, Institute's Damaging, Minutemen's Damaging, Railroad's Damaging, Glass Cannon |
| Stealth | harder to detect | **Stealth** | Escapist's, Shadow Dwellin' |
| Seeing enemies | highlights or senses enemies | **Tactical Highlighting** | Sensin', Tracker's Focused Sight, Highlighting |
| Melee reactions | melee attackers suffer an effect | **Untouchable (Elements)** | Untouchable (Freeze), Untouchable (Disarm), Untouchable (Fire), Untouchable (Frenzy), Untouchable (Knockdown), Untouchable (Poison), Untouchable (Rad), Untouchable (Shock), Untouchable (Spook), Static Charged |
| Avoiding hits | chance to take no damage or bounce shots back | **Generic 80s Action Hero's** | Bullet Escapist |
| Damaging auras | enemies near you take damage or slow down | **Radiatin' (Elements)** | Radiatin' (Fire), Radiatin' (Cryo), Radiatin' (Rads), Radiatin' (Shock) |
| Exploding kills | kills burst into caps and an explosion | **Cap Showerin' (Frag)** | Cap Showerin' (Cryo), Cap Showerin' (Fire), Cap Showerin' (Plasma) |

Always shown (nothing similar among the balanced ones): Santa Prisca's, Enlightened, Fiddlin', Gheed's Fortunate, Scavenger's, Cat Tailed, Waterbreathing, Impact Landing (Basic), Lucky Hittin' (10%), Murderous (x3), Marathon Runnin', Quick Hands (50%), Refilling (10%), Titanium, Battery Regeneratin' (Slow), Overcharged, Punching (Radiation), Shavka's Explosive Striking, Radiatin' (Healing), Glow, Amphibious, Entrenched, Home Turf, Night Owl's, Storm Chasin', Glowing Heart, Ironclad, Underdog's.

Two armour records are both called "Highlighting"; both are in the Seeing enemies group, so 169 legendaries are
hidden in all (33 groups: 121 weapon and armour, 48 spawns).

## Still to do

- Settings texts: rewritten 2026-10-14 as one system, "how you get legendaries" and "what the workbench shows",
  each setting saying what you get without it (chemistry station, holotape, MCM, Nexus, Bethesda.net, readme).
- In-game test: `docs/TEST_CHECKLIST_2.1.md`, "Concise view".
- Requester spelling ggg3336 / gggg336: not found online; kept as ggg3336 in the credits.
