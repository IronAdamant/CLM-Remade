"""Package a CLM release: BA2 archives for PC and Xbox, and the Nexus zip (a FOMOD installer).

    python tools/release/package.py --version 2.0.0 [--game "D:/Steam/steamapps/common/Fallout 4"]

Fallout 4 loads "<plugin> - Main.ba2" and "<plugin> - Textures.ba2" beside a plugin by itself, so every loose file
the mod needs goes into the main plugin's two archives (the DLC add-ons are plugins only):
    Custom Legendary Modifications Remade - Main.ba2      Scripts (compiled, plus their sources), meshes (General)
    Custom Legendary Modifications Remade - Textures.ba2  textures                                         (DDS)
The Creation Kit's Bethesda.net upload looks for the Xbox versions as "- Main_xbox.ba2" and "- Textures_xbox.ba2"
(XBoxDDS textures, Xbox compression). Output in dist/:
    PC/      the main plugin + PC archives, and the add-ons            (Bethesda.net PC uploads)
    Xbox/    the main plugin + _xbox archives, and the add-ons         (Bethesda.net Xbox uploads)
    CLM Remade <version>.zip   for Nexus: a FOMOD that installs the main mod, ticks the add-ons for the DLC the
                               player has, and offers the optional F4SE menu (mcm/data: "CLM - MCM", needs F4SE and
                               Mod Configuration Menu; loose files, as MCM reads its menu from loose files). Nexus
                               only: the Bethesda.net uploads (PC/, Xbox/) never include it.
The debug recorder (debug/) is a testing tool and never packaged.
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
ADDONS = [  # (plugin, DLC master, what it adds)
    ('CLM - Automatron.esp', 'DLCRobot.esm', 'the 13 robot-spawning legendaries'),
    ('CLM - Far Harbor.esp', 'DLCCoast.esm',
     "Far Harbor's creature and Trapper spawns, Paintball, Trappin', Moby-Dick's and the Silenced Harpoon Striker"),
    ('CLM - Nuka-World.esp', 'DLCNukaWorld.esm', "Nuka-World's creature and raider spawns"),
    ('CLM - Contraptions.esp', 'DLCworkshop02.esm', 'Pyrotechnical and Weather Altering'),
]
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


def fomod(version: str) -> tuple[str, str]:
    info = f"""<fomod>
  <Name>Custom Legendary Modifications Remade</Name>
  <Author>Deadmansprice</Author>
  <Version>{version}</Version>
  <Description>Over 570 legendary effects to craft at the workbench, or to hunt for as loot. Set up at any chemistry station, with a holotape, or (optional, F4SE) from the pause menu.</Description>
  <Groups><element>Weapons</element><element>Armour</element><element>Gameplay</element></Groups>
</fomod>
"""
    plugins = []
    for plugin, master, adds in ADDONS:
        title = plugin.removesuffix('.esp')
        plugins.append(f"""          <plugin name="{title}">
            <description>Adds {adds}. Needs the {title.removeprefix('CLM - ')} DLC.</description>
            <files><file source="Add-ons\\{plugin}" destination="{plugin}" priority="0"/></files>
            <typeDescriptor>
              <dependencyType>
                <defaultType name="Optional"/>
                <patterns>
                  <pattern><dependencies operator="And"><fileDependency file="{master}" state="Active"/></dependencies><type name="Recommended"/></pattern>
                  <pattern><dependencies operator="And"><fileDependency file="{master}" state="Missing"/></dependencies><type name="NotUsable"/></pattern>
                </patterns>
              </dependencyType>
            </typeDescriptor>
          </plugin>""")
    config = f"""<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
  <moduleName>Custom Legendary Modifications Remade</moduleName>
  <requiredInstallFiles>
    <folder source="Core" destination=""/>
  </requiredInstallFiles>
  <installSteps order="Explicit">
    <installStep name="DLC add-ons">
      <optionalFileGroups order="Explicit">
        <group name="Add-ons for the DLC you own (each needs its DLC)" type="SelectAny">
          <plugins order="Explicit">
{chr(10).join(plugins)}
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
    for platform, suffix, tex_fmt, comp in (('PC', '', 'DDS', 'Default'), ('Xbox', '_xbox', 'XBoxDDS', 'XBox')):
        out = DIST / platform
        archive2(game, root, ['Scripts', 'Meshes'], out / f'{STEM} - Main{suffix}.ba2', 'General', comp)
        archive2(game, root, ['Textures'], out / f'{STEM} - Textures{suffix}.ba2', tex_fmt, comp)
        for plugin in [MAIN] + [p for p, _, _ in ADDONS]:
            shutil.copy(DATA / plugin, out / plugin)
    zpath = DIST / f'CLM Remade {a.version}.zip'
    info, config = fomod(a.version)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('fomod/info.xml', info)
        z.writestr('fomod/ModuleConfig.xml', config)
        for name in (MAIN, f'{STEM} - Main.ba2', f'{STEM} - Textures.ba2'):
            z.write(DIST / 'PC' / name, f'Core/{name}')
        z.write(README, f'Core/{README.name}')
        for plugin, _, _ in ADDONS:
            z.write(DIST / 'PC' / plugin, f'Add-ons/{plugin}')
        for f in sorted(MCM_DATA.rglob('*')):        # the optional F4SE menu, loose
            if f.is_file():
                z.write(f, f'F4SE Menu/{f.relative_to(MCM_DATA).as_posix()}')
        for f in sorted(MCM_SOURCE.glob('*.psc')):
            z.write(f, f'F4SE Menu/Scripts/Source/User/{f.name}')
    shutil.rmtree(tmp)
    for f in sorted(DIST.rglob('*')):
        if f.is_file():
            print(f'{f.relative_to(DIST)}  {f.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
