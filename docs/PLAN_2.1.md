# CLM 2.1 plan: the old requests

2.0 fixed the bugs (Grok's scrape, `docs/COMPLAINTS_TRIAGE.md`). It did not go through the **feature requests** of
2016-17: the ones the author marked "not possible", "delayed" or "no time". 2.1 is a minor update: those requests,
as new legendaries, plus a few loose ends. No changes to loot, settings or the costly / free system.

Platforms, as in 2.0: legendaries built from records only go everywhere, PlayStation included. Legendaries that need
a script are PC and Xbox only; the PlayStation build (`tools/release/playstation.py`) keeps them with a note or
leaves them out.

## Sources (read 2026-10-13)

The author's 2016-17 documents are in `docs/private logs/`: **local only, never committed** (excluded in
`.git/info/exclude`; the repo is public). If that folder is missing, ask the author for it.

- `CK Requests.docx`: the request log behind both Google Docs on the old mod page ("Requests in progress" and
  "Requests he could not complete"). Its text colours were the status: red = impossible then, blue = done, orange =
  unsure, green = in progress, black = to do. A plain-text copy without colours is in AgentCreationKit
  `private/logs_text/`.
- `Custom Legendary Modifications (Mods done).xlsx`: the "Completed effects" sheet (386 legendaries with who
  requested each; marked out of date in 2017). Use it for credits, and for step 4's check.
- `Custom Legendary Modifications ideas.docx`, `Place for IDEAS.docx`: the author's own ideas (below).
- `Remade System plans.docx`: the global-variable settings design that 2.0 already implements.

Requests already in CLM, nothing to do: Caged Savage, Gunslinger's, Gauss legendaries (YamatoNCC-1701), triple
damage (Triplet: in the damage families), paddleball Quantum (mademost), Thor's power-attack explosion, Bloody Messy,
lobber arrow mines (2.0's Lobbin' mines), healing others (2.0's Medic's), loot-list injection (2.0's loot mode), One
Punch (fixed in 2.0).

## 1. Can be built now (records only: all platforms)

| Request (by) | What was asked | How | Check in the CK first |
|---|---|---|---|
| **Blitzkrieg** (FL4CKTROOPER) | +60% V.A.T.S. accuracy and range, 95% less AP in V.A.T.S., double crit damage, crit meter fills 2x faster | Weapon legendary: perk entry points for V.A.T.S. hit chance, crit damage and crit charge; the weapon's Action Point Cost property for the AP part | Which entry point gives V.A.T.S. accuracy (Concentrated Fire's) and range; whether AP cost x0.05 behaves |
| **Bloodlust** (FL4CKTROOPER) | The lower your health, the more damage: every 10% of health lost adds 10 damage | Weapon legendary: one perk entry (Mod Weapon Attack Damage) per 10% band, each conditioned on the player's health percentage, as vanilla Nerd Rage and Adrenaline do | Condition function for health % (FO4 numbers differ from Skyrim: decode through FO4Edit) |
| **Staminator** (Wardogg83) | No AP drain on anything; no need to breathe | Armour legendary: Marathon Runnin's entry point (Mod Sprint AP Drain Rate) at 0, AP cost in V.A.T.S. through the matching entry point, the WaterBreathing actor value | Which drains remain (jumping in power armour? melee power attacks) |
| **Nature's Wrath** (Sereda Hawke) | Each hit: 10% chance each of +20% fire, cryo, poison or shock damage; +25% fire rate | Weapon legendary: four chance-conditioned enchantments (the RandomPercent fix from 2.0), plus the fire rate property. It needs no random projectile, which is why 1.09 thought it impossible | "+20%" as a damage multiplier or flat damage per type |
| **OP Weapon Skills** (mademost) | Armour: crit chance (15-20%), crit damage, scope stability, crit charge, bash crits, faster weapon draw and scope in/out, cheaper V.A.T.S. No weapon damage | Armour legendary, OP: perk entry points | Draw / scope speed: is there an entry point, or a weapon actor value? Scope stability scale: 1.0 = normal, below is worse (2.0 lesson) |
| **Friendly Mirelurk Queen** (LandH) | A shot spawns a friendly Mirelurk Queen; optional hatchlings and a death explosion | Weapon legendary in CLM's spawn system, which spawns only hostile creatures today: needs a friendly variant (player-allied faction or a teammate flag on the spawned actor). Hatchlings and explosion only if cheap | How the Human/Brotherhood "ally" spawns pick their side; whether a creature can use it without a script |
| **Stealthy Armour** (Doom1993) | On crouch: muffled, shadowed, chameleon, enemies lose track of you; constant 5000 Perception, Luck, Agility, Endurance; power armour vision; sure pickpocketing, from 1000 feet | Armour legendary, OP: everything except remote pickpocketing exists in CLM pieces already (Ghostly, Camouflaged, Murderous...). Sure pickpocketing through the pickpocket chance entry point | Pickpocketing at range: leave out, say so in the description |
| **Simple effects** (ViscousVitriol) | Plain stat legendaries without extras: 2x fire rate, 10x damage, both together, 100% cripple chance | Check the catalog first (Hurtin', Rapid, Crippingly...); add only the missing plain ones, with short descriptions | - |
| **Jumpy (10%)** (Doom1993) | A 10% jump step; the 1.09 author promised it | Jumpy starts at 50% today: add the 10% (and 25%?) variant | - |
| **Brutish and Plated Titanium** (FL4CKTROOPER) | Brutish: fire damage only while Burning Rage triggers, 5 points, not stacking. Plated Titanium: in-combat regen capped at 50% health, or only below 20% | Review both against the request; the author never got to it. Plated Titanium is not found by name in 2.0 (see 4) | 2.0 changed in-combat regeneration (Brutal, Super-Tankin'...): keep that consistent |
| **PlayStation perks** (author's note: "a scriptless way to add perks") | The perk holotape is scripted, so PlayStation has no perk adding | "CLM Perk" magazines at the chemistry station: reading one adds its perk, with no script (the CLM Loot Manual already works this way). Adding only: removing a perk needs a script | Which of the 110 holotape perks are worth a magazine |

## 2. Can be built now, with a script (PC and Xbox)

| Request (by) | What was asked | How | Risk |
|---|---|---|---|
| **% of health damage** (ViscousVitriol) | Each hit takes e.g. 10% of the enemy's health | OnHit script: DamageValue(Health, 10% of the target's base health). Maybe cap or skip essential actors | Script load on automatics; test with a minigun |
| **Hello Neighbour!** (stephen4000) | Armour that makes Gunners friendly | On equip, the player joins a faction friendly to the Gunners (or the Gunners' reaction to the player changes); undone on unequip | Quests that need Gunners hostile (Quincy, Gunner plazas): test |
| **Advanced Titanium, real reflect** (FL4CKTROOPER) | Power armour: reflect 5% of melee damage | 1.09 shipped "5% less damage" instead. The old "Wrathful Titan's" (now Titan's Wrath) claims 100% melee reflect: check how it does it first, then reuse or add an OnHit script | Keep the 5% cut if reflect stays unreliable; description to match |

PlayStation: these are left out of the PlayStation build, or kept with a note (as 2.0 did for Untouchable).

## 3. Needs a deeper investigation (may stay impossible)

| Request (by) | What was asked | What to investigate | Fallback |
|---|---|---|---|
| **CQC: three-round burst** (DarkArcher045) | Any firearm fires three-round bursts | FO4 has no burst mode. Script: RegisterForAnimationEvent(player, "weaponFire"), then fire two more shots (Weapon.Fire) per trigger pull; check ammo use, timing and V.A.T.S. | A faster fire rate on semi-auto only |
| **Jumper's** (Heavy & Ze Medic) | Rocket-jump: shooting your feet launches you; no self or fall damage | Explosions do not push the player in FO4. Look for a scripted launch (a knockback spell on the player, ApplyHavokImpulse, the jetpack's physics) | Explosion and fall damage immunity only (already in CLM's Landin' pieces) |
| **Cinematic Excellence** (Tjonbrown24) | 10% chance of a V.A.T.S.-style kill camera outside V.A.T.S. | Whether any function triggers a kill camera from a script | None: say so |
| **Flight** (Wickedcircle, Heavy & Ze Medic) | Real flight | No engine flight. Look at existing flight mods (how they do it, F4SE or not); 1.09's Superman effects are the stand-in | Keep Flyin' as is |
| **God Creator / Healing Beam** (Heavy & Ze Medic) | A beam that heals (10 rising to 80 per second as the patient's health drops) and, for God Creator, makes them invulnerable | Medic's proved healing others works. A beam projectile, heal scaled by the target's health, temporary invulnerability on companions only | A stronger Medic's variant |
| **DragonBlade** (AgentSmithGSOM) | Melee: teleport to the crosshair when attacking, deflect bullets when blocking or sprinting, +200 damage | Deflect and damage exist (Jedi Reflexes, Bouncin'). Teleport needs a script (MoveTo a point in front of the player, collision checks) | Without the teleport |
| **No Brakin'** (H3xx) | Pain Train without power armour (all ranks combined) | Left as "WIP - DO NOT USE" in 2017, and "Pain Train on armour does nothing" was never solved. Why the perk needs power armour: its conditions, or the charge itself | Leave out |
| **Enraged** (author's idea) | Armour: faster attacks and movement, and a rage burst that makes enemies flee while they burn | Attack and move speed are simple; the burst needs an explosion carrying fear and fire on a trigger (when hit, or low health) | Speed parts only |
| **Fortune Finder explosions** (author's idea, "Place for IDEAS") | Variants of PerkFortuneFinderEffect (exploding caps) that cause real explosions, without changing projectiles | How Fortune Finder spawns its explosion; swap in CLM's explosions | - |
| **2LM / 3LM versions** (author's future plan; credit matzman666 and Marelo) | A second and third legendary slot | LEO already adds extra slots and is compatible. Decide: point players to LEO, or ship CLM's own | Point to LEO |

Requests the author refused on purpose stay refused (GigaByteWide's Demon of the Divide set, "not in the spirit of
the mod").

## 4. Loose ends from 2.0

- [ ] Test in game: Speedy and Combined Speed and Jump reset on unequip (triage #1; Jumpy already passed).
- [ ] Toxic Blood, Slow Aim, Pain Train on armour, Silenced Electrical Striker in V.A.T.S.: 1.09 reported them not
      working. Find out whether they were renamed, removed or never built.
- [ ] The "Mods done" sheet against `docs/CATALOG.md`: most names differ only by renames (Wrathful Titan's = Titan's
      Wrath, force fields = Shield, Destroyin' = Destroyer's, spawns = "Custom Spawning: ..."). Not found under any
      name: Plated Titanium, Gheed's Fortunate (barter), Resettin' (the stuck jump/speed fix item), the Minuteman
      and Child of Atom spawns. Find out whether they were removed before 1.09 (they may have been, on purpose), and
      bring back any that were lost by accident.
- [ ] `A1ALMQuestConfigInit` logs "Cannot clear a non-optional alias" once per new game: harmless; make the alias
      optional or drop the Clear().
- [ ] `docs/COMPLAINTS_TRIAGE.md` #16-18 still describe the DLC add-ons; 2.0 merged them back (four DLC, one
      plugin). Update the wording.

## 5. Release

Same pipeline as 2.0 (`docs/release/BETHESDA_NET.md`): `package.py --version 2.1.0`, CK uploads (PC, Xbox page,
PlayStation), Nexus zip. Every new legendary gets a catalog entry, a loot pool (`tools/loot/plan.py`), a picker
family if it starts a new one, its requester in the changelog, and an in-game test checklist before release.
