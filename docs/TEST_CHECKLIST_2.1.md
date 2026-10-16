# CLM 2.1 in-game test checklist (remaining)

What is left to test in 2.1: only what carries new risk: new scripts, new mechanics or new combinations of effects,
and the mascots. Legendaries that copy a working base-game or CLM record and only change numbers or conditions are
listed at the end as low risk, not needed. Tick each box once it works; write what went wrong under any that do not.
(Obsidian task list: `- [ ]` unticked, `- [x]` ticked.)

## Setup

- **Restart the game first:** the plugin was fixed again after the last session.
- **Test in the open world, not the arena or a test cell:** a room without a navmesh leaves NPCs unable to walk (the
  risen stood still and "hunted" one target on a rock for a minute), and the arena's holograms dispel effects.
- Carry from the chemistry station (CLM Settings): **Free crafting**, **Show OP**, **Show variants**, **Show all
  legendaries** and **Show spawning legendaries**. Leave **Picker mode** off.
- **Debug recorder** is on (log: `Documents\My Games\Fallout4\Logs\Script\User\CLM.0.log`).
- **When done:** `python debug/build_recorder.py --game "D:/Steam/steamapps/common/Fallout 4" --remove`, then
  `python -m ack papyrus-log off` (in AgentCreationKit), and untick the recorder.

## 1. Re-test

- [ ] **Necromancer's** (the copy now spawns invisible, joins your side, then fades in): it is never hostile, not even for a moment.
- [ ] **Loot mode, default**: in the F4SE menu, turn **Show all legendaries OFF** (it was on during the last test, and it lets hidden legendaries drop on purpose). Then, with loot mode on and "Hidden legendaries drop too" off, loot a few legendary enemies: no hidden legendaries (tell me which ones you pick up; the log lists them). Turn "Hidden legendaries drop too" on: they can drop.

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

- Round 6: Necromancer's ash copies fight (apart from the hostile moment, fixed above), Jumper's ends after 3 s, Momentum (+20% speed on a kill, seen in the log), DragonBlade slides without a loading screen.
- Round 5: CQC fires real bursts, Cinematic Excellence back to 1 in 10, holotape and F4SE menu settings.
- Round 4: CQC bursts fire (see the open question), DragonBlade dashes (loading screen fixed above), Cinematic
  Excellence (CE Test), Flamin' (stream and burning), Resistance (All), Cap Showerin', No Brakin'.
- Fixed and re-tested: Rallyin' (works, now out of combat too), Decimatin' (10% of full health per hit), Shockingly
  Lobbin' (electrical blast), Radiatin' (Elements), Energizin' (5% full AP refill), Singularity (implosion pulls),
  Disheartenin'.
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
