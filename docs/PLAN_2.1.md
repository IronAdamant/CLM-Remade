# CLM 2.1 plan: the old requests

2.0 fixed the bugs (Grok's scrape, `docs/COMPLAINTS_TRIAGE.md`). It did not go through the **feature requests** of
2016-17: the ones the author marked "not possible", "delayed" or "no time" in `CK Requests.txt` (ACK
`private/logs_text/`) and the two Google Docs linked from the mod page. 2.1 is a minor update: those requests, as new
legendaries, plus a few loose ends. No changes to loot, settings or the costly / free system.

Platforms, as in 2.0: legendaries built from records only go everywhere, PlayStation included. Legendaries that need
a script are PC and Xbox only; the PlayStation build (`tools/release/playstation.py`) keeps them with a note or
leaves them out.

## 0. Gather the full list first

- [ ] Fetch the author's two Google Docs ("Requests in progress", "Requests he could not complete"; links in
      `docs/Nexus bugs and complaints.md`) and the "Mods done" spreadsheet, and merge them with `CK Requests.txt`.
      If the docs are not public, the author exports them.
- [ ] One line per request in this file: requester, what was asked, status. Requests already in CLM under another
      name are marked done.
- [ ] Credit each requester in the changelog entry of their legendary, as 1.09 did.

## 1. Can be built now (records only: all platforms)

| Request (by) | What was asked | How | Check in the CK first |
|---|---|---|---|
| **Blitzkrieg** (FL4CKTROOPER) | +60% V.A.T.S. accuracy and range, 95% less AP in V.A.T.S., double crit damage, crit meter fills 2x faster | Weapon legendary: perk entry points for V.A.T.S. hit chance, crit damage and crit charge; the weapon's Action Point Cost property for the AP part | Which entry point gives V.A.T.S. accuracy (Concentrated Fire's) and range; whether AP cost x0.05 behaves |
| **Bloodlust** (FL4CKTROOPER) | The lower your health, the more damage: every 10% of health lost adds 10 damage | Weapon legendary: one perk entry (Mod Weapon Attack Damage) per 10% band, each conditioned on the player's health percentage, as vanilla Nerd Rage and Adrenaline do | Condition function for health % (FO4 numbers differ from Skyrim: decode through FO4Edit) |
| **Staminator** (Wardogg83) | No AP drain on anything; breathe underwater | Armour legendary: Marathon Runnin's entry point (Mod Sprint AP Drain Rate) at 0, AP cost in V.A.T.S. through the matching entry point, the WaterBreathing actor value | Which drains remain (jumping in power armour? melee power attacks); name it as requested |
| **Nature's Wrath** (Sereda Hawke) | Each hit: 10% chance each of +20% fire, cryo, poison or shock damage; +25% fire rate | Weapon legendary: four chance-conditioned enchantments (the RandomPercent fix from 2.0), plus the fire rate property. It needs no random projectile, which is why 1.09 thought it impossible | "+20%" as a damage multiplier or flat damage per type |
| **OP Weapon Skills** (mademost) | Armour: crit chance (15-20%), crit damage, scope stability, crit charge, bash crits, faster weapon draw and scope in/out, cheaper V.A.T.S. No weapon damage | Armour legendary, OP: perk entry points | Draw / scope speed: is there an entry point, or a weapon actor value? Scope stability scale: 1.0 = normal, below is worse (2.0 lesson) |
| **Friendly Mirelurk Queen** (LandH) | A shot spawns a friendly Mirelurk Queen; optional hatchlings and a death explosion | Weapon legendary in CLM's spawn system, which spawns only hostile creatures today: needs a friendly variant (player-allied faction or a teammate flag on the spawned actor). Hatchlings and explosion only if cheap | How the Human/Brotherhood "ally" spawns pick their side; whether a creature can use it without a script |

## 2. Can be built now, with a script (PC and Xbox)

| Request (by) | What was asked | How | Risk |
|---|---|---|---|
| **% of health damage** (ViscousVitriol) | Each hit takes e.g. 10% of the enemy's health | OnHit script: DamageValue(Health, 10% of the target's base health). Bosses and legendaries included; maybe cap or skip essential actors | Script load on automatics; test with a minigun |
| **Hello Neighbour!** (stephen4000) | Armour that makes Gunners friendly | On equip, the player joins a faction friendly to the Gunners (or the Gunners' reaction to the player changes); undone on unequip | Quests that need Gunners hostile (Quincy, Gunner plazas): test; scripted fights may still turn them |
| **Advanced Titanium, real reflect** (FL4CKTROOPER) | Power armour: reflect 5% of melee damage | 1.09 shipped "5% less damage" instead. Retry: Jedi Reflexes / Bouncin' already reflect projectiles; melee reflect needs an OnHit script on the player (deal 5% of the hit back) | Keep the 5% cut if reflect stays unreliable; update the description to match |

PlayStation: these three are left out of the PlayStation build, or kept with a note (as 2.0 did for Untouchable).

## 3. Needs a deeper investigation (may stay impossible)

| Request (by) | What was asked | What to investigate | Fallback |
|---|---|---|---|
| **CQC: three-round burst** (DarkArcher045) | Any firearm fires three-round bursts | FO4 has no burst mode. Script: RegisterForAnimationEvent(player, "weaponFire"), then fire two more shots (Weapon.Fire) per trigger pull; check ammo use, timing and V.A.T.S. | A faster fire rate on semi-auto only |
| **Jumper's** (Heavy & Ze Medic) | Rocket-jump: shooting your feet launches you; no self or fall damage | Explosions do not push the player in FO4. Look for a scripted launch (a knockback spell on the player, ApplyHavokImpulse, the jetpack's physics) | Explosion and fall damage immunity only (already in CLM's power armour landing pieces) |
| **Cinematic Excellence** (Tjonbrown24) | 10% chance of a V.A.T.S.-style kill camera outside V.A.T.S. | Whether any function triggers a kill camera from a script | None: say so in the reply |
| **Flight** (Wickedcircle, Heavy & Ze Medic) | Real flight | No engine flight. Look at existing flight mods (how they do it, F4SE or not); 1.09's Superman effects are the stand-in | Keep Flyin' as is |
| **God Creator** (Heavy & Ze Medic) | Beam that heals and makes a target invulnerable | Medic's (2.0) proved healing others works. Beam projectile + heal + temporary invulnerability on companions only | A stronger Medic's variant |

Requests the author refused on purpose stay refused (GigaByteWide's set, "not in the spirit of the mod").

## 4. Loose ends from 2.0

- [ ] Test in game: Speedy and Combined Speed and Jump reset on unequip (triage #1; Jumpy already passed).
- [ ] Toxic Blood, Slow Aim, Pain Train on armour, Silenced Electrical Striker in V.A.T.S.: 1.09 reported them not
      working, and none appears under that name in `docs/CATALOG.md`. Find out whether they were renamed, removed or
      never built.
- [ ] `A1ALMQuestConfigInit` logs "Cannot clear a non-optional alias" once per new game: harmless; make the alias
      optional or drop the Clear().
- [ ] `docs/COMPLAINTS_TRIAGE.md` #16-18 still describe the DLC add-ons; 2.0 merged them back (four DLC, one
      plugin). Update the wording.

## 5. Release

Same pipeline as 2.0 (`docs/release/BETHESDA_NET.md`): `package.py --version 2.1.0`, CK uploads (PC, Xbox page,
PlayStation), Nexus zip. Every new legendary gets a catalog entry, a loot pool (`tools/loot/plan.py`), a picker
family if it starts a new one, and an in-game test checklist before release.
