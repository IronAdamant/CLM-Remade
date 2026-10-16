# Changelog

## 2.1.0 (in progress)

A balance pass measured against the base game's own legendaries, new armour, the 2016 legendaries that went
missing, and the feature requests of 2016-17 that 1.09 left as "not possible" or "no time".

### Changed
- **Concise view: one legendary per group of similar effects.** Too many legendaries felt alike, so the workbench
  now shows one balanced legendary per group (33 groups: "More damage", "Elemental hits", "Grenades and mines",
  "Melee reactions"...) and hides the rest of each group: 120 legendaries, plus the Legendary and Boss tiers of the
  spawns (48). A new game shows 82 legendaries instead of 316. Nothing is removed and gear you own keeps working.
  - Where no single legendary stood for its group, a new balanced one does (records only unless noted):
    **Opportunist's** (+60% damage on a sneak attack, against a full-health target or below half health, one at a
    time), **Elemental Strikin'** (Nature's Wrath's elements without its fire rate), **Double Tappin'** (the base
    game's Two Shot), **Resistance (All)** (25% less from all six damage types), **Vitality** (1 health a second, 3
    below 25% health), **Untouchable (Elements)** (melee attackers: 33% each to freeze, burn, shock; PC and Xbox, like
    the other Untouchables), **Radiatin' (Elements)** (a little of each aura).
  - **CLM Setting: Show all legendaries** shows everything, as before 2.1. **Saves made before 2.1 get it
    automatically** (PC and Xbox); on PlayStation, craft it at the chemistry station to keep the full list.
  - **CLM Group** items (chemistry station, category CLM Groups) show one whole group; the F4SE menu has a switch per
    group (page "Concise view").
  - Loot mode: hidden legendaries do not drop unless **CLM Setting: Hidden legendaries drop too** (or Show all) is on.
- **Balanced now means "no stronger than the base game's strongest of its kind"** (Two Shot's damage, Rapid's fire
  rate, Sentinel's and Bolstering on armour). 56 legendaries above that moved to **OP**; with "Show OP" off their
  recipes are hidden. **Gear you already own keeps working.** To craft them again, carry the Show OP setting.
  - Weapons: Hurtin' (150%), (200%); Devil's Due; Hustlin'; Rapid Fire (100%); Quicker (75%), (100%); Gunslanger's;
    Four Shot; High Explosive; Slayer's; Silent Slayer's; Bird Shootin'; all eight Shotgun Surgeon's and Shockgun
    Surgeon's; Thor Blessed; Overchargin'; Alien-Tech'd; Keltas' Perfect Factorium; Synthesised Rapid, Specialised
    and Perfect Factorium; the nuclear ones: Lobbin' (Nuke Mine), Sticky Nuke Mine launchin', BioReactive Explosive
    (Nuclear), Shavka's Explosive Striking (Nuclear).
  - Armour: Fisto's (100%), (150%); Ballistic Protection (Advanced), (Master-crafted); Advanced Titanium; Tradin'
    Jack's; Regenerative; Speedy (50-150%); Combined Speed and Jump Boosts (50-150%); Nimble (100%), (150%); Jumpy
    (150%); Lucky Hittin' (25%); Sadistic Brawlers; Untouchable (Paralyzed), (Pacify); Punching (Paralyze); Devil's
    Due; Shavka's Explosive Striking (Nuclear).
  - Back to balanced: **Majestically Swaggering** and **Aim Stabilized (100%)**.
  - Each family that lost its balanced members got smaller balanced tiers (see New).
- **Fisto's no longer multiplies across armour pieces:** only your best Fisto's piece counts. Before, different
  tiers on different pieces multiplied ((20%) to (150%) on five pieces was about 11 times the damage).
- **Camouflaged (Always) and (Crouch)** appeared twice at the workbench under the same names; the duplicate pair's
  recipes are gone (the legendaries stay, so existing gear keeps working).
- **Names:** legendaries that shared a name with another now differ: Havoc (Bullets / Plasma / Blue Laser / Red Laser,
  Limited), Prometheus' Fiery (Limited), Alien Enhanced Nano-Coated (the +500 one, its 2016 name). Typos fixed: Yao
  Guai, Silenced Electrical Striker, Mighty Nearly Unbreakable, Liar's Compendium, and the stray ":" or "." after
  Reaper's Embrace, Hydra's Fanged and Compressed Vortex Synthesized.
- **Brutish** (FL4CKTROOPER's fix): its punches burned for 100 fire damage at 80% health or less, plus 100 on anyone
  who hit it in melee. Now, as FL4CKTROOPER asked, its hits do 5 fire damage, and only below half health, when the
  Burning Rage effect kicks in. The rest of Brutish is unchanged.
- **Advanced Titanium** now also reflects 5% of melee damage, as FL4CKTROOPER originally asked (1.09 shipped it with the
  5% damage cut only).
- **Descriptions** now say what the legendary does: Fisto's (the number, all weapons, best piece only), Nimble and
  Combined Speed and Jump Boosts (the numbers; Combined mentioned only jumping), Santa Prisca's (+75 carry weight,
  not 75%), plus typos and stray commas.

- **Weak and broken balanced legendaries brought up to the base game's** (reported on Nexus; baselines per hit:
  Wounding 25 bleed, Incendiary 15 fire, Poisoner's 30 poison, Explosive +15 splash, Two Shot +100% damage with its
  extra projectile, since an extra projectile alone only splits the same damage):
  - Extra projectiles that added no damage: **Scattering** (all three) +100% like Two Shot; **Carbonatin'** and
    **Shotgun Surgeon's (Trainee)** +50%; **Generically 80s Action Hero's** (four shot) +100%.
  - **Thumpin'** no longer halves the fire rate (it was the base game's Explosive at half speed).
  - **Aim Stabilized (50%)** was only 10% (x1.1): now 50%.
  - **Escapist's** only worked at exactly 15% health (practically never): now below 30%. **Bullet Escapist**
    worked above 30% health, the opposite of its text: now whenever you sprint.
  - Damage over time: **Burning** always burns for 15 (was a 10% chance), the hotter burn and ash stay one hit in
    ten; **Acidic** 10 -> 30 acid; **Lesser Bleeding** 12 -> 20; **Hinokagutsuchi** 10 -> 25; **Rayden's Fury** 25
    -> 75 on critical hits; **Elemental Strikin'** 10% -> 20% per element (Nature's Wrath keeps 10%, with its
    faster fire rate).
  - Concise-view mascots raised to their group to match: **Elemental Strikin'** 25% per element, **Untouchable
    (Elements)** 33% per element, **Opportunist's** +60%.
  - **Compacted** +20% -> +50% magazine; **Refilling** 10% -> 25%, now named Refilling (25%); **Beginner** 2% ->
    10% (its recoil part made recoil worse; now less).
  - Stronger than their text said: **Fiery Operator's** burned for 150, now the 15 it promises; **Generically 80s
    Action Hero's** (weapon) cut damage taken standing still by 70%, now the 30% it promises. **Greater Poisoning**
    keeps its 90 poison over 10 seconds; its text said 9.
- **BioReactive Explosive (all six) now explodes on every hit** (reported on Nexus): it ran vanilla Fortune Finder's
  script, which only sets off its explosion if the target is already dead, so since 1.09 it exploded on killing hits
  only. A CLM script now explodes on every hit that lands on an actor (still never on walls or water). Singularity had
  the same problem and the same fix. PC and Xbox; on PlayStation they still explode on killing hits only (noted in
  their descriptions).
- **Necromancer's** (2.1 testing): no limit on how many risen stand at once (author's decision: it is OP); each
  body still rises only once.
- **Fixed (during 2.1 testing, round 6):** Necromancer's: resurrected bodies came back with their combat AI not
  working and stood still. Now the body crumbles to ash (its loot stays in the ash pile, as with a laser kill) and a
  fresh copy rises in its place (appearing already on your side), fights for you for 60 seconds, then crumbles to an
  empty ash pile. Jumper's and
  Momentum no longer leave their boost on in a save where the armour was already worn. DragonBlade's dash slides you
  there instead of teleporting (fix_testing6_21.py).
- **Fixed (during 2.1 testing, round 5):** Jumper's jump and Momentum's rush never applied: the timed spell they cast
  on you changed nothing (the debug recorder showed the jump height untouched). They now give you an ability for 3 /
  10 seconds instead, the same effects Jumpy and Speedy use. DragonBlade's dash no longer shows a loading screen.
  CQC's extra rounds were the gun's plain projectile; the burst now makes you fire the gun itself (the AI's fire
  action), so they are the real, modded shot (fix_testing5_21.py).
- **Fixed (during 2.1 testing, round 4):** CQC listened for "weaponFire", but the event is "WeaponFire" (names are
  case-sensitive), so no burst ever fired. DragonBlade's enemy search returned you yourself; it now looks for enemies
  ahead by type, as Cleavin' does. Necromancer's risen walk to their target and charge in. Flamin' now burns its
  targets (the base game's Incendiary). **Hello Neighbour!** was cut: Gunners kept attacking even made neutral to
  your faction (fix_testing4_21.py).
- **Fixed (during 2.1 testing, round 3):** CQC, DragonBlade and Cinematic Excellence did nothing: copied from an
  armour-type mod and turned into weapon mods, their enchantment had become a "Speed" property (and DragonBlade's
  +200 damage too). Hello Neighbour! now also makes Gunners neutral to the player's faction. Flamin' is fully
  automatic (hold for the stream). Shockingly Lobbin' bursts for 100 damage (the Lightning Gun's chain explosion did
  nothing from a grenade). Radiatin' (Elements) raised to 3 fire / 3 shock / 5 rads a second, 20% slower.
  Necromancer's raises each body once. Rallyin' only worked on allies in combat; now whenever they are near you
  (fix_testing3_21.py).
- **Fixed (during 2.1 testing):** Rallyin' and Disheartenin' (and Shrinkin's weaker hits) did nothing: they now
  change the value while the effect lasts and give it back after (Rallyin's aura now refreshes a 3-second
  effect). Necromancer's risen now join your side, go for the nearest enemy, and no limit on how many stand at once (an OP legendary; the game counts their kills as yours, so they raise more). Breakin' and Enterin' was cut: the lock and
  terminal levels come from the Locksmith and Hacker perks themselves (fix_testing2_21.py). Singularity's pull did nothing (an explosion cannot pull): a script now pulls nearby enemies in (PC and
  Xbox). tools/edits/fix_testing_21.py.
- **Fixed (during 2.1 testing):** merging the concise-view groups left the old groups' globals behind, and 23
  legendaries (Sun-Kissed, Jumpy, Nimble, the bleed/poison/fire/cold ones...) could not show even with Show all.
  tools/config/concise.py now prunes them and drops any condition on a group that no longer exists.
- **Spawning legendaries are hidden by default** (new setting **CLM Setting: Show spawning legendaries**): a new
  game starts with weapons and armour only. "Show all legendaries" shows them too, so saves from before 2.1
  (which get it on PC and Xbox) keep them; "Hide spawning legendaries" still hides them in every case. Loot
  mode is unchanged: a spawn found as loot can be used. Picker mode's spawn families appear once spawns show.
- **Removed the two "ALM: A - Test" slots** (weapon and armour): the author's 1.09-era scratch legendaries for trying
  effects out, never meant for players.

### New
- **Jumpy (10%)** and **Jumpy (25%)** (requested by Doom1993): smaller jump boosts below the 50% the family started at.
- Plain effects without extras or long descriptions (requested by ViscousVitriol):
  - **Rapid Fire (100%):** your weapon fires twice as fast, nothing else (a Quicker variant).
  - **Rapid Hurtin'** (OP): ten times the damage and twice the fire rate.
  - **Crippling (100%):** every hit cripples the limb it hits.
  - "10x damage" alone is Hurtin' (1000%), added in 2.0.
- **Bloodlust** (requested by FL4CKTROOPER): the lower your health, the harder you hit: +10 damage for every 10% of
  health lost, up to +90.
- **Blitzkrieg** (OP, requested by FL4CKTROOPER): +60% V.A.T.S. accuracy and range, V.A.T.S. attacks cost 95% less
  Action Points, double critical damage, critical meter fills twice as fast.
- **Nature's Wrath** (requested by Sereda Hawke): each hit has a 10% chance each of extra fire, cryo, poison and
  electrical damage; fires 25% faster. 1.09 called it impossible: it needs no random projectile after all.
- **Staminator** (armour, OP, requested by Wardogg83): sprinting, power attacks, holding your breath and reloading in
  V.A.T.S. cost no Action Points, V.A.T.S. attacks almost none; breathe underwater.
- **Weapon Mastery** (armour, OP, mademost's "OP weapon skills"): +20% critical chance, +100% critical damage, faster
  critical meter, bash criticals, steady scopes, cheaper V.A.T.S. No damage bonus. Faster weapon draw and scope zoom
  are not possible without scripts.
- **Balanced tiers** for the families that moved to OP: **Hurtin' (25%)**, **(50%)**; **Speedy (10%)**, **(25%)**
  (Leylanee's 2016 Speedy); **Combined Speed and Jump Boosts (10%)**, **(25%)** (Leylanee's Speedily Jumpy);
  **Nimble (25%)**; **Ballistic Protection (Light)** (+25); **Regenerative (Slow)** (1 health a second, 2 out of
  combat); **Resistance (Acid / Electric / Explosion / Limb Damage / Poison / Radiation)**: 50% less, where the
  Immunities are 100%; **Gheed's Fortunate** (forgrif's 2016 request: buy 20% cheaper, sell 20% higher);
  **Shotgun Surgeon's (Trainee)** (+3 pellets); **Keltas' Quick Draw Factorium** (one empty magazine in four refills
  itself).
- **The 2016 legendaries that went missing before 1.09**, back:
  - **Poisoner's Nimble** (Erierth): move 75% faster while aiming; hits poison for 25 damage over 5 seconds.
  - **Zeus Crafted (Limited)** (OP; thobro2015, Cidion77): Zeus Crafted with +50 ammo capacity instead of never-ending.
  - **Shockingly Lobbin'**: a lightning grenade launcher; the grenade bursts into Automatron's chain lightning.
  - **MIRV's Impactin'** (OP; DavidH): a MIRV that bursts on impact instead of in mid-air.
  - **Sticky Bottlecap Mine launchin'** (the 2016 "(Bottlecap) Mine layin'").
  - **One Man Punchin'** (OP; OnePunchMonk): fists and melee weapons do 50 times the damage and enemies burst apart.
  - **Flamin'**: your weapon shoots a flamer stream.
  - **Concentratin' (Constant)** (OP; the 2016 "Constant Slow Time"): time slows for as long as you aim.
  - Spawns (Maiqtheliar84): **Random Minuteman** and **Random Children of Atom cultist** (friendly or hostile by your
    standing), **Random Robobrain**, **Rust Devil Boss**. (The base game has no boss Assaultron to spawn: the
    Legendary Assaultron spawn is the nearest.)
  - **Plated Titanium** (OP; FL4CKTROOPER): 8 times power armour health, heals 1 health a second out of combat and
    removes 1 rad a second.
  - Joker's Gas and Backstabbing already are the 2016 "(Limited)" versions. Highly / Insanely Speedy are covered by
    Speedy (50-150%).
- **The 2016-17 requests 1.09 called impossible**, sized against the base game (balanced unless marked OP):
  - **Friendly Mirelurk Queen** spawn (OP; LandH): a Mirelurk Queen that fights on your side (no hatchlings).
  - **Stealthy** (OP; Doom1993): crouch and you are muffled, shadowed and cloaked; +50 Perception, Luck, Agility and
    Endurance; power armour targeting; every pickpocket succeeds. (+5000 stats and pickpocketing from 1000 feet are not
    possible.)
  - **Cap Showerin' (Frag / Fire / Cryo / Plasma; Nuclear is OP)** (the author's idea): 15% of your kills burst into a
    Fortune Finder shower of caps that is also a real explosion.
  - **Healing Beam** (Heavy & Ze Medic): shots heal 10, up to 80 the more hurt the patient is, and hurt no one.
    **God Creator** (OP): the same, plus 10 seconds of near-invulnerability for whoever you heal.
  - **Jumper's** (Heavy & Ze Medic): 50% less explosion damage, no fall damage; your own explosions give you a
    huge jump for 3 seconds, so you can rocket-jump (the jump is PC and Xbox only).
  - **No Brakin'** (OP; H3xx): Pain Train's top rank without power armour.
  - **Enraged** (OP; the author's idea): faster in combat; below half health, nearby enemies burn and flee in fear.
  - PC and Xbox only (scripts): **Decimatin'** (OP; ViscousVitriol): each hit takes 10% of the target's health.
    **Hello Neighbour!** (OP; stephen4000): Gunners are not hostile while you wear it. **CQC** (OP; DarkArcher045):
    three-round bursts. **DragonBlade** (OP; AgentSmithGSOM): +200 damage, dash to the enemy ahead when you swing,
    ricochet bullets while blocking or sprinting. **Cinematic Excellence** (Tjonbrown24): one kill in ten in slow
    motion from the third-person camera (a real kill camera outside V.A.T.S. is not possible).
  - **PlayStation perks** (the author's note): the perk holotape needs scripts, so on PlayStation every CLM perk is a
    "CLM Perk" magazine made at the chemistry station (category CLM Perks). Reading it adds the perk; removing one
    is not possible there. Fixed in testing: reading one (or the CLM Loot Manual) crashed the game; their perks are
    now made like vanilla magazine perks (non-playable, with the Wasteland Survival Guide animation), and picking
    one up no longer shows Live & Love's message.
  - Not built: real flight (it needs F4SE, which CLM does not use; Flyin' stays), and second and third CLM
    legendary slots (they would mean editing every weapon and armour record; LEO's extra slots hold LEO's own
    effects).
- **14 legendaries for kinds of effect CLM lacked** (weakening and controlling enemies, backing companions, utility;
  `tools/edits/gen_variety_21.py`). Balanced, every platform unless marked:
  - **Disheartenin'**: enemies you hit deal 25% less damage for 5 seconds.
  - **Energizin'**: 5% of hits refill your Action Points completely (the base game's own refill effect, so it works
    on PlayStation too; a fixed amount per hit would need a script).
  - **Capitalist's**: +10% damage per 1,000 caps you carry, up to +50%.
  - **Cleavin'** (PC and Xbox): melee and unarmed hits also strike every other enemy within 3 metres for 40 damage.
  - **Disarmin'**: 10% chance a hit knocks the target's weapon out of its hands.
  - **Terrifyin'**: enemies 5+ levels below you flee for 10 seconds when hit.
  - **Midas'**: kills turn to gold dust (as Disintegratin' (Gold); ordinary ash on PlayStation) and carry a handful of
    extra caps.
  - **Rallyin'** (armour): companions and allies near you get +15 damage and energy resistance and +10% damage.
  - **Intimidatin'** (armour): enemies 10+ levels below you flee instead of fighting.
  - **Field Medic's** (armour): stimpaks and RadAway work 30% better; counts once.
  - OP: **Necromancer's** (PC and Xbox: kills rise and fight for you for 60 seconds), **Radroachin'** (PC and Xbox:
    10% chance a hit turns the target into a radroach carrying its loot), **Shrinkin'** (targets shrink to half size
    and deal half damage for 10 seconds; the shrinking is PC and Xbox), **Singularity** (hits implode, pulling
    enemies in; experimental).
- **23 new armour legendaries**, CLM's own: effects the base game does not have, sized against its legendaries
  (Sentinel's, Bolstering, Unyielding...). Balanced unless marked. Value effects (resistances, SPECIAL, speed,
  healing) add up per piece as the base game's do; the perk-based parts count once however many pieces carry them.
  - **Surroundings:** **Night Owl's** (8pm-6am: +1 Perception and Agility, +10 damage and energy resistance),
    **Sun-Kissed** (outdoors by day, dry weather: heal 1 health and lose 1 rad a second), **Storm Chasin'** (rain or
    radstorm: +20 energy and radiation resistance, 5% faster), **Shadow Dwellin'** (in the dark: +1 Agility and Luck,
    25% harder to see), **Amphibious** (breathe underwater; in water 10% faster and 25% less damage),
    **Entrenched** (crouched and still: +25 damage and energy resistance, steady aim), **Home Turf** (in your own
    settlements: +25 damage and energy resistance, +1 Charisma).
  - **Grit:** **Underdog's** (enemies above your level deal 25% less and take 25% more), **Glass Cannon** (25% more
    damage dealt and taken), **Ironclad** (cannot be staggered, half limb damage, 5% slower per piece), **Glowing
    Heart** (+5 damage and energy resistance per 100 rads, up to +30).
  - **Radiatin' (Fire / Shock / Rads / Cryo / Healing):** an aura: enemies near you burn, are shocked (5 a second),
    irradiated (10 rads a second) or slowed by 30%; or your companions and allies heal 3 health a second while they
    fight beside you. **Radiatin' (Inferno)** (OP): 30 fire damage a second in twice the radius.
  - **Overcharged** (power armour: +2 Strength, +25 damage and energy resistance, faster fusion core drain) and
    **Scavenger's** (enemies you kill carry extra ammo and caps).
  - PC and Xbox only (they need a script): **Phoenix** (once every 3 minutes, hit at 15% health or less: heal 40%
    and set the attacker on fire), **Bloodthirsty** (every kill heals 10%), **Momentum** (every kill: 20% faster and
    faster Action Points for 10 seconds), **Static Charged** (anything that hits you has a 20% chance of being
    shocked for 40 electrical damage, at most every 5 seconds).

## 2.0.0 (2026-10-12)

### Requirements
- **Four DLC instead of six:** Automatron, Far Harbor, Contraptions Workshop and Nuka-World. Wasteland Workshop and
  Vault-Tec Workshop are no longer needed. Still one plugin, so gear from 1.09 keeps its legendaries, DLC ones
  included.
- The **Untouchable** legendaries and perks (and Brutish, Burning Rage, Constantly Flamin' Cloaked) and the
  **auto-stimpak** effects used Far Harbor scripts; they now use CLM's own copies, which behave identically.

### New
- **15 new legendaries**, finished from pieces 1.09 built but never used:
  - **Lobbin' (Frag / Cryo / Nuke / Plasma / Pulse Mine):** lobs live mines that arm where they land.
  - **Hurtin' (1000%)** (OP): the top of the Hurtin' family.
  - **Instant Killin'** (OP): game-breaking damage; almost anything dies in one hit.
  - **Medic's:** your shots heal whoever they hit by 50 health, at half damage. Heal companions mid-fight.
  - **Overchargin':** hits deal 50 extra energy damage.
  - **VATS Penetratin':** target enemies behind cover in V.A.T.S., like the Penetrator perk.
  - **Quick Hands (50%)** (armour): reload 50% faster.
  - **Marathon Runnin'** (armour): sprinting uses 75% less Action Points.
  - **Focused (Brief)** (armour): time slows for three seconds when you aim, with any weapon.
  - **Stealth Boy'd** (armour, OP): a permanent Stealth Boy field.
  - **Custom Spawning: Random Legendary Radroach:** the one insect that had no legendary version.
- **Settings are now items, and work on every platform** (PlayStation included: 1.09's holotape menus were scripts,
  which PlayStation strips). Each setting is a weightless "CLM Setting" item: carry it and the setting is on, drop
  it and it is off. Craft them for free at any **chemistry station, under "CLM Settings"**, or (PC and Xbox) use the
  configuration holotape, which now gives and takes the same items. Settings:
  - Free crafting / Loot mode (with neither: Costly, legendaries cost components).
  - Show OP legendaries, Show variants, Hide perk-style legendaries, Hide spawning legendaries.
  - Loot mode only: Low or Higher drop rate (with neither: Standard).
- **Legendary Picker** (setting "Picker mode", off by default): too many legendaries at the workbench? Turn it on and
  the workbench shows only the families you pick. At a chemistry station, pick families under the "CLM Armour",
  "CLM Spawns" and "CLM Weapon" categories (e.g. CLM Weapon: Damage > Hurtin'): each pick is a weightless "CLM Pick"
  item; drop it to hide that family again. Your other settings still apply (OP, variants...). Families that are
  entirely OP are also gathered under "CLM OP" and need Show OP. Works on every platform.
- **Optional F4SE menu (PC, Nexus):** with F4SE and Mod Configuration Menu, the "CLM - MCM" add-on puts every
  setting, the Legendary Picker and the perk holotape's 110 perks in the pause menu. Nothing to carry: settings and
  picks become menu settings instead of items, and the holotapes are replaced (they can be turned back on). A button
  turns everything back into items before the add-on is removed.
- **New games start Costly and Balanced**: OP legendaries and variants hidden until you turn them on. No "Starting
  Configuration" step any more.
- **Upgrading from 1.09:** your holotape settings are converted into setting items once, on the first load (PC and
  Xbox).
- **The holotape shows only real choices:** an option disappears while it is already the active setting and comes
  back when you pick another one. Its menus are now one page.
- **Loot mode** (setting "Loot mode", or the holotape's "Loot version - Hunt for legendaries"; was "No-craft
  version / WIP" in 1.09, now finished). CLM legendaries stop being craftable from the start and drop instead, from any enemy you kill
  (vanilla, DLC or modded), with starred legendary enemies dropping far more:
  - **Loose mods:** every legendary can drop as an item. Attach it at a workbench; it is used up instead of
    components.
  - **CLM holotapes:** 112 of them, one per family of legendaries (e.g. Jumpy, Cold, Savage). Carry one to craft its
    whole family.
  - **Legendary Cores:** rare items (one for weapons, one for armour) needed to craft OP legendaries.
  - **Drop rate:** Standard by default; the Low and Higher drop rate settings (or the holotape's "Loot version -
    Drop rate") change it. Rarity tiers (common,
    uncommon, rare, OP) are listed in docs/LOOT_PLAN.md. With Standard: common 3%, uncommon 1%, rare 0.3%, OP 0.1%
    per kill.
  - To go back to crafting, drop the Loot mode setting (or pick Free or Costly on the holotape).
- **Energized laser colours:** Green, Purple, Gold, Orange, Pink and Deep Blue, alongside the original Red and Blue.
  Beam, muzzle flash, sparks, impacts and light all match the chosen colour.
- **Coloured disintegration:** an Energized laser's critical kills now turn enemies to glowing ash in the laser's
  colour (new green, purple, gold, orange, pink and deep blue ash and glow). Before, they disintegrated in the base
  gun's colour, so a green laser on an Institute gun still left blue ash. **Disintegratin' (Green)** now really
  disintegrates in green (it used the plasma "goo" effect); Disintegratin' (Meltin') keeps the goo.
- **Disintegratin' in five new colours:** Purple, Gold, Orange, Pink and Deep Blue, matching the laser colours.

### Fixed: legendaries that did not work
- **Bird Shootin'** no longer turns any gun into a machine gun (it set the fire rate to 7.5x, which its text never promised). It is 50% heavier instead, as described.
- **Scopes no longer go out of control** with Aim Stabilized, Widowmaker's / Tracker's sights or Critically Hurtin' (they added a value far outside the game's range). Aim Stabilized (100%) now holds the scope still on the same scale as the vanilla Stabilized mod. Aim Stabilized (50%) made your scope sway more than with no armour; it now reduces the sway, without stopping it.
- **Weapon effects no longer spread to other weapons or stay on** (reported on Nexus: slow time never turning off, damage and ammo effects on weapons you did not mod). A weapon legendary's hidden bonuses now work only while a weapon carrying that legendary is equipped. Armour legendaries are unaffected. Weapons you already modded get the fix automatically.
- **Chance-based effects now trigger.** 1.09 checked its random chances in a way that was never (or almost never) true, so these chances never fired: Burning (10% to set on fire), Forcible, Deadlier and Lethally Forcible (50% stagger), Slightly Freezing (40% freeze), Seekin' (Plasma), Lucky Drawin' (1% instant kill), Explosively Pushing (Ranged), Roid Ragin' (25%), Suppressin' (10% / 20%), Angry Nerd's (40%), Purely Purging, Generic 80s Action Hero's (15% no damage), Enduring (deflect) and Nightly Training (deflect).
- **Medic's** now really heals (the 50 health was taken straight back), deals 50% less damage as described (1.09's multiplier was wrong), and does no damage at all to your companions. The self-heal on hits of Full Invulnerability (One Punch Man's, God Father's, Generic 80s Action Hero's) had the same healing fault.
- **Health regeneration now works in combat** for Brutal, Super-Tankin', Burning Rage and Constantly Flamin' Cloaked. They used the game's heal rate, which stops during combat; they now restore the same amount per second (e.g. Brutal's 50) at all times.
- **Keltas' Factorium** (Flawed, Rapid, Specialised, Perfect) no longer crashes vanilla weapons the moment they fire
  (1.09 warned about it: it removed the weapon's ammo). Its magazine now refills itself when it runs dry, so you
  still never reload, and it holds twice as many rounds. Works on every gun. Not with Scrounger rank 4.
- **Roid Ragin'**: its 25% chance now does 10x damage, as described (it was a flat instant kill).
- **Suppressin'**: it ignored armour on every hit; now 10% of the time, as described.
- **Keltas' Flawed Factorium** fires 25% slower, as described (it was 50%).
- **Liar's Compedium** now also stuns (staggers) its targets, as described.
- **Vampiric** (and Raging, Annihilating, Reaper's Embrace, Reclaimer's) now heals you on every hit. It used to heal only when the target survived the hit, so kills (molerats, radroaches...) gave nothing.
- **Face Bustin'** no longer kills everything in one hit: targets now blow apart only if the hit killed them, as its description says.
- **One Punch Man's** no longer knocks over the wearer when equipped. Punches still send enemies flying.
- Now flagged **OP** (hidden unless you carry the "Show OP legendaries" setting), as they are as strong as other OP legendaries: Savage, Savage (Limited), Silently Savage (Limited), Caged Savage, Deathly Silenced, Murderously Silenced, all eight Havoc variants, Performance Center, Burning Hellish, Face Bustin', One Punch Man's and Searing.
- **One Punch Man's** now gives what it promises, within what the game can handle: Strength +100 (it gave none), 10x jump height (was 2x) and 3x run speed (was 1.5x). The description no longer promises 100x speed, which breaks movement and world loading.
- **God Father's** now launches the enemies you hit (it used to target the wearer).
- **Cheater's (weapon)** now actually ignores armour (100% penetration).
- **Cheater's (armor)** now gives the 90% explosion resistance its description promised.
- **Mr. Freeze's** now deals its 60 points of cryo damage (it only showed a visual effect before).
- **Salvaged Assaultron's Beaming** no longer irradiates you.

### Fixed: legendaries now do what their description says
- **Generically 80s Action Hero's:** -30% fire rate and -30% recoil now work as described (they broke the weapon's values).
- **Silently Savage (Limited):** 150% fire rate (was about 5x).
- **Advanced Recoilless:** 300% range (the range bonus was almost nothing).
- **Room Clearing:** 35% range, -30% fire rate, 20 extra projectiles; description no longer contradicts itself.
- **Burning Hellish:** 50% more range and accuracy, 75% less recoil.
- **Brutish:** now gives 7x armour health; +20 damage resistance no longer applied twice.
- **Destroyer's (all tiers), Many Barreled Optimised, Nearly Recoilless:** recoil and accuracy bonuses are now real
  percentage reductions.
- **Hydra's (all four):** -40% fire rate and +40% recoil as described.
- **Suppressin':** fire rate and recoil had their signs flipped; its 20% damage proc is now 3x as described (was 4x).
- **Zeus Crafted:** lowers AP cost by 50% (it raised it).
- **Performance Center:** energy damage bonus no longer doubled.
- **Thumpin':** now actually halves fire rate.
- **Super Shotgunnin':** +10 ammo (was +9); 80% range.
- **Improved Performance Center, Reclaimer's, Operator's Balanced:** range now matches the description.
- Weapons whose range is far beyond "100%" (Savage, Deadly Accurate, Slayer's, Thumpin' and others) keep their range;
  their descriptions now say "massively/greatly increased range".
- **Savage (Limited), Caged Savage:** descriptions now mention their +40 energy damage.

### Fixed: holotapes
- **Perk holotape:** "Add Perk -Jedi Reflexible Sprint" label fixed. All 110 perks checked: each has a working add and
  remove.
- **Perk holotape:** Greater Lockpicking (5x) can now be removed. Choosing to remove it used to remove Greater
  Gunbashing instead, and removing Gunbashing did nothing.

### Fixed: other
- **Explosions no longer kill you at close range** (reported on Nexus): legendaries that put an explosion on every bullet or beam used missile-sized blasts (BioReactive (Nuclear) a full Fat Man). They now use the same blast size as the vanilla Explosive legendary, with the same damage: High Explosive, Explosively Penetratin', Viciously Thumpin', Havoc (all), Ultima Hecate's, Garm's, Explosively Striking, Jupiter's Wrathful and BioReactive Explosive (all).
- **Shavka's Explosive Striking** on weapons now warns, like the armour version, that its melee explosions can hurt you.
- Removed 1.09 leftovers that nothing used (unfinished drafts, duplicates of existing effects, the CQC test). No legendary changed.
- **Costly version:** Untouchable (Freeze), Concentratin' Intensely (and Brief), Slightly Freezing and Mr. Freeze's cost nothing to craft. They now cost the same as their closest sibling (Untouchable (Fire), Concentratin' Harder / (Brief), Chilling, Prometheus' Fiery).
- The mod's archive no longer replaces 24 of the game's own scripts with old 2017 copies (one was F4SE's version,
  which could cause problems without F4SE, e.g. on Xbox).
- Typos in several descriptions.

## 1.09 (2017)
Final release of the original mod. See the Nexus Mods page for earlier history.
