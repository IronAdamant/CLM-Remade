"""Package a CLM release: BA2 archives for PC, plugins for Xbox and PlayStation, and the Nexus zip (a FOMOD installer).

    python tools/release/package.py --version 2.0.0 [--game "D:/Steam/steamapps/common/Fallout 4"]

Fallout 4 loads "<plugin> - Main.ba2" and "<plugin> - Textures.ba2" beside a plugin by itself, so every loose file
the mod needs goes into the plugin's two archives. One plugin: it needs Automatron, Far Harbor, Contraptions
Workshop and Nuka-World (the DLC add-ons were merged into it, 2026-10-12):
    Custom Legendary Modifications Remade - Main.ba2      Scripts (compiled, plus their sources), meshes (General)
    Custom Legendary Modifications Remade - Textures.ba2  textures                                         (DDS)
No Xbox archives: Archive2's XBoxDDS format keeps the textures in the PC layout (tile mode 8; Sandbox Room 1.0.0
shipped them so and Xbox players got pink textures). The Creation Kit's Generate ("Upload Plugin and Archive to
Bethesda.net") tiles them for the console: tools/release/xbox.py stages the loose files in Data for it and checks the
"- Main_xbox.ba2" / "- Textures_xbox.ba2" it writes. Output in dist/:
    PC/      the plugin + PC archives                                (Bethesda.net PC upload)
    PlayStation/  the plugin only (tools/release/playstation.py)      (Bethesda.net PS4/PS5 upload)
    Xbox/    the plugin; the archives come from the CK (xbox.py)     (Bethesda.net Xbox upload)
    CLM Remade <version>.zip   for Nexus: a FOMOD that checks the four DLC are there, installs the mod as packed
                               archives (BA2, default) or loose files (for mod tools / players who prefer loose), and
                               offers the optional F4SE menu (mcm/data: "CLM - MCM", needs F4SE and Mod Configuration
                               Menu; loose files, as MCM reads its menu from loose files). Nexus only: the Bethesda.net
                               uploads (PC/, Xbox/) never include it.
The debug recorder (debug/) is a testing tool and never packaged.

PC archives are stamped BA2 version 1. The Creation Kit's Archive2 (next-gen update, 2024) writes version 8, which
game versions before that update (1.10.163 and older, still widely played) silently ignore - no scripts, no
textures. Versions 1, 7 and 8 share the same layout for Fallout 4 (only the number differs) and the current game
reads version 1, so v1 archives work on every PC version.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / 'data'
DIST = REPO / 'dist'
MAIN = 'Custom Legendary Modifications Remade.esp'
STEM = MAIN.removesuffix('.esp')
DLC = ['DLCRobot.esm', 'DLCCoast.esm', 'DLCworkshop02.esm', 'DLCNukaWorld.esm']   # the plugin's masters
README = REPO / 'docs' / 'release' / 'CLM Remade - Readme.txt'
MCM_DATA = REPO / 'mcm' / 'data'
MCM_SOURCE = REPO / 'mcm' / 'source'


def stage(tmp: Path) -> Path:
    """The loose files laid out as a Data folder."""
    root = tmp / 'Data'
    shutil.copytree(DATA / 'SCRIPTS', root / 'Scripts')
    shutil.copytree(REPO / 'source' / 'User', root / 'Scripts' / 'Source' / 'User')
    shutil.copytree(DATA / 'Meshes', root / 'Meshes')
    shutil.copytree(DATA / 'Textures', root / 'Textures')
    return root


def archive2(game: Path, root: Path, folders: list[str], out: Path, fmt: str, compression: str) -> None:
    exe = game / 'Tools' / 'Archive2' / 'Archive2.exe'
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(exe), ','.join(str(root / f) for f in folders), f'-create={out}', f'-root={root}',
                        f'-format={fmt}', f'-compression={compression}', '-quiet'], capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        raise SystemExit(f'Archive2 failed for {out.name}:\n{r.stdout}\n{r.stderr}')


def stamp_v1(path: Path) -> None:
    """Mark a Fallout 4 BA2 as version 1 so pre-next-gen game versions load it (layout is unchanged)."""
    with open(path, 'r+b') as f:
        head = f.read(8)
        assert head[:4] == b'BTDX' and int.from_bytes(head[4:8], 'little') in (1, 7, 8), (path, head)
        f.seek(4)
        f.write((1).to_bytes(4, 'little'))


def fomod(version: str) -> tuple[str, str]:
    info = f"""<fomod>
  <Name>Custom Legendary Modifications Remade</Name>
  <Author>Deadmansprice</Author>
  <Version>{version}</Version>
  <Description>Over 570 legendary effects to craft at the workbench, or to hunt for as loot. Set up at any chemistry station, with a holotape, or (optional, F4SE) from the pause menu.</Description>
  <Groups><element>Weapons</element><element>Armour</element><element>Gameplay</element></Groups>
</fomod>
"""
    needs = '\n'.join(f'    <fileDependency file="{m}" state="Active"/>' for m in DLC)
    config = f"""<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
  <moduleName>Custom Legendary Modifications Remade</moduleName>
  <moduleDependencies operator="And">
{needs}
  </moduleDependencies>
  <requiredInstallFiles>
    <folder source="Core" destination=""/>
  </requiredInstallFiles>
  <installSteps order="Explicit">
    <installStep name="Files">
      <optionalFileGroups order="Explicit">
        <group name="How to install CLM's scripts, meshes and textures" type="SelectExactlyOne">
          <plugins order="Explicit">
            <plugin name="Packed archives (recommended)">
              <description>Two BA2 archives next to the plugin. Works on every PC game version, current and older (1.10.163).</description>
              <files><folder source="Packed" destination="" priority="0"/></files>
              <typeDescriptor><type name="Recommended"/></typeDescriptor>
            </plugin>
            <plugin name="Loose files">
              <description>The same files unpacked into Data (Scripts, Meshes, Textures), including the script sources. For players and mod tools that prefer loose files.</description>
              <files><folder source="Loose" destination="" priority="0"/></files>
              <typeDescriptor><type name="Optional"/></typeDescriptor>
            </plugin>
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
    <installStep name="F4SE menu (PC)">
      <optionalFileGroups order="Explicit">
        <group name="Optional: set CLM up from the pause menu" type="SelectAny">
          <plugins order="Explicit">
            <plugin name="CLM - MCM">
              <description>Needs F4SE and Mod Configuration Menu (MCM). Puts every CLM setting and the perk holotape's 110 perks in the pause menu (Mod Config), replacing the configuration and perk holotapes (they can be turned back on in the menu). Works on the same setting items as the chemistry station. Skip this without F4SE.</description>
              <files><folder source="F4SE Menu" destination="" priority="0"/></files>
              <typeDescriptor><type name="Optional"/></typeDescriptor>
            </plugin>
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
  </installSteps>
</config>
"""
    return info, config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', required=True)
    ap.add_argument('--game', default='D:/Steam/steamapps/common/Fallout 4')
    a = ap.parse_args()
    game = Path(a.game)
    if DIST.exists():
        shutil.rmtree(DIST)
    tmp = DIST / '_stage'
    root = stage(tmp)
    archive2(game, root, ['Scripts', 'Meshes'], DIST / 'PC' / f'{STEM} - Main.ba2', 'General', 'Default')
    archive2(game, root, ['Textures'], DIST / 'PC' / f'{STEM} - Textures.ba2', 'DDS', 'Default')
    for name in (f'{STEM} - Main.ba2', f'{STEM} - Textures.ba2'):
        stamp_v1(DIST / 'PC' / name)
    for platform in ('PC', 'Xbox'):
        (DIST / platform).mkdir(parents=True, exist_ok=True)
        shutil.copy(DATA / MAIN, DIST / platform / MAIN)
    zpath = DIST / f'CLM Remade {a.version}.zip'
    info, config = fomod(a.version)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('fomod/info.xml', info)
        z.writestr('fomod/ModuleConfig.xml', config)
        z.write(DIST / 'PC' / MAIN, f'Core/{MAIN}')
        for name in (f'{STEM} - Main.ba2', f'{STEM} - Textures.ba2'):
            z.write(DIST / 'PC' / name, f'Packed/{name}')
        for f in sorted(root.rglob('*')):              # the loose alternative: the staged Data folder
            if f.is_file():
                z.write(f, f'Loose/{f.relative_to(root).as_posix()}')
        z.write(README, f'Core/{README.name}')
        for f in sorted(MCM_DATA.rglob('*')):        # the optional F4SE menu, loose
            if f.is_file():
                z.write(f, f'F4SE Menu/{f.relative_to(MCM_DATA).as_posix()}')
        for f in sorted(MCM_SOURCE.glob('*.psc')):
            z.write(f, f'F4SE Menu/Scripts/Source/User/{f.name}')
    shutil.rmtree(tmp)
    import playstation                                  # dist/PlayStation: plugins only, no scripts or assets
    playstation.build(game)
    for f in sorted(DIST.rglob('*')):
        if f.is_file():
            print(f'{f.relative_to(DIST)}  {f.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
