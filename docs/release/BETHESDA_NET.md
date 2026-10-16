# Uploading to Bethesda.net

`python tools/release/package.py --version X.Y.Z` builds `dist/`:

| Folder | What | Use |
|---|---|---|
| `dist/PC/` | the plugin + `- Main.ba2` / `- Textures.ba2` (version 1) | PC |
| `dist/Xbox/` | the plugin; the archives come from the Creation Kit's Generate | Xbox |
| `dist/PlayStation/` | the PlayStation plugin, no archives | PS4/PS5 (see `PLAYSTATION.md`) |

One plugin; requirements on every platform: Automatron, Far Harbor, Contraptions Workshop, Nuka-World.

Every upload goes through the Creation Kit: File > Data, tick only `Custom Legendary Modifications Remade.esp`, set
it active, OK (never save); then File > Upload Plugin and Archive to Bethesda.net. Leave "Upload as Light Master"
unticked. Text: `bethesda_net_description.txt` (the CK allows about 3,000 characters), `bethesda_net_playstation_description.txt`
for PlayStation.

## PC and Xbox

1. `Fallout 4\Data` holds the PC plugin and PC archives from `dist/PC/`.
2. `python tools/release/xbox.py stage`: copies CLM's loose files into `Data` for Generate, and writes
   `work/CLM_xbox.achlist`.
3. In the upload dialog, PC: Include Archives ticked, the existing `- Main.ba2` / `- Textures.ba2`. Do not
   Generate for PC: it would replace the version-1 archives.
4. Xbox: **always Generate**, never Archive2's XBoxDDS (it keeps the PC texture layout: pink textures on Xbox).
   In Generate's file list, Import `work/CLM_xbox.achlist` (125 files in 2.1), so no vanilla scripts get in and nothing
   is missed.
5. Before uploading: `python tools/release/xbox.py check`. Upload only when it prints "Xbox archives OK".
6. After uploading: `python tools/release/xbox.py unstage` (removes the staged files and moves the `_xbox`
   archives to `work/xbox_upload`: a PC game with them in `Data` can crash).

## PlayStation

1. `python tools/release/playstation.py --test-install` (the PlayStation plugin replaces the PC one in `Data`).
2. Upload the plugin for PlayStation, plugin only (no archives).
3. `python tools/release/playstation.py --test-restore`.
