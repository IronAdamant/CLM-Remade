# PlayStation (PS4/PS5) version

PlayStation mods may not include custom scripts or assets: the upload is the plugins only. `dist/PlayStation/` is
built from the finished PC plugins by `tools/release/playstation.py` (also run by `tools/release/package.py`), with
the author's decisions of 2026-10-12. Checked: no CLM script attached anywhere, no recipe reaches a CLM mesh or
texture, FO4Edit: 0 errors in all five plugins.

The chemistry station settings and the Legendary Picker are what make CLM work on PlayStation (and on Xbox, and on
PC without F4SE): they need no scripts. Upload as for PC/Xbox: the plugin only, no archives. Requirements:
Automatron, Far Harbor, Contraptions Workshop and Nuka-World.

## What is different on PlayStation

| Content | PlayStation |
|---|---|
| Configuration and perk holotapes | Not given, not craftable (a holotape runs scripts). Settings: chemistry station. |
| Loot mode | Works. The drop perk comes from a "CLM Loot Manual" magazine, made once at the chemistry station (CLM Settings) while Loot mode is on. If nothing drops, drop the manual and pick it up again. |
| Energized Green / Purple / Gold / Orange / Pink / Deep Blue, Disintegratin' Purple / Gold / Orange / Pink / Deep Blue | Left out (new textures and meshes). Energized Red, Blue, Plasma and Gauss stay. |
| Disintegratin' (Green) | Vanilla plasma "goo" again (the green ash is a new asset). |
| Custom Spawning: Kellogg | Left out (custom face files). |
| Vampiric, Raging, Annihilating, Reaper's Embrace, Reclaimer's | 1.09's version: heal on every hit except killing blows. |
| Auto-Medical / Aid Patch | Regenerate about 6% of health per second (a stimpak's rate; the amount steps up with your level, as a fixed amount is all a plugin can restore) while at or below 20% / 50% health; no stimpak used, no cooldown. Uses vanilla RegenerateHealthAbility: heal rate does nothing in combat. |
| Face Bustin' | Cripples and speeds as before; targets are not blown apart. |
| Untouchable (all), Shavka's Explosive Striking (all), Ridiculously Absorbin', Sadistic Brawlers | Kept, with a note: their effect is a script, so it does nothing on PlayStation. |
| Brutish, Burning Rage, Constantly Flamin' Cloaked, One Punch Man's, God Father's, Generic 80s Action Hero's | Kept, with a note: one part of their effect is a script (e.g. the self-heal on hits of Full Invulnerability). |
| Everything else (settings, picker, ~570 legendaries) | Same as PC and Xbox. |

Re-run the build before every release (it starts from data/*.esp). Testing on PC:
`python tools/release/playstation.py --test-install`, play (with CLM - MCM.esp unticked), then `--test-restore`.

---

## Copy-paste: Bethesda.net PlayStation description

See `bethesda_net_playstation_description.txt` (Bethesda.net allows 1,988 characters).

## Copy-paste: readme (plain text)

PLAYSTATION VERSION
PlayStation mods cannot use scripts or new assets, so this version differs a little:
- Settings are made at any chemistry station (CLM Settings); there are no holotapes.
- Loot mode: also make the CLM Loot Manual (CLM Settings) once to start getting drops. If nothing drops, drop the
  manual and pick it up again.
- Left out: the new laser colours (Energized and Disintegratin' Green, Purple, Gold, Orange, Pink, Deep Blue) and
  the Kellogg spawn.
- Vampiric and its family heal on every hit except killing blows. Auto-Medical and Aid Patch regenerate health
  quickly while you are low instead of using stimpaks. Face Bustin' does not blow targets apart.
- Untouchable, Shavka's Explosive Striking, Ridiculously Absorbin' and Sadistic Brawlers do nothing on PlayStation
  (their effect is a script); a few others lose one scripted part. Their descriptions say so.

## Copy-paste: Nexus (BBCode)

[size=4][b]PlayStation version[/b][/size]
CLM 2.0 is also on Bethesda.net for PS4/PS5. PlayStation mods cannot use scripts or new assets, so there:
[list]
[*]Settings are made at the chemistry station (no holotapes); loot mode also needs the CLM Loot Manual, made once there.
[*]The new laser colours and the Kellogg spawn are left out.
[*]Vampiric and its family heal on every hit except killing blows; Auto-Medical and Aid Patch regenerate health instead of using stimpaks; Face Bustin' does not blow targets apart.
[*]Untouchable, Shavka's Explosive Striking, Ridiculously Absorbin' and Sadistic Brawlers do nothing there; a few others lose one scripted part.
[/list]
