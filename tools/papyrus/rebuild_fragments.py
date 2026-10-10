"""Rebuild Papyrus sources (.psc) for CLM's terminal fragment scripts from the compiled .pex files.

The 2017 sources were lost; only compiled scripts shipped. This is a one-time recovery tool: after the
recovered sources are committed, source/ is the truth and fixes are made there. Re-running it would
overwrite those fixes with what the compiled scripts contain. Terminal fragments are simple enough to reconstruct
exactly: every fragment is one or more of
    Game.GetPlayer().AddPerk(P) / Game.GetPlayer().RemovePerk(P) / SomeGlobal.SetValue(n)
The decompiler only accepts those instruction patterns and stops on anything else, so it can never silently
produce a wrong source.

    python tools/papyrus/rebuild_fragments.py --game "D:/Steam/steamapps/common/Fallout 4" [--verify]

--verify compiles each rebuilt source with the game's PapyrusCompiler and checks that its code is
instruction-for-instruction identical to the original (ignoring temp variable names and line numbers).
Sources are written in the Creation Kit's fragment layout so the CK can keep editing them.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PEX_DIR = REPO / 'data' / 'SCRIPTS' / 'Fragments' / 'Terminals'
SRC_DIR = REPO / 'source' / 'User' / 'Fragments' / 'Terminals'


def disassemble(game: Path, pex: Path, workdir: Path) -> str:
    """Disassemble a namespaced fragment .pex with PapyrusAssembler; returns the .pas text."""
    tree = workdir / 'Fragments' / 'Terminals'
    tree.mkdir(parents=True, exist_ok=True)
    shutil.copy(pex, tree / pex.name)
    assembler = game / 'Papyrus Compiler' / 'PapyrusAssembler.exe'
    subprocess.run([str(assembler), f'Fragments:Terminals:{pex.stem}', '-D', '-Q'], cwd=workdir, check=True,
                   capture_output=True)
    return (workdir / f'{pex.stem}.disassemble.pas').read_text(encoding='latin1')


def parse(pas: str):
    obj = re.search(r'\.object (\S+) (\w+)(?: (const))?\n\s*\.userFlags (\d+)', pas)
    name, parent, const, flags = obj.group(1), obj.group(2), obj.group(3), int(obj.group(4))
    props = re.findall(r'\.property (\w+) ([\w\[\]]+) auto\b', pas)
    funcs = {}
    for m in re.finditer(r'\.function (Fragment_\w+)\n(.*?)\.endFunction', pas, re.S):
        code = m.group(2).split('.code', 1)[1].split('.endCode', 1)[0]
        lines = [re.sub(r'\s*;@line \d+', '', l).strip() for l in code.strip().splitlines() if l.strip()]
        funcs[m.group(1)] = decompile(m.group(1), lines)
    return name, parent, const, flags, props, funcs


def decompile(fn: str, lines: list[str]) -> list[str]:
    out, player, casts = [], {}, {}
    for l in lines:
        if m := re.fullmatch(r'CallStatic game GetPlayer (::temp\d+)', l):
            player[m.group(1)] = True
        elif m := re.fullmatch(r'CallMethod (AddPerk|RemovePerk) (::temp\d+) ::nonevar ::(\w+)_var(?: (False|True))?', l):
            if m.group(2) not in player:
                raise ValueError(f'{fn}: {m.group(1)} on something other than the player: {l}')
            out.append(f'Game.GetPlayer().{m.group(1)}({m.group(3)})')
        elif m := re.fullmatch(r'Cast (::temp\d+) (-?[\d.]+)', l):
            casts[m.group(1)] = m.group(2)
        elif m := re.fullmatch(r'CallMethod SetValue ::(\w+)_var ::nonevar (::temp\d+)', l):
            out.append(f'{m.group(1)}.SetValue({casts[m.group(2)]})')
        else:
            raise ValueError(f'{fn}: unsupported instruction: {l}')
    return out


# Compiled scripts store type names in lower case; restore the spelling the Creation Kit writes.
TYPE_NAMES = {'perk': 'Perk', 'globalvariable': 'GlobalVariable', 'terminal': 'Terminal'}


def type_name(t: str) -> str:
    base, arr = (t[:-2], '[]') if t.endswith('[]') else (t, '')
    return TYPE_NAMES.get(base.lower(), base[:1].upper() + base[1:]) + arr


def render(name, parent, const, flags, props, funcs) -> str:
    mods = (' Hidden' if flags & 1 else '') + (' Const' if const else '')
    s = [';BEGIN FRAGMENT CODE - Do not edit anything between this and the end comment',
         f'Scriptname {name} Extends {type_name(parent)}{mods}', '']
    for fn in sorted(funcs, key=lambda f: int(re.search(r'\d+$', f).group())):
        s += [f';BEGIN FRAGMENT {fn}', f'Function {fn}(ObjectReference akTerminalRef)', ';BEGIN CODE']
        s += funcs[fn]
        s += [';END CODE', 'EndFunction', ';END FRAGMENT', '']
    s += [';END FRAGMENT CODE - Do not edit anything between this and the begin comment', '']
    for pname, ptype in sorted(props, key=lambda p: p[0].lower()):
        s.append(f'{type_name(ptype)} Property {pname} Auto Const')
    return '\n'.join(s) + '\n'


def compile_source(game: Path, psc: Path, out: Path) -> Path:
    """Compile a fragment source against the vanilla script sources. Not optimised: the 2017 originals were built
    without -optimize (e.g. int-to-float conversions happen at run time), and the rebuild must match them exactly."""
    base = game / 'Data' / 'Scripts' / 'Source' / 'Base'
    user_root = psc.parents[2]  # .../User (contains Fragments/Terminals)
    compiler = game / 'Papyrus Compiler' / 'PapyrusCompiler.exe'
    # Pass the namespaced script name, not a path: the compiler derives the namespace from the name and finds the
    # file through the import folders (as the CK does).
    r = subprocess.run([str(compiler), f'Fragments:Terminals:{psc.stem}', f'-i={user_root};{base}', f'-o={out}',
                        f'-f={base / "Institute_Papyrus_Flags.flg"}', '-release', '-final', '-quiet'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'compile failed for {psc.name}:\n{r.stdout}\n{r.stderr}')
    return next(out.rglob(psc.stem + '.pex'))


def code_signature(pas: str) -> dict[str, list[str]]:
    """Per-function code with temp names and line numbers normalised, for comparing two builds."""
    sig = {}
    for m in re.finditer(r'\.function (Fragment_\w+)\n(.*?)\.endFunction', pas, re.S):
        code = m.group(2).split('.code', 1)[1].split('.endCode', 1)[0]
        lines = [re.sub(r'::temp\d+', 'T', re.sub(r'\s*;@line \d+', '', l)).strip()
                 for l in code.strip().splitlines() if l.strip()]
        sig[m.group(1)] = lines
    return sig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    ap.add_argument('--verify', action='store_true')
    a = ap.parse_args()
    game = Path(a.game)
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for pex in sorted(PEX_DIR.glob('*.pex')):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            original = disassemble(game, pex, tmp / 'orig')
            parsed = parse(original)
            psc = SRC_DIR / f'{pex.stem}.psc'
            psc.write_text(render(*parsed), encoding='utf8', newline='\r\n')
            status = f'{len(parsed[5])} fragments, {len(parsed[4])} properties'
            if a.verify:
                built = compile_source(game, psc, tmp / 'build')
                rebuilt = disassemble(game, built, tmp / 'rebuilt')
                same = code_signature(original) == code_signature(rebuilt)
                props_same = sorted(re.findall(r'\.property (\w+ \w+)', original)) == \
                    sorted(re.findall(r'\.property (\w+ \w+)', rebuilt))
                ok &= same and props_same
                status += f' | recompiled code identical: {same}, properties identical: {props_same}'
            print(f'{pex.stem:45} {status}')
    if a.verify and not ok:
        raise SystemExit('verification FAILED')


if __name__ == '__main__':
    main()
