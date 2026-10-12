# Uploading to Bethesda.net

`python tools/release/package.py --version X.Y.Z` builds `dist/`:

| Folder | What | Use |
|---|---|---|
| `dist/PC/` | the five plugins + `- Main.ba2` / `- Textures.ba2` (version 1) | PC |
| `dist/Xbox/` | the five plugins; the archives come from the Creation Kit's Generate | Xbox |
| `dist/PlayStation/` | the five PlayStation plugins, no archives | PS4/PS5 (see `PLAYSTATION.md`) |

Every upload goes through the Creation Kit: File > Data, tick only the plugin being uploaded, set it active, OK
(never save); then File > Upload Plugin and Archive to Bethesda.net. Leave "Upload as Light Master" unticked (the
add-ons are already light through their ESL flag). Text: `bethesda_net_description_1000.txt` (1,000 characters
max), `bethesda_net_playstation_description.txt` for PlayStation.

## PC and Xbox: the main plugin

1. `Fallout 4\Data` holds the PC plugins and PC archives from `dist/PC/`.
2. `python tools/release/xbox.py stage`: copies CLM's loose files into `Data` for Generate, and writes
   `work/CLM_xbox.achlist`.
3. In the upload dialog, PC: Include Archives ticked, the existing `- Main.ba2` / `- Textures.ba2`. Do not
   Generate for PC: it would replace the version-1 archives.
4. Xbox: **always Generate**, never Archive2's XBoxDDS (it keeps the PC texture layout: pink textures on Xbox).
   In Generate's file list, Import `work/CLM_xbox.achlist` (111 files), so no vanilla scripts get in and nothing
   is missed.
5. Before uploading: `python tools/release/xbox.py check`. Upload only when it prints "Xbox archives OK".
6. After uploading: `python tools/release/xbox.py unstage` (removes the staged files and moves the `_xbox`
   archives to `work/xbox_upload`: a PC game with them in `Data` can crash).

## The DLC add-ons (PC, Xbox, PlayStation)

One creation each, plugin only (Include Archives unticked): `CLM - Automatron.esp`, `CLM - Far Harbor.esp`,
`CLM - Nuka-World.esp`, `CLM - Contraptions.esp`. Requirements: Custom Legendary Modifications Remade and the DLC.

## PlayStation

1. `python tools/release/playstation.py --test-install` (the PlayStation plugins replace the PC ones in `Data`).
2. Upload the main plugin and the four add-ons for PlayStation, plugins only.
3. `python tools/release/playstation.py --test-restore`.
