# CLM 2.1 in-game test checklist (remaining)

What is left to test in 2.1: only what carries new risk: new scripts, new mechanics or new combinations of effects,
and the mascots. Legendaries that copy a working base-game or CLM record and only change numbers or conditions are
listed at the end as low risk, not needed. Tick each box once it works; write what went wrong under any that do not.
(Obsidian task list: `- [ ]` unticked, `- [x]` ticked.)

## Setup

- **Restart the game first:** the plugin was fixed again after the last session.
- **Test on ordinary enemies, not the arena:** the arena's holograms dispel effects and die on their own.
- To read a target's health: open the console, click the target, then `getav health` (without `player.`).
- Carry from the chemistry station (CLM Settings): **Free crafting**, **Show OP**, **Show variants**, **Show all
  legendaries** and **Show spawning legendaries**. Leave **Picker mode** off.
- **Debug recorder** is on (log: `Documents\My Games\Fallout4\Logs\Script\User\CLM.0.log`).
- **When done:** `python debug/build_recorder.py --game "D:/Steam/steamapps/common/Fallout 4" --remove`, then
  `python -m ack papyrus-log off` (in AgentCreationKit), and untick the recorder.

## 1. Re-test: fixed again

- [ ] **CQC** (it listened for the wrong event name): every shot is followed by two more, one round of ammo each (the log shows "extra rounds ... fired").
- [ ] **DragonBlade** (its enemy search found you yourself): swinging at an enemy ahead, 2-20 m away, dashes you to it, at most every 2 s (the log shows "swing: dashed").
- [ ] **Cinematic Excellence (CE Test)**: now on EVERY kill for this test: slow motion and third person for 2 s, then back to first person. It goes back to 1 kill in 10 before release.
- [ ] **Necromancer's**: the risen now walk to the nearest enemy and charge in (the log shows "hunting ..."); at most three; each body rises once.
- [ ] **Flamin'**: hold for the stream; targets now catch fire like the Incendiary legendary.
- [ ] **Resistance (All)**: "doesn't show": at the armour workbench, or no visible effect? It is in the plugin with working recipes. Its effect is a hidden perk, so nothing shows in the Pip-Boy; check it by taking poison or radiation with and without it.

## 2. Not tested yet

- [ ] **Cap Showerin' (Frag)** (one of five): about 15% of kills burst into caps and a frag explosion.
- [ ] **Jumper's** (PC/Xbox part): your own blast at your feet gives a 4x jump for 3 s.
- [ ] **No Brakin'** (OP): sprinting into enemies out of power armour knocks them down (75 damage).

## 3. Settings still to check

- [ ] **Holotape** (PC/Xbox): "Show all legendaries" / "Concise view" switch it; loot page: "Hidden legendaries drop too".
- [ ] **F4SE menu**: "Concise view" page has a switch per group; switches survive a save/load.
- [ ] **Loot mode, default**: hidden legendaries do not drop; with "Hidden legendaries drop too" they do.

## PlayStation build on PC (optional)

`python tools/release/playstation.py --test-install` (recorder off first); `--test-restore` puts the PC plugins back.
- [ ] Settings, Picker and the CLM Perk / CLM Loot Manual magazines work from the chemistry station; no holotape.
- [ ] A "needs a script" legendary (e.g. Phoenix) shows the PlayStation note and does nothing, without errors.

## Low risk, not needed (copies of working records, numbers or conditions changed)

- Variety: Midas' (Disintegratin' (Gold) + Scavenger's caps), Field Medic's (the Medic perk's entries).
- Mascots: Elemental Strikin' (Nature's Wrath), Double Tappin' (Two Shot's numbers).
- Number fixes: Scattering, Carbonatin', Shotgun Surgeon's (Trainee), Generically 80s Action Hero's, Thumpin',
  Burning, Acidic, Lesser Bleeding, Hinokagutsuchi, Rayden's Fury, Compacted, Refilling (25%), Beginner,
  Aim Stabilized (50%), Escapist's, Bullet Escapist, Fiery Operator's.
- Restored and requested: One Man Punchin', MIRV's Impactin', Sticky Bottlecap Mine launchin', the four new spawns,
  Plated Titanium, Stealthy, Healing Beam / God Creator, Brutish, Advanced Titanium, Fisto's stacking.
- Balanced counterparts, the moved-to-OP lists, renames and descriptions.

## Cut in testing

- **Breakin' and Enterin'**: the lock and terminal levels did not change; the game reads them from the Locksmith and
  Hacker perks themselves. Fiddlin' covers lockpicking.
- **Hello Neighbour!**: Gunners kept attacking, even made neutral to the player's faction.

## Passed so far

- Fixed and re-tested: Rallyin' (works, now out of combat too), Decimatin' (10% of full health per hit), Shockingly
  Lobbin' (electrical blast), Radiatin' (Elements), Energizin' (5% full AP refill), Singularity (implosion pulls),
  Disheartenin'. Cinematic Excellence's 10% roll was seen working in the log (9 misses, 1 hit).
- New mechanics: BioReactive (consistent explosions every hit), Concentratin' (Constant), Friendly Mirelurk Queen,
  Enraged.
- Mascots: Opportunist's, Vitality, Untouchable (Elements).
- Merged-group fix: Sun-Kissed and the merged groups show. Scripted armour: Phoenix, Bloodthirsty.
- Variety: Capitalist's, Cleavin', Disarmin', Terrifyin', Intimidatin', Radroachin', Shrinkin'.
- Recorder log works. Concise view: new game (now 82), Show all, old 2.0 save, CLM Group items. All 10
  spawning-default checks. Moved-to-OP spot check; owned gear keeps working.
- New armour: Night Owl's, Storm Chasin' (radstorm counts), Shadow Dwellin', Amphibious (wading and swimming both
  count), Entrenched, Home Turf, Underdog's, Glass Cannon, Ironclad, Glowing Heart, all six Radiatin' (Healing heals
  companions, not enemies), aura radius, Overcharged, Scavenger's.

## Before release

- Revert the CE Test: Cinematic Excellence back to 1 kill in 10 and its normal name (docs/PLAN_2.1.md).
