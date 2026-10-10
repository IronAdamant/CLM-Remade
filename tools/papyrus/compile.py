"""Compile CLM Papyrus sources from source/User into data/SCRIPTS.

    python tools/papyrus/compile.py --game "D:/Steam/steamapps/common/Fallout 4" A1ALMMGEF_OnMeleeEffect Fragments:Terminals:TERM_X

Compiles against the game's vanilla sources only (Data/Scripts/Source/Base), never the F4SE sources that may be
installed next to them: CLM must not depend on F4SE (1.09 accidentally shipped F4SE's ScriptObject that way).
Uses the same settings as the 2017 builds (release, final, not optimised).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'source' / 'User'
OUTPUT = REPO / 'data' / 'SCRIPTS'


def compile_script(game: Path, name: str) -> Path:
    base = game / 'Data' / 'Scripts' / 'Source' / 'Base'
    compiler = game / 'Papyrus Compiler' / 'PapyrusCompiler.exe'
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([str(compiler), name, f'-i={SOURCE};{base}', f'-o={tmp}',
                            f'-f={base / "Institute_Papyrus_Flags.flg"}', '-release', '-final', '-quiet'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f'compile failed for {name}:\n{r.stdout}\n{r.stderr}')
        built = next(Path(tmp).rglob(name.split(':')[-1] + '.pex'))
        dest = OUTPUT.joinpath(*name.split(':')[:-1]) / built.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(built, dest)
        return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    ap.add_argument('scripts', nargs='+', help='script names, namespaced with ":" (e.g. Fragments:Terminals:TERM_X)')
    a = ap.parse_args()
    for name in a.scripts:
        print('compiled', compile_script(Path(a.game), name).relative_to(REPO))


if __name__ == '__main__':
    main()
