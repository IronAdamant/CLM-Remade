"""Prove a recovered script source matches the shipped one: compile source/User/<name>.psc with 1.09's settings and
compare its disassembly with data/SCRIPTS/<name>.pex.

    python tools/papyrus/verify_recovered.py --game "D:/Steam/steamapps/common/Fallout 4" NAME [NAME ...]

The code must match line for line (statements and their line markers). Timestamps, paths, user, machine and
docstrings are ignored, and the compiler's flag, variable and property tables are compared as sets, since it writes
them in no stable order (two 1.09 builds of the same script differ there).
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def disassemble(game: Path, pex: Path) -> list[str]:
    asm = game / 'Papyrus Compiler' / 'PapyrusAssembler.exe'
    subprocess.run([str(asm), pex.stem, '-D', '-Q'], cwd=pex.parent, capture_output=True)
    text = (pex.parent / f'{pex.stem}.disassemble.pas').read_text(encoding='utf8', errors='replace')
    skip = re.compile(r'^\s*\.(source|user|computer|modifyTime|compileTime|docString)\b')
    lines = [' '.join(l.split()) for l in text.splitlines() if not skip.match(l)]  # column padding varies
    out, block, flags = [], None, []
    in_group = False
    for l in lines:
        if l.startswith('.propertyGroup'):
            in_group = not l.startswith('.propertyGroupTable') or in_group
        if l.startswith('.flag '):
            flags.append(l)
        elif not in_group and l.startswith(('.variable ', '.property ')):
            block = [l]
        elif block is not None:
            block.append(l)
            if l in ('.endVariable', '.endProperty'):
                out.append('TABLE ' + ' | '.join(block))
                block = None
        else:
            out.append(l)
        if l == '.endPropertyGroupTable':
            in_group = False
    tables = sorted(x for x in out if x.startswith('TABLE '))
    # functions: also written in no stable order - compare each whole function (its code stays in order)
    rest, funcs, cur = [], [], None
    for x in out:
        if x.startswith('TABLE '):
            continue
        if x.startswith('.function '):
            cur = [x]
        elif cur is not None:
            cur.append(x)
            if x == '.endFunction':
                # jump labels are numbered differently between builds: renumber by first appearance
                text, names = ' | '.join(cur), {}
                text = re.sub(r'_label\d+', lambda m: names.setdefault(m.group(0), f'L{len(names)}'), text)
                funcs.append(text)
                cur = None
        else:
            rest.append(x)
    return sorted(flags) + tables + rest + ['FUNCTION ' + f for f in sorted(funcs)]


def verify(game: Path, name: str) -> bool:
    base = game / 'Data' / 'Scripts' / 'Source' / 'Base'
    compiler = game / 'Papyrus Compiler' / 'PapyrusCompiler.exe'
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([str(compiler), name, f'-i={REPO / "source" / "User"};{base}', f'-o={tmp}',
                            f'-f={base / "Institute_Papyrus_Flags.flg"}', '-release', '-final', '-quiet'],
                           capture_output=True, text=True)
        if r.returncode:
            print(f'{name}: compile failed\n{r.stdout}{r.stderr}')
            return False
        built = next(Path(tmp).rglob(f'{name.split(":")[-1]}.pex'))
        orig = Path(tmp) / 'orig' / built.name
        orig.parent.mkdir()
        shutil.copy(REPO / 'data' / 'SCRIPTS' / Path(*name.split(':')).with_suffix('.pex'), orig)
        new, old = disassemble(game, built), disassemble(game, orig)
        diff = [(i, x, y) for i, (x, y) in enumerate(zip(new, old)) if x != y]
        same = not diff and len(new) == len(old)
        print(f'{name}: {"IDENTICAL to the shipped .pex" if same else "DIFFERS"}')
        for i, x, y in diff[:12]:
            print(f'   {i}: new {x[:100]}\n      old {y[:100]}')
        return same


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    ap.add_argument('names', nargs='+')
    a = ap.parse_args()
    ok = all([verify(Path(a.game), n) for n in a.names])
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
