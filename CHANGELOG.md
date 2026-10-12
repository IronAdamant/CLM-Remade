# Changelog

## 2.1.0 (in progress)

The feature requests of 2016-17 that 1.09 left as "not possible" or "no time".

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
