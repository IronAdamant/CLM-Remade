# How CLM works

Notes for anyone maintaining or extending this mod. Condensed from the author's 2016-2017 working notes, with
corrections from the 2026 audit.

## Naming

Every record CLM adds starts with `A1ALM`, so they sort together in the Creation Kit and FO4Edit:

| Prefix | Record type |
|---|---|
| `A1ALMOMOD_Legendary_Weapon_*` / `_Armor_*` | The legendary modifications themselves |
| `co_A1ALMOMOD_*` / `co_A1ALMOMOD_*FREE` | Costly / free crafting recipe for each one |
| `A1ALMEnch_*` | Enchantments (`Constant_Effect_*` on the wearer, `FaF_Contact_*` on hit targets) |
| `A1ALMMGEF_*` | Magic effects |
| `A1ALMPERK_Legendary_Hidden_*` | Perks applied through magic effects (not shown to the player) |
| `A1ALMPROJ_*` / `A1ALMEXP_*` | Custom projectiles and explosions |
| `A1ALMTERM_*`, `A1ALMTAPE_*` | Holotape menus |

In-game names: `CLM:` for normal legendaries; `ZLM:` for the Custom Spawning ones, so they sort to the end of the
workbench list.

## The configuration system

The workbench would show over 500 legendaries at once, so six global variables decide which recipes appear.
Every recipe carries `GetGlobalValue` conditions; the holotape changes the globals.

| Global | 1 | 0 |
|---|---|---|
| `A1ALMAFREE` | Free recipes | Costly recipes (component costs) |
| `A1ALMAPERK` | Legendaries that have a perk counterpart are craftable | Hidden |
| `A1ALMASPAWN` | Custom Spawning legendaries are craftable | Hidden |
| `A1ALMAVAR` | Variants are craftable | Only the base legendaries |
| `A1ALMAWPN` | Explosive weapon legendaries are craftable | Hidden (there are many) |
| `A1ALMABALANCED` | OP and balanced legendaries | Balanced only |

Recipes only test for `== 1` (and `A1ALMAFREE == 0` for costly ones), so any other value hides a category. The
holotape's "No-craft" option uses this by setting the globals to 4.

The **Configuration Holotape** is craftable at the chemistry station (UTILITY) and is also given automatically by the
quest `A1ALMAQUEST_Inventory_Autoadd`: its script waits until the player has the Pip-Boy (`MQ102` stage 6), then adds
the holotape. Items given earlier are lost during the pre-war sequence.

The **Perk Holotape** adds and removes CLM's perk versions of legendaries. Each entry is shown only when the player has
(or lacks) that perk, via `HasPerk` conditions on the menu items.

## Why the legendary slot shows up

CLM's only edit to a base-game record gives the `ap_Legendary` attach-point keyword a name ("Not Legendary"). The
workbench appears to show an attach slot only when its keyword has a name, which is what makes the legendary slot
visible (teaLz's Legendary Modification uses the same approach). A mod that also edits that keyword and loads later can
hide the slot again; players reported fixing missing CLM recipes by changing load order. *(Still to be confirmed with
an in-game test.)*

## Techniques worth knowing

- **Put stats in enchantments, not OMOD actor values.** Adding actor values directly on an OMOD is unreliable. Build a
  magic effect, put it in an enchantment with the magnitude you want, and attach the enchantment to the OMOD. Exception:
  armor penetration needs the penetration keyword plus the `EncharmorPenetration` enchantment, then the actor value.
- **Overriding a weapon's projectile:** the `OverrideProjectile` property must use `SET`, not `ADD` or `REM`. A weapon
  can only override to one projectile, so "random projectile per shot" is not possible without scripting.
- **Infinite ammo (the Factorium legendaries):** set the weapon's ammo to none. Works for most weapon types, but not
  alien blasters or laser weapons.
- **Refilling** uses the Scrounger perk's ammo entry point. Scrounger rank 4 *sets* that value to 0.05, so it overrides
  Refilling. Doesn't work with the Cryolator.
- **Chain projectiles** only work with beam-type projectiles (lasers, gauss, and spikes converted to beams). Plasma,
  alien and cryo projectiles are missile-type: as beams they fire no visible projectile.
- **Seeking projectiles** only work with missile-type projectiles. Set gravity to 0 so they fly straight.
- **Power armor impact landing without power armor:** make a copy of `PowerArmorPerkEffect` and point its
  `PowerArmorFXScript` properties (`myImpactLandExplosion`, `PA_ExplosiveVentExplosion`) at your explosion. Pair it with
  no-fall-damage and protection from that explosion. Use a *copy* of `PowerArmorPerk`: the original expects a power armor
  helmet and breaks the Pip-Boy.
- **Rainman's (splitting missiles):** untick "Always Uses World Orientation" on the explosions that spawn the missiles.
- **Regeneration effects:** tick "Power Affects Magnitude" (Spellmaking) so the enchantment's magnitude applies.

## Things that were not possible in 2017

Without scripts (the PlayStation version cannot use any), these could not be built:

- A random projectile or random damage type per shot
- Healing beams that heal allies
- Damage as a percentage of the target's health
- Removing AP drain entirely (no AP cost entry point in the Creation Kit)
- Burst fire (Fallout 4 has no burst-fire mode)
- Triggering kill-cam style kills outside VATS
- Reflecting damage back at attackers (Advanced Titanium shipped with 5% damage reduction instead)

Several of these can be done with Papyrus scripts on PC and Xbox.

## Coloured lasers (2.0)

A laser's colour is spread across several places, and all of them have to change together or the vanilla colour
leaks through. `tools/assets/laser_colors.py` generates everything from the game's own red laser files:

- **Gradient textures** (32x32 colour lookups) drive the beam, muzzle flash and impact colours. New colours are the
  vanilla red gradients with the hue rotated, which keeps the white-hot core and fade.
- **Shader base colour** multiplies the gradient. The vanilla muzzle flash has a red-orange base colour baked in, so
  it must be set to white or every colour comes out red.
- **Add-on nodes** (ADDN records) are shared particle effects (sparks, smoke, impact wave) that models attach by a
  global index, so swapping texture paths never reaches them. Each colour has its own four, at indexes
  1500 + colour*10 + kind.
- **Light** (LIGH) and **impact data set** (IPDS/IPCT, including the decal colour) are records, set per colour by the
  scripts in `tools/xedit/`.

Two lessons from testing:
- **Keep ADDN indexes small.** All official content uses indexes below 1000. A build that used 5565000+ made the game
  crash; 1511-1564 works.
- **Texture paths are case-insensitive.** Vanilla models mix `textures\Effects` and `textures\effects`, so path
  replacement must ignore case. The generator refuses to write a model that still points at a vanilla colour.
