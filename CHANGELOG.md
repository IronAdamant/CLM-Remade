# Changelog

## Unreleased (work in progress towards 2.0)

### Requirements
- **The main mod no longer needs any DLC** - just Fallout 4. (1.09 needed all six.)
- Legendaries that use a DLC's creatures, art or effects moved to optional add-ons, one per DLC. Install the ones for
  the DLC you own; they are ESL-flagged (no load-order slot) and follow the configuration holotape like the rest:
  - `CLM - Automatron.esp`: 13 robot spawns.
  - `CLM - Far Harbor.esp`: 9 creature and Trapper spawns, Paintball x6, Trappin' x4, Moby-Dick's, Silenced Harpoon
    Striker.
  - `CLM - Nuka-World.esp`: 12 creature and raider spawns.
  - `CLM - Contraptions.esp`: Pyrotechnical x9, Weather Altering x3.
  - **Upgrading from 1.09:** gear that already has one of these legendaries attached loses it unless the matching
    add-on is installed (then re-craft it). Take them off at a workbench before updating if unsure.
- The **Untouchable** legendaries and perks (and Brutish, Burning Rage, Constantly Flamin' Cloaked) and the
  **auto-stimpak** effects used Far Harbor scripts; they now use CLM's own copies, which behave identically.

### New
- **Loot mode** (configuration holotape: "Loot version - Hunt for legendaries"; was "No-craft version / WIP" in
  1.09, now finished). CLM legendaries stop being craftable from the start and drop instead, from any enemy you kill
  (vanilla, DLC or modded), with starred legendary enemies dropping far more:
  - **Loose mods:** every legendary can drop as an item. Attach it at a workbench; it is used up instead of
    components.
  - **CLM holotapes:** 112 of them, one per family of legendaries (e.g. Jumpy, Cold, Savage). Carry one to craft its
    whole family.
  - **Legendary Cores:** rare items (one for weapons, one for armour) needed to craft OP legendaries.
  - **Drop rate:** "Loot version - Drop rate" offers Low, Standard (default) and Higher. Rarity tiers (common,
    uncommon, rare, OP) are listed in docs/LOOT_PLAN.md. With Standard: common 3%, uncommon 1%, rare 0.3%, OP 0.1%
    per kill.
  - DLC legendaries drop only with their add-on installed, without raising the overall drop rate.
  - To go back to crafting, run a Starting Configuration on the Free or Costly version page.
- **Energized laser colours:** Green, Purple, Gold, Orange, Pink and Deep Blue, alongside the original Red and Blue.
  Beam, muzzle flash, sparks, impacts and light all match the chosen colour.

### Fixed: legendaries that did not work
- **One Punch Man's** no longer knocks over the wearer when equipped. Punches still send enemies flying.
- Now flagged **OP** (hidden when the configuration holotape is set to "Balanced only"), as they are as strong as other OP legendaries: Savage, Savage (Limited), Silently Savage (Limited), Caged Savage, Deathly Silenced, Murderously Silenced, all eight Havoc variants, Performance Center, Burning Hellish, Face Bustin', One Punch Man's and Searing.
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
- **Perk holotape:** Greater Lockpicking (5x) can now be removed. Choosing to remove it used to remove Greater
  Gunbashing instead, and removing Gunbashing did nothing.
- **Configuration holotape (Free version):** the Balanced page had its two options' labels swapped.

### Fixed: other
- The mod's archive no longer replaces 24 of the game's own scripts with old 2017 copies (one was F4SE's version,
  which could cause problems without F4SE, e.g. on Xbox).
- Typos in several descriptions.

## 1.09 (2017)
Final release of the original mod. See the Nexus Mods page for earlier history.
