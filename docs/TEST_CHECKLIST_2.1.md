# CLM 2.1 in-game test checklist

Everything 2.1 added or changed, for in-game testing. Tick each box once it works; write what went wrong under any
that do not. (Obsidian task list: `- [ ]` unticked, `- [x]` ticked.)

## Setup

- Carry the settings items from the chemistry station (CLM Settings): **Free crafting**, **Show OP**, **Show
  variants**. Spawning and perk-style legendaries show by default. Leave **Picker mode** off.
- PC/Xbox only = needs a script; on PlayStation it shows a "needs a script" note and does nothing.
- Handy console commands: `set gamehour to 22` (night) / `to 12` (day); `fw 1c3d5e` (radstorm; for rain,
  `help rain 4` lists the rain weathers to `fw`); `player.modav rads 300` / `player.restoreav rads 1000`;
  `player.damageav health 300`; `tgm` off while testing damage; `coc SanctuaryExt` (Home Turf);
  `player.setlevel 5` (Underdog's; undo with your old level).

## New armour: CLM's own (23)

### Surroundings
- [ ] **Night Owl's** (Balanced): 8pm-6am +1 Perception, +1 Agility, +10 DR/ER; nothing by day (`set gamehour`).
- [ ] **Sun-Kissed** (Balanced): outdoors, 6am-8pm, dry weather: +1 health and -1 rad a second. Indoors / night / rain: nothing.
- [ ] **Storm Chasin'** (Balanced): in rain AND in a radstorm: +20 energy and radiation resistance, 5% faster. Check that the radstorm counts.
- [ ] **Shadow Dwellin'** (Balanced): in the dark: +1 Agility, +1 Luck, harder to spot. Lit area: nothing.
- [ ] **Amphibious** (Balanced): breathe underwater; in water 10% faster, 25% less damage. Does wading count, or only swimming?
- [ ] **Entrenched** (Balanced): crouched and still: +25 DR/ER, steady scope. Moving: nothing.
- [ ] **Home Turf** (Balanced): in a settlement you own (Sanctuary): +25 DR/ER, +1 Charisma. Diamond City / unowned settlement: nothing.

### Grit
- [ ] **Underdog's** (Balanced): enemies above your level deal 25% less and take 25% more. Same-level enemies: normal.
- [ ] **Glass Cannon** (Balanced): +25% damage dealt and taken. Two pieces = still 25%.
- [ ] **Ironclad** (Balanced): no stagger, half limb damage; 5% slower per piece. Do knockdowns still happen?
- [ ] **Glowing Heart** (Balanced): +5 DR/ER per 100 rads, up to +30 at 600 (`player.modav rads`).

### Radiatin' (auras)
- [ ] **Radiatin' (Fire)** (Balanced): enemies near you burn, 5 a second. Companions, settlers and neutrals untouched.
- [ ] **Radiatin' (Shock)** (Balanced): 5 electrical a second to nearby enemies.
- [ ] **Radiatin' (Rads)** (Balanced): 10 rads a second to nearby enemies.
- [ ] **Radiatin' (Cryo)** (Balanced): nearby enemies 30% slower.
- [ ] **Radiatin' (Healing)** (Balanced): companions and allies heal 3 a second while fighting near you; enemies are not healed.
- [ ] **Radiatin' (Inferno)** (OP): 30 fire a second, twice the radius.
- [ ] Aura radius feels right (about 10 ft; Inferno 20).

### Power armour and scavenging
- [ ] **Overcharged** (Balanced): in power armour +2 Strength, +25 DR/ER; fusion core drains faster. Is the drain sensible? Out of power armour: nothing.
- [ ] **Scavenger's** (Balanced): killed enemies carry extra ammo and a few caps.

### PC/Xbox only
- [ ] **Phoenix** (Balanced): hit at 15% health or less: heal 40%, attacker set on fire (50); then nothing for 3 minutes. Two pieces still trigger once.
- [ ] **Static Charged** (Balanced): hits on you have a 20% chance to shock the attacker for 40, at most every 5 s; works on ranged attackers too.
- [ ] **Bloodthirsty** (Balanced): every kill heals 10%.
- [ ] **Momentum** (Balanced): every kill: 20% faster and faster AP regeneration for 10 s.

## Balanced counterparts (18)

- [ ] **Hurtin' (25%)** (Balanced): +25% damage.
- [ ] **Hurtin' (50%)** (Balanced): +50% damage.
- [ ] **Speedy (10%)** (Balanced): +10% speed; resets when taken off.
- [ ] **Speedy (25%)** (Balanced): +25% speed; resets when taken off.
- [ ] **Combined Speed and Jump Boosts (10%)** (Balanced): +10% speed and jump; resets when taken off.
- [ ] **Combined Speed and Jump Boosts (25%)** (Balanced): +25% speed and jump; resets when taken off.
- [ ] **Nimble (25%)** (Balanced): 25% faster while aiming.
- [ ] **Ballistic Protection (Light)** (Balanced): +25 damage resistance.
- [ ] **Regenerative (Slow)** (Balanced): 1 health a second, 2 out of combat.
- [ ] **Resistance (Acid)** (Balanced): 50% less acid damage.
- [ ] **Resistance (Electric)** (Balanced): 50% less electrical damage.
- [ ] **Resistance (Explosion)** (Balanced): 50% less explosion damage.
- [ ] **Resistance (Limb Damage)** (Balanced): 50% less limb damage.
- [ ] **Resistance (Poison)** (Balanced): 50% less poison damage.
- [ ] **Resistance (Radiation)** (Balanced): 50% less radiation.
- [ ] **Gheed's Fortunate** (Balanced): buy 20% cheaper, sell 20% higher.
- [ ] **Shotgun Surgeon's (Trainee)** (Balanced): +3 pellets, 30% wider spread; no knock-back or armour piercing.
- [ ] **Keltas' Quick Draw Factorium** (Balanced): about one empty magazine in four refills itself (not with Scrounger rank 4).

## The 2016 legendaries, restored (16)

- [ ] **Poisoner's Nimble** (Balanced; Erierth): 75% faster while aiming; hits poison for 25 over 5 s.
- [ ] **Zeus Crafted (Limited)** (OP): Zeus Crafted with +50 ammo capacity instead of never-ending.
- [ ] **Shockingly Lobbin'** (Balanced): lobbed grenade bursts into chain lightning. Does the Automatron lightning explosion work from a grenade?
- [ ] **MIRV's Impactin'** (OP; DavidH): MIRV bursts on impact, not mid-air. Safe at range?
- [ ] **Sticky Bottlecap Mine launchin'** (Balanced): sticky bottlecap mines, bottlecap model and explosion.
- [ ] **One Man Punchin'** (OP; OnePunchMonk): fists and melee x50 damage, enemies burst; guns unaffected.
- [ ] **Flamin'** (Balanced): your weapon shoots a flamer stream. Does the stream work on other weapons?
- [ ] **Concentratin' (Constant)** (OP): time slows while aiming, returns when you stop. Does a constant slow-time effect work?
- [ ] **Spawn: Random Minuteman** (Maiqtheliar84): friendly or hostile by your Minutemen standing.
- [ ] **Spawn: Random Children of Atom cultist** (Maiqtheliar84): friendly or hostile by standing.
- [ ] **Spawn: Random Robobrain** (Maiqtheliar84): a regular, non-Automatron robobrain, hostile.
- [ ] **Spawn: Rust Devil Boss** (Maiqtheliar84): hostile Rust Devil boss.
- [ ] **Plated Titanium** (OP; FL4CKTROOPER): 8x power armour health; out of combat +1 health a second; -1 rad a second.
- [ ] **Speedy (25%)** / **Combined Speed and Jump Boosts (25%)** (Leylanee's): same items as in the counterparts above.
- [ ] **Gheed's Fortunate** (forgrif's): same item as in the counterparts above.
- [ ] Joker's Gas and Backstabbing still work (they are the 2016 "(Limited)" versions).

## The old requests (17 new, 2 changed)

- [ ] **Spawn: Friendly Mirelurk Queen** (OP; LandH): spawns a Queen that fights for you and ignores you and your companions; no hatchlings.
- [ ] **Stealthy** (OP; Doom1993): crouched you are cloaked, quiet and unseen even moving; +50 PER/LCK/AGI/END; enemies highlighted; every pickpocket succeeds.
- [ ] **Cap Showerin' (Frag)** (Balanced): about 15% of kills burst into caps with a frag explosion (150).
- [ ] **Cap Showerin' (Fire)** (Balanced): caps and a fire burst (60, sets alight).
- [ ] **Cap Showerin' (Cryo)** (Balanced): caps and a freezing burst (50).
- [ ] **Cap Showerin' (Plasma)** (Balanced): caps and a plasma burst (100).
- [ ] **Cap Showerin' (Nuclear)** (OP): caps and a nuclear burst (700). Keep your distance.
- [ ] **Healing Beam** (Balanced; Heavy & Ze Medic): heals 10, more the more hurt the target is (up to 80); no damage to anyone. Do companions mind being shot?
- [ ] **God Creator** (OP; Heavy & Ze Medic): Healing Beam plus 10 s of near-invulnerability on the target.
- [ ] **Jumper's** (Balanced; Heavy & Ze Medic): 50% less explosion damage, no fall damage; PC/Xbox: after your own explosion hits you, a 4x jump for 3 s.
- [ ] **No Brakin'** (OP; H3xx): out of power armour, sprinting into enemies knocks them down and deals 75. Allies untouched.
- [ ] **Enraged** (OP): faster in combat; below half health nearby enemies burn and flee. Does the AnimationMult speed-up feel right, or is it too much?
- [ ] **Decimatin'** (OP, PC/Xbox; ViscousVitriol): each hit takes 10% of the target's full health (try it on a minigun and a Deathclaw).
- [ ] **Hello Neighbour!** (OP, PC/Xbox; stephen4000): Gunners neutral while worn, hostile again when removed.
- [ ] **CQC** (OP, PC/Xbox; DarkArcher045): each shot followed by two more; one round of ammo each. In V.A.T.S. too?
- [ ] **DragonBlade** (OP, PC/Xbox; AgentSmithGSOM): +200 damage; swinging at an enemy ahead (up to ~15 m) dashes you to it, at most every 2 s; ricochet while blocking or sprinting. No dash through walls?
- [ ] **Cinematic Excellence** (Balanced, PC/Xbox; Tjonbrown24): about 1 kill in 10: slow motion and third person for 2 s, then back to first person. Third-person players: no camera switch.
- [ ] **Brutish** (changed; FL4CKTROOPER): no fire on hits above half health; below half, 5 fire damage per hit; no more 100-point burns on melee attackers; self-heal and resistances unchanged.
- [ ] **Advanced Titanium** (changed; FL4CKTROOPER): reflects 5% of melee damage, on top of the 5% damage cut.
- [ ] **PlayStation perk magazines** (PlayStation build only): `python tools/release/playstation.py --test-install`, then chemistry station > CLM Perks: make a magazine, read it, the perk is added; the recipe disappears once you have it. Restore with `--test-restore`.

## Concise view

- [ ] **New game**: the workbench shows one legendary per group (e.g. Hurtin' (50%) but not Hurtin' (25%) / (100%); Lobbin' (Frag Grenade) but no mines). The plain Random spawns show, Legendary/Boss spawns do not.
- [ ] **CLM Setting: Show all legendaries** (chemistry station, CLM Settings): everything is back; drop it and the concise view returns.
- [ ] **Old save** (made with 2.0): after loading, "Show all legendaries" is in the inventory and nothing disappeared (PC/Xbox).
- [ ] **CLM Group** item (chemistry station, CLM Groups), e.g. "Grenades and mines (Weapon)": the whole group shows; its description lists what it adds. The group items are not offered while Show all is carried.
- [ ] **Holotape** (PC/Xbox): "Show all legendaries" / "Concise view" entries switch it; loot page: "Hidden legendaries drop too" / "Only the concise view drops".
- [ ] **F4SE menu**: Settings page "Show all legendaries" and "Hidden legendaries drop too"; "Concise view" page with a switch per group; switches survive a save/load.
- [ ] **Loot mode, default**: hidden legendaries never drop and their holotape does not unlock them; with "Hidden legendaries drop too" (or Show all) they drop and unlock.
- [ ] **Picker mode** still works on top (a family picked shows only its concise members unless Show all / its group is on).
- [ ] An item already carrying a hidden legendary keeps it.

### Mascots (the shown legendary of their group)
- [ ] **Opportunist's** (Balanced): +40% on a sneak attack, on a full-health target, or below half health; never more than +40% when two apply.
- [ ] **Elemental Strikin'** (Balanced): random fire / cryo / poison / electrical bursts, no fire-rate change.
- [ ] **Double Tappin'** (Balanced): two projectiles per shot, about double damage, wider spread.
- [ ] **Resistance (All)** (Balanced): 25% less acid, electrical, explosion, poison, radiation and limb damage.
- [ ] **Vitality** (Balanced): 1 health a second, 3 below 25% health.
- [ ] **Untouchable (Elements)** (Balanced, PC/Xbox): melee attackers sometimes frozen, burned or shocked.
- [ ] **Radiatin' (Elements)** (Balanced): nearby enemies take a little fire, shock and rads and slow down.

## Changed existing legendaries

### Moved to OP: recipe hidden without Show OP, visible with it, owned gear still works
- [ ] Spot check: drop the **Show OP** item; the legendaries below disappear from the workbench; carry it again and they come back.
- [ ] Weapons: Hurtin' (150%), Hurtin' (200%), Devil's Due, Hustlin', Rapid Fire (100%), Quicker (75%), Quicker (100%), Gunslanger's
- [ ] Weapons: Four Shot, High Explosive, Slayer's, Silent Slayer's, Bird Shootin'
- [ ] Weapons: Shotgun Surgeon's I and II (Basic, Institute, Laser, Plasma: all 8), Shockgun Surgeon's
- [ ] Weapons: Thor Blessed, Overchargin', Alien-Tech'd, Keltas' Perfect Factorium, Synthesised Rapid / Specialised / Perfect Factorium
- [ ] Weapons: Lobbin' (Nuke Mine), Sticky Nuke Mine launchin', BioReactive Explosive (Nuclear), Shavka's Explosive Striking (Nuclear)
- [ ] Armour: Fisto's (100%), Fisto's (150%), Ballistic Protection (Advanced), (Master-crafted), Advanced Titanium, Tradin' Jack's, Regenerative
- [ ] Armour: Speedy (50%), (100%), (150%); Combined Speed and Jump Boosts (50%), (100%), (150%); Nimble (100%), (150%); Jumpy (150%)
- [ ] Armour: Lucky Hittin' (25%), Sadistic Brawlers, Untouchable (Paralyzed), Untouchable (Pacify), Punching (Paralyze), Devil's Due, Shavka's Explosive Striking (Nuclear)
- [ ] An item already carrying one of these keeps working after loading a save.

### Back to balanced
- [ ] **Majestically Swaggering**: shows without Show OP.
- [ ] **Aim Stabilized (100%)**: shows without Show OP.

### Other changes
- [ ] **Fisto's stacking**: wear Fisto's (20%) and (50%) on two pieces: damage is +50%, not x1.8. One piece alone still works.
- [ ] **Factional Damaging** (BoS / Institute / Minutemen / Railroad) still +25% (they share Fisto's (25%) perk).
- [ ] **Camouflaged (Always) / (Crouch)**: only one of each at the workbench now; an item that has the hidden duplicate still works.
- [ ] **Renamed**: Havoc (Bullets / Plasma / Blue Laser / Red Laser, Limited), Prometheus' Fiery (Limited), Alien Enhanced Nano-Coated (+500), Random (Legendary) Yao Guai spawns, Silenced Electrical Striker, Mighty Nearly Unbreakable, Liar's Compendium, Reaper's Embrace, Hydra's Fanged, Compressed Vortex Synthesized.
- [ ] **Descriptions**: Fisto's, Nimble, Combined Speed and Jump Boosts, Santa Prisca's (+75 carry weight) read right.
- [ ] **Loot mode**: OP drops still come (the OP pool is now two halves of 128 under one list); new legendaries can drop as loose mods.
- [ ] **Picker / MCM**: new families Surroundings, Grit, Radiatin', Cap Showerin', Spawn: Minutemen, Spawn: Children of Atom have selectors and MCM switches.
- [ ] Speedy and Combined Speed and Jump reset speed and jump when unequipped (decides whether Resettin' comes back).
