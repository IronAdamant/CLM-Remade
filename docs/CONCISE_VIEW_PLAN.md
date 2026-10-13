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

## Weapons: 38 shown, 53 hidden (of 91 balanced, not counting variants)

| Group | Feels alike because | Shown | Hidden in the concise view |
|---|---|---|---|
| More damage | flat damage up, with or without a fire-rate cost | **Hurtin' (50%)** | Hurtin' (25%), Hurtin' (100%), Devastating, Beginner |
| Situational damage | more damage under one condition (low health, sneaking, aiming, streaks, luck) | **Bloodlust** | Commando's, Widowmakin', Communicatin', Lucky Drawin' |
| Bleeding | damage over time from bleeding | **Greater Bleeding** | Lesser Bleeding, Woundingly Enraging, Woundingly Instigating |
| Poison and acid | poison or acid damage over time | **Greater Poisoning** | Acidic, Poisoner's Nimble |
| Fire on hit | sets targets alight | **Incendiary Striking** | Burning, Hinokagutsuchi, Fiery Operator's |
| Cold | freezes or slows targets | **Chilling** | Slightly Freezing |
| Lightning guns | turns the weapon into a lightning gun | **Harshly Shocking** | Jupiter's Wrathful |
| Energy damage | extra energy damage, targets turn to goo or ash | **Improved Plasma Infused** | Disintegratin' (Red) |
| Crippling | cripples limbs | **Crippling (100%)** | Crippingly Rapid |
| Handling | fire rate, reload and magazine | **Prototype Optimized** | Quicker, Compacted, Operator's Balanced, Operator's Enhanced Arsenal |
| Recoil and range | no recoil, longer range | **Recoilless** | Dangerously Recoilless, High Velocity Full Titanium |
| Armour piercing | ignores armour or cover | **Vatastically Penetrating** | VATS Penetratin' |
| Extra projectiles | more projectiles per shot | **Carbonatin'** | Scattering (Red Laser), Generically 80s Action Hero's, Shotgun Surgeon's (Trainee) |
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

Always shown (nothing similar among the balanced ones): Automatic (Furious), Nature's Wrath, Forcible, Rebounding (Bullet), Vampiric, Pre-Suppressed, Bloody Messy, Cinematic Excellence, Lorenzo's Legendary Artificial, Salvaged Assaultron's Beaming, Moby-Dick's, Heavily Ordnanced, Pyrotechnical (Minutemen Flare), Shavka's Explosive Striking, Rayden's Fury.

## Armour: 45 shown, 49 hidden (of 94 balanced, not counting variants)

| Group | Feels alike because | Shown | Hidden in the concise view |
|---|---|---|---|
| Damage resistance | flat damage resistance | **Ballistic Protection (Basic)** | Ballistic Protection (Light) |
| Steady healing | health over time | **Regenerative (Slow)** | Sun-Kissed |
| Emergency healing | heals you when your health is low | **Auto-Medical** | Aid Patch, Phoenix |
| Healing on a kill | kills heal or speed you up | **Bloodthirsty** | Momentum |
| Resistances | less damage from one damage type | **Resistance (Explosion)** | Resistance (Acid), Resistance (Electric), Resistance (Limb Damage), Resistance (Poison), Resistance (Radiation) |
| Speed | faster movement | **Speedy (25%)** | Speedy (10%), Combined Speed and Jump Boosts (10%), Combined Speed and Jump Boosts (25%) |
| Moving while aiming | faster while aiming | **Nimble (50%)** | Nimble (25%) |
| Jumping | higher jumps | **Jumpy (50%)** | Jumpy (10%), Jumpy (25%), Jumpy (100%), Jumper's |
| Slow time | time slows when you aim, crit or sprint | **Concentratin' (Brief)** | Focused (Brief), Critically Concentratin', Chronos' |
| Steady aim | steadier aim | **Aim Stabilized (100%)** | Aim Stabilized (50%), Critically Hurtin' |
| Damage (armour) | more weapon damage from armour | **Fisto's (20%)** | Brotherhood of Steel's Damaging, Institute's Damaging, Minutemen's Damaging, Railroad's Damaging, Glass Cannon |
| Stealth | harder to detect | **Stealth** | Escapist's, Shadow Dwellin' |
| Seeing enemies | highlights or senses enemies | **Tactical Highlighting** | Sensin', Tracker's Focused Sight, Highlighting |
| Melee reactions | melee attackers suffer an effect | **Untouchable (Freeze)** | Untouchable (Disarm), Untouchable (Fire), Untouchable (Frenzy), Untouchable (Knockdown), Untouchable (Poison), Untouchable (Rad), Untouchable (Shock), Untouchable (Spook), Static Charged |
| Avoiding hits | chance to take no damage or bounce shots back | **Generic 80s Action Hero's** | Bullet Escapist |
| Damaging auras | enemies near you take damage or slow down | **Radiatin' (Fire)** | Radiatin' (Cryo), Radiatin' (Rads), Radiatin' (Shock) |
| Exploding kills | kills burst into caps and an explosion | **Cap Showerin' (Frag)** | Cap Showerin' (Cryo), Cap Showerin' (Fire), Cap Showerin' (Plasma) |

Always shown (nothing similar among the balanced ones): Santa Prisca's, Enlightened, Fiddlin', Gheed's Fortunate, Scavenger's, Cat Tailed, Waterbreathing, Impact Landing (Basic), Lucky Hittin' (10%), Murderous (x3), Marathon Runnin', Quick Hands (50%), Refilling (10%), Titanium, Battery Regeneratin' (Slow), Overcharged, Punching (Radiation), Shavka's Explosive Striking, Radiatin' (Healing), Glow, Amphibious, Entrenched, Home Turf, Night Owl's, Storm Chasin', Glowing Heart, Ironclad, Underdog's.

Two armour records are both called "Highlighting" (Weapon_Highlighting is an armour mod); both are in the Seeing
enemies group, so 151 legendaries are hidden in all (53 weapon, 50 armour, 48 spawns).

## Still to do

- Settings texts: rewritten 2026-10-14 as one system, "how you get legendaries" and "what the workbench shows",
  each setting saying what you get without it (chemistry station, holotape, MCM, Nexus, Bethesda.net, readme).
- In-game test: `docs/TEST_CHECKLIST_2.1.md`, "Concise view".
- Requester spelling ggg3336 / gggg336: not found online; kept as ggg3336 in the credits.
