# PlayStation: what does not work (heads-up for the release texts)

PlayStation (PS4/PS5) mods may not include custom scripts: anything that relies on a CLM script silently does nothing
there. Vanilla (Bethesda) scripts work, so most effects are fine. Checked 2026-10-11 by listing every script every CLM
record uses (`docs/CATALOG.md`, `tools/audit/catalog.py`): 40 of the main plugin's 522 legendaries depend on a CLM
script; the DLC add-ons' legendaries use none. Re-check before release if legendaries or scripts change.

Plan agreed for 2.0 (not built yet): settings move to items crafted at the chemistry station ("Option 2"), so the
configuration works on every platform; the holotape stays on PC and Xbox as a front end.

## Legendaries that need a CLM script

| Legendaries | Script | PlayStation |
|---|---|---|
| Untouchable (Disarm, Fire, Freeze, Frenzy, Knockdown, Pacify, Paralyzed, Poison, Rad, Shock, Spook), Brutish, Burning Rage, Constantly Flamin' Cloaked | A1ALMMGEF_OnMeleeEffect (melee retaliation) | Does not work - no scriptless way to act on whoever hits you |
| Shavka's Explosive Striking (all 7, weapon and armour versions) | A1ALMMGEF_OnMeleeHitCLMEffect | Does not work - explosions on hit need a script |
| Brutish, Ridiculously Absorbin', Sadistic Brawlers | A1ALMMGEF_OnMeleeCLMEffect, dlc03_Legendary_OnMeleeCLMEffect | Does not work |
| Auto-Medical, Aid Patch | A1ALMMGEF_OnHealthUseStim (auto-stimpak) | Possible scriptless stand-in: heal over time while health is low |
| Vampiric, Raging, Annihilating, Reaper's Embrace, Reclaimer's | A1ALMMGEF_DrainOnHitScript (2.0 fix) | Can fall back to 1.09's version: heals on hits, not on kills |
| Face Bustin' | A1ALMMGEF_ExplodeAfterDeathScript (2.0 fix) | Can keep cripple and speed; "explode after death" dropped |

Undecided: leave the "does not work" group (about 30) out of the PS build, or ship it with this note.

## Systems that need a CLM script

- Configuration holotape menus and the quest that gives the holotape: replaced by chemistry station settings (Option 2).
- Loot mode: drops themselves need no script. Giving the player the loot perk (scripted quest) and the drop-rate menu
  need scriptless versions: the perk from a "book" item (as vanilla magazines grant perks - seen working in the first
  loot prototype, to confirm when crafted), the rates as settings items read by the drop perk's conditions.

---

## Copy-paste: Bethesda.net / readme (plain text)

PLAYSTATION NOTE
PlayStation mods cannot use custom scripts, so a few legendaries cannot work there and are left out of the
PlayStation version: the Untouchable legendaries, Shavka's Explosive Striking, Brutish, Burning Rage, Constantly
Flamin' Cloaked, Ridiculously Absorbin' and Sadistic Brawlers. On PlayStation, Vampiric (and Raging, Annihilating,
Reaper's Embrace, Reclaimer's) heals on every hit except killing blows, Face Bustin' does not blow targets apart, and
Auto-Medical and Aid Patch heal gradually instead of using stimpaks. Everything else works the same as on PC and Xbox.

## Copy-paste: Nexus (BBCode)

[size=4][b]PlayStation note[/b][/size]
PlayStation mods cannot use custom scripts, so a few legendaries cannot work there and are left out of the PlayStation version:
[list]
[*]Untouchable (all), Shavka's Explosive Striking (all), Brutish, Burning Rage, Constantly Flamin' Cloaked, Ridiculously Absorbin', Sadistic Brawlers.
[/list]
On PlayStation:
[list]
[*]Vampiric, Raging, Annihilating, Reaper's Embrace and Reclaimer's heal on every hit except killing blows.
[*]Face Bustin' cripples but does not blow targets apart.
[*]Auto-Medical and Aid Patch heal gradually instead of using stimpaks.
[/list]
Everything else works the same as on PC and Xbox.

(The copy-paste texts assume the "leave them out" option and the fallbacks above; adjust if that changes.)
