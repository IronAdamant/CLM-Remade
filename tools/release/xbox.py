"""Xbox archives: made by the Creation Kit's Generate, staged and checked here.

    python tools/release/xbox.py stage     copy CLM's loose files into the game's Data folder, for the CK
    python tools/release/xbox.py achlist   write the file list to Import in the CK's Generate (work/CLM_xbox.achlist)
    python tools/release/xbox.py check     check the "- Main_xbox.ba2" / "- Textures_xbox.ba2" the CK wrote there
    python tools/release/xbox.py unstage   take the staged loose files out of Data again, and move the _xbox
                                           archives to work/xbox_upload (a PC game with them in Data can crash)

Archive2's XBoxDDS format keeps the textures in the PC layout (tile mode 8): Sandbox Room 1.0.0 shipped such archives
and Xbox players got pink textures. The Creation Kit's Generate ("Upload Plugin and Archive to Bethesda.net", Xbox)
tiles them for the console, but it builds the archives from loose files in Data, and since the packed tests CLM's
files are in Data as PC archives. `stage` copies the loose set (the same files as the PC archives and the Nexus
"Loose" option) into Data, skipping files already there unchanged and stopping on a different one; it records what it
added so `unstage` removes exactly those. Loose files override the PC archives, but they are the same files.

Generate's own file list can be wrong (for Sandbox Room it added vanilla Form/ObjectReference/ScriptObject.pex and
missed files only the add-ons use); `achlist` writes the right list, to Import in Generate's file list.
"""
from __future__ import annotations

import argparse
import json
import shutil
import struct
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from package import STEM, stage  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
STAGED = REPO / 'work' / 'xbox_staged.txt'
ACHLIST = REPO / 'work' / 'CLM_xbox.achlist'
XBOX_KEEP = REPO / 'work' / 'xbox_upload'
XBOX_ARCHIVES = (f'{STEM} - Main_xbox.ba2', f'{STEM} - Textures_xbox.ba2')
PC_TILE_MODE = 8           # what Archive2 writes for PC, and for XBoxDDS; the CK's Xbox textures have 13


def loose_files(root: Path) -> dict[str, Path]:
    return {f.relative_to(root).as_posix(): f for f in root.rglob('*') if f.is_file()}


def cmd_stage(data: Path) -> None:
    if STAGED.exists():
        raise SystemExit(f'{STAGED} exists: already staged (run unstage first)')
    with tempfile.TemporaryDirectory() as tmp:
        files = loose_files(stage(Path(tmp)))
        clash = [rel for rel, f in files.items() if (data / rel).exists() and (data / rel).read_bytes() != f.read_bytes()]
        if clash:
            raise SystemExit('Data already has different copies of these files; not touching them:\n  ' + '\n  '.join(clash))
        added = []
        for rel, f in sorted(files.items()):
            if not (data / rel).exists():
                (data / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, data / rel)
                added.append(rel)
    STAGED.parent.mkdir(parents=True, exist_ok=True)
    STAGED.write_text('\n'.join(added) + '\n', encoding='utf8')
    print(f'{len(added)} loose files copied into Data ({len(files) - len(added)} were already there). '
          'Now generate the Xbox archives in the Creation Kit, then run: xbox.py check')
    cmd_achlist(data)


def cmd_achlist(data: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        files = loose_files(stage(Path(tmp)))
    rels = sorted(rel for rel in files if not rel.lower().startswith('scripts/source/'))
    ACHLIST.parent.mkdir(parents=True, exist_ok=True)
    ACHLIST.write_text(json.dumps(['Data\\' + rel.replace('/', '\\') for rel in rels], indent='\t'), encoding='utf8')
    print(f"{ACHLIST}: {len(rels)} files, to Import in the Creation Kit's Generate")


def cmd_unstage(data: Path) -> None:
    if not STAGED.exists():
        raise SystemExit('nothing staged')
    rels = [r for r in STAGED.read_text(encoding='utf8').splitlines() if r]
    for rel in rels:
        (data / rel).unlink(missing_ok=True)
    for rel in rels:                                    # drop folders the staging created and left empty
        d = (data / rel).parent
        while d != data and d.exists() and not any(d.iterdir()):
            d.rmdir()
            d = d.parent
    STAGED.unlink()
    print(f'{len(rels)} staged loose files removed from Data')
    for name in XBOX_ARCHIVES:
        if (data / name).exists():
            XBOX_KEEP.mkdir(parents=True, exist_ok=True)
            shutil.move(data / name, XBOX_KEEP / name)
            print(f'{name} moved to {XBOX_KEEP}')


def read_ba2(path: Path) -> tuple[bytes, dict[str, int | None]]:
    """The archive type (GNRL or DX10) and its files: normalised path -> tile mode (None for GNRL)."""
    b = path.read_bytes()
    magic, _, typ, n, names_at = struct.unpack('<4sI4sIQ', b[:24])
    if magic != b'BTDX':
        raise SystemExit(f'{path.name}: not a BA2 archive')
    o, tiles = 24, []
    for _ in range(n):
        if typ == b'GNRL':
            tiles.append(None)
            o += 36
        else:
            chunks, tile = b[o + 13], b[o + 23]
            tiles.append(tile)
            o += 24 + 24 * chunks
    files = {}
    for tile in tiles:
        size = struct.unpack('<H', b[names_at:names_at + 2])[0]
        files[b[names_at + 2:names_at + 2 + size].decode().replace('\\', '/').lower()] = tile
        names_at += 2 + size
    return typ, files


def check(path: Path, typ_wanted: bytes, want: set[str]) -> list[str]:
    if not path.exists():
        return [f'{path.name}: missing']
    typ, files = read_ba2(path)
    problems = [f'{path.name}: {typ.decode()} archive, expected {typ_wanted.decode()}'] if typ != typ_wanted else []
    problems += [f'{path.name}: missing {f}' for f in sorted(want - files.keys())]
    problems += [f'{path.name}: not part of the mod: {f}' for f in sorted(files.keys() - want)
                 if not f.startswith('scripts/source/')]  # script sources are harmless
    problems += [f'{path.name}: PC layout (not tiled for Xbox): {f}' for f, tile in sorted(files.items())
                 if tile == PC_TILE_MODE]
    return problems


def cmd_check(data: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        files = {rel.lower() for rel in loose_files(stage(Path(tmp)))}
    main = {f for f in files if f.startswith('meshes/') or (f.startswith('scripts/') and f.endswith('.pex'))}
    textures = {f for f in files if f.startswith('textures/')}
    problems = (check(data / f'{STEM} - Main_xbox.ba2', b'GNRL', main)
                + check(data / f'{STEM} - Textures_xbox.ba2', b'DX10', textures))
    for p in problems:
        print(p)
    if problems:
        raise SystemExit(f'{len(problems)} problem(s): do not upload these Xbox archives')
    print(f'Xbox archives OK: all {len(main)} scripts and meshes and {len(textures)} textures, tiled for Xbox')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=('stage', 'achlist', 'check', 'unstage'))
    ap.add_argument('--game', default='D:/Steam/steamapps/common/Fallout 4')
    a = ap.parse_args()
    data = Path(a.game) / 'Data'
    {'stage': cmd_stage, 'achlist': cmd_achlist, 'check': cmd_check, 'unstage': cmd_unstage}[a.command](data)


if __name__ == '__main__':
    main()
