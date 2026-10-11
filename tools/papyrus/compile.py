"""Compile CLM Papyrus sources from source/User into data/SCRIPTS.

    python tools/papyrus/compile.py --game "D:/Steam/steamapps/common/Fallout 4" A1ALMMGEF_OnMeleeEffect Fragments:Terminals:TERM_X

Compiles against the game's vanilla sources only (Data/Scripts/Source/Base), never the F4SE sources that may be
installed next to them: CLM must not depend on F4SE (1.09 accidentally shipped F4SE's ScriptObject that way).
Uses the same settings as the 2017 builds (release, final, not optimised).

    python tools/papyrus/compile.py --game "..." --debug A1ALMDBG_RecorderScript

--debug builds testing-only scripts from debug/source into debug/SCRIPTS (never shipped) and keeps their
Debug.Trace/TraceUser calls, which release builds strip.

    python tools/papyrus/compile.py --game "..." --f4se mcm/source --mcm "<MCM mod>/Scripts/Source/User" A1ALMMCMScript

--f4se builds a script of the optional F4SE add-on (the MCM menu) from that folder into its data/Scripts folder,
against the F4SE sources (Data/Scripts/Source) and, with --mcm, MCM's API (MCM.psc, not redistributed).
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
DEBUG_SOURCE = REPO / 'debug' / 'source'
DEBUG_OUTPUT = REPO / 'debug' / 'SCRIPTS'


def compile_script(game: Path, name: str, debug: bool = False, f4se: Path | None = None,
                   mcm: Path | None = None) -> Path:
    base = game / 'Data' / 'Scripts' / 'Source' / 'Base'
    compiler = game / 'Papyrus Compiler' / 'PapyrusCompiler.exe'
    with tempfile.TemporaryDirectory() as tmp:
        imports = f'{DEBUG_SOURCE};{SOURCE};{base}' if debug else f'{SOURCE};{base}'
        if f4se:   # F4SE's ScriptObject etc. come before the vanilla ones they extend
            imports = ';'.join(str(x) for x in (f4se, mcm, SOURCE, base.parent, base) if x)
        flags = [] if debug else ['-release', '-final']
        r = subprocess.run([str(compiler), name, f'-i={imports}', f'-o={tmp}',
                            f'-f={base / "Institute_Papyrus_Flags.flg"}', '-quiet'] + flags,
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f'compile failed for {name}:\n{r.stdout}\n{r.stderr}')
        built = next(Path(tmp).rglob(name.split(':')[-1] + '.pex'))
        out = f4se.parent / 'data' / 'Scripts' if f4se else DEBUG_OUTPUT if debug else OUTPUT
        dest = out.joinpath(*name.split(':')[:-1]) / built.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(built, dest)
        return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    ap.add_argument('--debug', action='store_true', help='testing-only script from debug/source; keep traces')
    ap.add_argument('--f4se', type=Path, help='source folder of an F4SE add-on script (e.g. mcm/source)')
    ap.add_argument('--mcm', type=Path, help="MCM's Scripts/Source/User folder (MCM.psc)")
    ap.add_argument('scripts', nargs='+', help='script names, namespaced with ":" (e.g. Fragments:Terminals:TERM_X)')
    a = ap.parse_args()
    for name in a.scripts:
        print('compiled', compile_script(Path(a.game), name, a.debug, a.f4se and a.f4se.resolve(),
                                         a.mcm).relative_to(REPO))


if __name__ == '__main__':
    main()
