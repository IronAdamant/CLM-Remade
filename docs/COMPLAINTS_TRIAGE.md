# Nexus complaints: status in 2.0

Triage of `docs/Nexus bugs and complaints.md` (Grok's scrape of the 1.09 page, posts and bug tracker, 2026-10-11)
against the 2.0 plugin. Numbers refer to that file's "Still open" list. Evidence comes from the plugin itself:
`docs/CATALOG.md` (every legendary's real effect chain, `tools/audit/catalog.py`) and the checks named below.

Statuses: **Fixed in 2.0** (with the commit or change), **To fix** (confirmed from the data, work planned),
**Test in game** (the data looks right; needs a real check), **Not CLM** (the plugin cannot cause it),
**By design** (works as described; text or docs may need clarifying).

## Still-open list

| # | Complaint | Status | Evidence / plan |
|---|---|---|---|
| 1 | Jump height and move speed stuck | Test in game | All CLM stat effects have the engine's Recover flag (checked every constant value-changing effect); the in-game test of Jumpy showed JumpHeightMult back to 0 on unequip. The 2023 report predates 2.0. Re-test Speedy and Combined Speed and Jump. |
| 2 | Effects spread to weapons you did not mod | Fixed in 2.0 | Weapon perks (infinite ammo, slow time, damage) are hidden perks with no condition tying them to the modded weapon: while the effect is active they apply to whatever is in your hands. Add a weapon condition to those perk entries. |
| 3 | Cannot talk to Curie | Not CLM | CLM changes one vanilla record (the `ap_Legendary` keyword). Nothing it adds touches dialogue, quests or NPCs. |
| 4 | Dog armour bench locks | Not CLM | Retracted by the reporter (another mod). |
| 5 | Mini-nuke explosions, self-kills | Fixed in 2.0 | Per-bullet explosions on High Explosive, Explosively Penetratin', both Thumpin's, Havoc (Bullets), Ultima Hecate's and Garm's use missile-sized blasts (500 units) on every shot; vanilla's Explosive legendary uses 200. Close shots catch the shooter. Shrink per-bullet blasts to vanilla size (damage unchanged). BioReactive's trigger distance to check. |
| 6 | Vampiric heals on some enemies only | Fixed in 2.0 | Uses the "Absorb Health" effect type; vanilla's Vampire's legendary heals the shooter through a perk instead. Rebuild on the vanilla mechanism. |
| 7 | Mr. Freeze's is visual only | Fixed in 2.0 | Batch 1c: its 60 cryo damage now applies. Now also costs components (Freeze recipe fix). |
| 8 | Time-slow never turns off | Fixed in 2.0 | Same mechanism as #2 (hidden perks); fix together, then test. |
| 9 | Shotguns lose spread, even vanilla ones | Not CLM | CLM does not touch any weapon, aim model or vanilla OMOD. |
| 10 | Raging slows you to a crawl | Test in game | Raging has no movement or weight effect in its data. (Its vampiric healing exists; it shares #6's fix.) |
| 11 | Burning Hellish recoil | By design | Recoil is cut 75%, as the text says, and its 100 burning damage is there (25 per second for 4 s). |
| 12 | Deadly Accurate disappeared | Fixed in 2.0 | It exists (Recoilless family, OP). Gear tagged by an older build lost it in a 2017 update. |
| 13 | Only some effects next to Legendary Modification | Not CLM | Another mod's list. |
| 14 | Effects never drop from legendary enemies | Fixed in 2.0 | Loot mode: every legendary drops, starred enemies roll ten times. |
| 15 | Everything craftable for free | By design | The Free version. 2.0's holotape and readme say so, and Costly is one choice away. |
| 16, 17 | Missing masters, "something is missing" | Fixed in 2.0 | The main plugin needs no DLC; DLC content is in optional add-ons. |
| 18 | No no-DLC build | Fixed in 2.0 | As above. |
| 19 | Crafting Framework patches are dead | Done | Checked with LEO 2.1.3 (2026-10-12): no conflicts (LEO only names ap_Legendary "L1" and DamageDamageResistEffect); note in readme and Nexus text. |
| 20 | Stealth field stops human companions fighting | Test in game | Handy's "stealth field" is the Ghostly (Crouch) perk set (detection entry points). Test with a companion. |
| 21 | One Punch ragdolls the player | Fixed in 2.0 | Batch 1c; also now gives what its text promises. |
| 22 | Face Bustin' one-shots everything | Fixed in 2.0 | Confirmed: its "explode after death" uses vanilla's ExplodeOnContactScript, which dismembers and calls Kill() on every hit. Replace with an effect that only blows apart targets the hit killed. |
| 23 | Hazmat does not stop rads | Test in game | Biological Hazmat zeroes incoming spell magnitude and rad health loss; environmental radiation needs a real test. |
| 24 | Nuka-Infused fires the wrong bottle | Fixed in 2.0 | Rebuilt on the base-game Nuka Grenade. |
| 25 | Second legendary slot (2LM) | Not CLM | Other mods' slots. |

## Author's 1.09 "unfinished" list

- Healing another actor did not work in 2017: 2.0's new **Medic's** relies on it - test in game.
- Advanced Titanium reflect, Pain Train on armour, Critically Hurtin', Disintegration: part of the description pass.
- Loot-list injection: done (loot mode). Flight: Flyin' remains the substitute.

## The description pass (batch 2)

Batch 1 checked every number in every description (214 of 233 matched; the rest were fixed). It did not check
for promised effects that are missing altogether. `tools/audit/promises.py` flags candidates from the catalog.
(A first catalog version skipped every second property and produced 113 flags, several of them wrong - e.g.
Burning Hellish, Raging and Reaper's Embrace are fine. The catalog now checks its own property counts against the
plugin's; 37 flags remain, most of them wording.) Confirmed gaps:

- **Face Bustin'**: kills on every hit (see #22).
- **Roid Ragin'**: "25% to do 10x damage" is 10,000 damage on every hit; "flying on critical" happens on every hit.
- **Rayden's Fury**, **Carbonatin'**: effects meant for critical hits fire on every hit / kill.
- **Keltas' Flawed Factorium**: 50% slower; the text says 25%.
- **Liar's Compedium**: promises a stun it does not have.

## Done (2026-10-11)

- #5: 14 per-bullet blasts shrunk to vanilla size (`fix_explosion_sizes.py`); Shavka's weapons warn.
- #6: drain effects heal on every hit, kills included (`fix_vampiric_facebusting.py`).
- #22: Face Bustin' blows apart only dead targets (same tool).
- #2, #8: weapon perks require their keyword on the equipped weapon (`fix_weapon_perk_spread.py`: 28 perks, 64
  weapon legendaries; 7 perks shared with armour got weapon-only copies).
- Found on the way: 18 chance conditions that never fired (`fix_random_chances.py`), Roid Ragin', Suppressin',
  Keltas' Flawed, Liar's Compedium (`batch2_promises.*`).

