# CLM 2.1 in-game test checklist (remaining)

What is left to test in 2.1: new or changed things only, one item per family (a family's other variants share its
records, so one working means all work). Tick each box once it works; write what went wrong under any that do not.
(Obsidian task list: `- [ ]` unticked, `- [x]` ticked.)

## Setup

- **Load again first:** the plugin was fixed after the last session (merged-group fix), so restart the game.
- Carry from the chemistry station (CLM Settings): **Free crafting**, **Show OP**, **Show variants**, **Show all
  legendaries** and **Show spawning legendaries**. Leave **Picker mode** off.
- PC/Xbox only = needs a script; on PlayStation it shows a "needs a script" note and does nothing.
- **Debug recorder** is on (log: `Documents\My Games\Fallout4\Logs\Script\User\CLM.0.log`). When reporting a
  problem, say roughly what you did and when.
- **When done:** `python debug/build_recorder.py --game "D:/Steam/steamapps/common/Fallout 4" --remove`, then
  `python -m ack papyrus-log off` (in AgentCreationKit), and untick the recorder.
- Console: `set gamehour to 12` (day); `player.damageav health 300`; `tgm` off while testing damage;
  `player.setlevel 5` / back (Terrifyin', Intimidatin').

## 1. The merged-group fix (found in testing)

- [ ] **Sun-Kissed** (Balanced) now at the armour workbench: outdoors, 6am-8pm, dry weather: +1 health and -1 rad a second; indoors / night / rain: nothing.
- [ ] One more from a merged group shows with Show all: e.g. **Jumpy (50%)** or **Greater Bleeding**.

## 2. Scripted armour (PC/Xbox), one per script

- [ ] **Phoenix** (on-hit script; Static Charged shares it): hit at 15% health or less: heal 40%, attacker set on fire; then nothing for 3 minutes.
- [ ] **Bloodthirsty** (on-kill script; Momentum shares it): every kill heals 10%.

## 3. Variety: new kinds of effect (15)

- [ ] **Energizin'** (Balanced): your AP goes up 3 per hit. If it does not, tell me (it may need a script).
- [ ] **Singularity** (OP, experimental): every hit pulls nearby enemies towards the target. If they are pushed away instead, tell me.
- [ ] **Rallyin'** (Balanced): a companion's resistances go up near you (`getav damageresist` on them). Does it multiply with several pieces?
- [ ] **Breakin' and Enterin'** (Balanced): without Locksmith you can pick Advanced locks; without Hacker, hack Advanced terminals. It never lowers what your own perks allow.
- [ ] **Disheartenin'** (Balanced): hit enemies deal about 25% less damage for 5 s.
- [ ] **Capitalist's** (Balanced): more damage the more caps you carry (+10% per 1,000, up to +50%).
- [ ] **Cleavin'** (Balanced, PC/Xbox): melee hits also hurt enemies around the target (40); never you or companions; guns: nothing extra.
- [ ] **Disarmin'** (Balanced): enemies sometimes drop their weapon.
- [ ] **Terrifyin'** (Balanced): enemies 5+ levels below you run away when hit; equal or stronger ones keep fighting.
- [ ] **Midas'** (Balanced): enemies hit before they die turn to gold dust; kills carry extra caps.
- [ ] **Intimidatin'** (Balanced): enemies 10+ levels below you flee when near you.
- [ ] **Field Medic's** (Balanced): stimpaks heal more, RadAway removes more.
- [ ] **Necromancer's** (OP, PC/Xbox): kills rise ~1.5 s later, fight for you for 60 s, then drop dead; named characters stay dead.
- [ ] **Radroachin'** (OP, PC/Xbox): sometimes a target becomes a radroach carrying its loot; named characters unaffected.
- [ ] **Shrinkin'** (OP): targets shrink to half size for 10 s and hit softer, then grow back to normal (not smaller).

## 4. Mascots (7)

- [ ] **Opportunist's** (weapon): +60% on a sneak attack, a full-health target, or below half health; never more than +60%.
- [ ] **Elemental Strikin'** (weapon): 25% chance each of fire / cryo / poison / electrical bursts.
- [ ] **Double Tappin'** (weapon): two projectiles per shot, about double damage, wider spread.
- [ ] **Resistance (All)** (armour): 25% less acid, electrical, explosion, poison, radiation and limb damage.
- [ ] **Vitality** (armour): 1 health a second, 3 below 25% health.
- [ ] **Untouchable (Elements)** (armour, PC/Xbox): melee attackers 33% each frozen, burned or shocked.
- [ ] **Radiatin' (Elements)** (armour): nearby enemies take a little fire, shock and rads and slow down.

## 5. Today's fixes

- [ ] **BioReactive Explosive (Explosive)** (one of six): explodes on every hit on an enemy, not only on kills; never on walls or water (the log shows "exploded" per hit).
- [ ] **Scattering (Red Laser)** (one of the extra-projectile fixes): clearly harder hits than the plain weapon.
- [ ] **Thumpin'**: full fire rate, small explosions on impact.
- [ ] **Burning**: every hit sets the target alight.
- [ ] **Escapist's**: below 30% health, sprinting makes you invisible.
- [ ] **Bullet Escapist**: sprinting at full health, some shots bounce off.
- [ ] **Aim Stabilized (50%)**: scope sway clearly less than without it.
- [ ] **Refilling (25%)** shows under its new name.

## 6. Restored 2016 legendaries and old requests, one per family

- [ ] **Shockingly Lobbin'**: the lobbed grenade bursts into chain lightning (the Lobbin' family's riskiest one).
- [ ] **Flamin'**: your weapon shoots a flamer stream.
- [ ] **Concentratin' (Constant)** (OP): time slows while aiming, returns when you stop.
- [ ] **One Man Punchin'** (OP): fists and melee x50, enemies burst; guns unaffected.
- [ ] **MIRV's Impactin'** (OP): bursts on impact, not mid-air.
- [ ] **Sticky Bottlecap Mine launchin'**: sticky bottlecap mines.
- [ ] **Spawn: Random Minuteman** (one of the four new spawns): friendly or hostile by your Minutemen standing.
- [ ] **Spawn: Friendly Mirelurk Queen** (OP): fights for you, ignores you and companions; no hatchlings.
- [ ] **Plated Titanium** (OP): 8x power armour health; +1 health and -1 rad a second out of combat.
- [ ] **Stealthy** (OP): crouched you are cloaked and unseen even moving; every pickpocket succeeds.
- [ ] **Cap Showerin' (Frag)** (one of five): about 15% of kills burst into caps and a frag explosion.
- [ ] **Healing Beam**: heals instead of hurting, more the more hurt the target is.
- [ ] **Jumper's**: 50% less explosion damage, no fall damage; your own blast at your feet gives a 4x jump (PC/Xbox).
- [ ] **No Brakin'** (OP): sprinting into enemies out of power armour knocks them down (75 damage).
- [ ] **Enraged** (OP): faster in combat; below half health nearby enemies burn and flee. Speed-up too much?
- [ ] **Decimatin'** (OP, PC/Xbox): each hit takes 10% of the target's full health.
- [ ] **Hello Neighbour!** (OP, PC/Xbox): Gunners neutral while worn, hostile again when removed.
- [ ] **CQC** (OP, PC/Xbox): three-round bursts, one round of ammo each.
- [ ] **DragonBlade** (OP, PC/Xbox): swinging at an enemy ahead dashes you to it, at most every 2 s.
- [ ] **Cinematic Excellence** (PC/Xbox): about 1 kill in 10 in slow motion and third person for 2 s.
- [ ] **Brutish** (changed): no fire above half health; below half, 5 fire per hit.
- [ ] **Fisto's stacking** (changed): Fisto's (20%) and (50%) on two pieces give +50%, not x1.8.

## 7. Settings still to check

- [ ] **Holotape** (PC/Xbox): "Show all legendaries" / "Concise view" switch it; loot page: "Hidden legendaries drop too".
- [ ] **F4SE menu**: "Concise view" page has a switch per group; switches survive a save/load.
- [ ] **Loot mode, default**: hidden legendaries do not drop; with "Hidden legendaries drop too" they do. OP drops still come.

## PlayStation build on PC (optional)

`python tools/release/playstation.py --test-install` (recorder off first); `--test-restore` puts the PC plugins back.
- [ ] Settings, Picker and the CLM Perk / CLM Loot Manual magazines work from the chemistry station; no holotape.
- [ ] **BioReactive** explodes on killing hits only; **Midas'** leaves ordinary ash; descriptions say so.
- [ ] A "needs a script" legendary (e.g. Phoenix) shows the PlayStation note and does nothing, without errors.

## Passed so far

- Recorder log works. Concise view: new game (83), Show all, old 2.0 save, CLM Group items. All 10 spawning-default
  checks. Moved-to-OP spot check; owned gear keeps working.
- New armour: Night Owl's, Storm Chasin' (radstorm counts), Shadow Dwellin', Amphibious (wading and swimming both
  count), Entrenched, Home Turf, Underdog's, Glass Cannon, Ironclad, Glowing Heart, all six Radiatin' (Healing heals
  companions, not enemies), aura radius, Overcharged, Scavenger's.
- Skipped as tested before 2.1: the balanced counterparts, the moved-to-OP lists, renames and descriptions.
