# CLM 2.1 in-game test checklist (remaining)

The PC testing of 2.1 is done (see "Passed" at the end). What is left: an optional quick look at Necromancer's without
its cap, and the PlayStation build, tried on PC. Tick each box once it works; write what went wrong under any that do
not. (Obsidian task list: `- [ ]` unticked, `- [x]` ticked.)

## 1. PC: optional quick look

- [ ] **Necromancer's**: no limit on how many risen stand at once now; each body still rises only once.

## 2. PlayStation build, tried on PC: passed (2026-10-17)

PlayStation mods may not have scripts or assets, so the PlayStation plugin differs (your spreadsheet's "Platforms" tab
lists every difference).

**Setup**
1. Close the game. In the AgentCreationKit folder, switch the Papyrus log off: `python -m ack papyrus-log off`.
2. Untick **CLM - Debug Recorder.esp** and **CLM - MCM.esp** (both use PC scripts; a PlayStation player has neither).
3. In the CLM-Remade folder: `python tools/release/playstation.py --test-install` (swaps in the PlayStation plugin).
4. Start the game the normal way (not through F4SE). A save from this session is fine.

**Checks**
- [x] **No holotapes**: none in the inventory, none to craft. Settings are made at the chemistry station (CLM Settings) and work as on PC.
- [x] **CLM Perk magazines** (chemistry station, CLM Perks): make one and read it; the perk is added (the Wasteland Survival Guide Vault Boy plays) and its recipe disappears. Fixed: reading one crashed the game (the perks were not made like vanilla magazine perks). Make a new one: one made before the fix may still crash.
- [x] **Loot mode**: with "Loot mode" carried, make the **CLM Loot Manual** (CLM Settings) and read it; legendary enemies then drop CLM legendaries.
- [x] **Left out**: the six new laser colours, the five new Disintegratin' colours and the Kellogg spawn are not at the workbench.
- [x] **Changed**: Midas' leaves ordinary ash (not gold); BioReactive explodes on killing hits only; Vampiric heals on hits but not on killing blows; Auto-Medical / Aid Patch regenerate health while low without using a stimpak. Their descriptions say so.
- [x] **Needs a script** (e.g. Phoenix, Necromancer's, CQC): the description carries the PlayStation note and the legendary does nothing, without errors or crashes.
- [x] **Concise view and spawns** work as on PC: one legendary per group, spawns hidden until "Show spawning legendaries".

**When done**
1. `python tools/release/playstation.py --test-restore` (puts the PC plugin back).
2. Tick CLM - MCM.esp again. For more PC testing later: tick CLM - Debug Recorder.esp and
   `python -m ack papyrus-log on`; otherwise remove the recorder:
   `python debug/build_recorder.py --game "D:/Steam/steamapps/common/Fallout 4" --remove`.

## Cut in testing

- **Breakin' and Enterin'**: the lock and terminal levels did not change; the game reads them from the Locksmith and
  Hacker perks themselves. Fiddlin' covers lockpicking.
- **Hello Neighbour!**: Gunners kept attacking, even made neutral to the player's faction.

## Passed on PC

- **Scripted legendaries**: CQC (real bursts of the gun's own shot), DragonBlade (slides to the enemy, +200 damage),
  Cinematic Excellence (1 kill in 10), Necromancer's (ash copies that fight, never hostile), Jumper's (4x jump for
  3 s), Momentum (+20% speed on a kill), Phoenix, Bloodthirsty, Decimatin', Cleavin', Radroachin', Shrinkin',
  Singularity (implosion pulls), BioReactive (explodes on every hit).
- **Fixed in testing and re-tested**: Rallyin' (works out of combat too), Disheartenin', Energizin' (5% full AP
  refill), Shockingly Lobbin' (electrical blast), Flamin' (automatic stream that burns), Radiatin' (Elements).
- **New mechanics**: Concentratin' (Constant), Friendly Mirelurk Queen, Enraged, Cap Showerin', No Brakin',
  Resistance (All), Capitalist's, Disarmin', Terrifyin', Intimidatin'.
- **Mascots**: Opportunist's, Vitality, Untouchable (Elements); Elemental Strikin' and Double Tappin' are copies of
  working records.
- **Settings**: concise view (new game 82, Show all, old 2.0 save, CLM Group items, merged groups), all 10
  spawning-default checks, holotape and F4SE menu, loot mode (hidden legendaries drop only with "Hidden legendaries
  drop too" or Show all), moved-to-OP spot check, owned gear keeps working.
- **New armour**: Night Owl's, Sun-Kissed, Storm Chasin' (radstorm counts), Shadow Dwellin', Amphibious (wading and
  swimming both count), Entrenched, Home Turf, Underdog's, Glass Cannon, Ironclad, Glowing Heart, all six Radiatin'
  (Healing heals companions, not enemies), Overcharged, Scavenger's.
- **Not tested, low risk** (copies of working records with numbers or conditions changed): Midas', Field Medic's,
  the number fixes (Scattering, Carbonatin', Shotgun Surgeon's (Trainee), Generically 80s Action Hero's, Thumpin',
  Burning, Acidic, Lesser Bleeding, Hinokagutsuchi, Rayden's Fury, Compacted, Refilling (25%), Beginner, Aim
  Stabilized (50%), Escapist's, Bullet Escapist, Fiery Operator's), One Man Punchin', MIRV's Impactin', Sticky
  Bottlecap Mine launchin', the four new spawns, Plated Titanium, Stealthy, Healing Beam / God Creator, Brutish,
  Advanced Titanium, Fisto's stacking, the balanced counterparts, the moved-to-OP lists, renames and descriptions.
