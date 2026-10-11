"""Catalog of every CLM legendary as the plugin really builds it, for checking effects against descriptions.

    python tools/audit/catalog.py EXPORT_DIR [--out docs/CATALOG.md] [--only NAME_FRAGMENT ...]

EXPORT_DIR is an AgentCreationKit export_records run folder (one text file per record type, every field decoded):
    python -m ack xedit run export_records "Custom Legendary Modifications Remade.esp"
For each legendary (OMOD): name, description, its properties, and for enchantments the chain enchantment -> magic
effects (archetype, actor value, magnitude, duration, casting) -> perk entry points (with their values), and the
projectile -> explosion (damage, radius) for projectile overrides.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def blocks(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    text = '\n' + path.read_text(encoding='utf8', errors='replace')
    out = {}
    for b in text.split('\n==== ')[1:]:
        head = b.splitlines()[0].split()
        if len(head) >= 3:
            out[head[2]] = b
    return out


def field(block: str, name: str) -> str:
    m = re.search(rf'\n\s*{re.escape(name)} = (.*)', block)
    return m.group(1).strip() if m else ''


def edid_of(value: str) -> str:
    return value.split()[0] if value else ''


class Catalog:
    def __init__(self, export: Path):
        self.r = {sig: blocks(export / f'{sig}.txt') for sig in ('OMOD', 'ENCH', 'MGEF', 'PERK', 'SPEL', 'PROJ', 'EXPL')}

    def props(self, omod: str) -> list[tuple[str, str, str, str]]:
        b = self.r['OMOD'][omod]
        out = []
        # each property starts at a line that is just "Property"; its fields follow until the next one
        parts = re.split(r'\n\s+Property\n', '\n' + b.split('\n    Properties\n', 1)[-1] + '\n')[1:]
        for p in parts:
            out.append((field('\n' + p, 'Function Type'), field('\n' + p, 'Property'), field('\n' + p, 'Value 1'),
                        field('\n' + p, 'Value 2')))
        return out

    def perk(self, edid: str, depth: int) -> list[str]:
        b = self.r['PERK'].get(edid)
        if not b:
            return [f'{"  " * depth}PERK {edid} (not in CLM)']
        lines = []
        for ep in re.finditer(r'Entry Point = (.+)\n\s+Function = (.+)', b):
            lines.append(f'{"  " * depth}entry point: {ep.group(1).strip()} / {ep.group(2).strip()}')
        vals = re.findall(r'\n\s+(?:Float|Value|Spell|Leveled Item|Actor Value) = (.+)', b)
        if vals:
            lines.append(f'{"  " * depth}values: ' + '; '.join(v.strip()[:60] for v in vals[:6]))
        spells = re.findall(r'\n\s+Spell = (\S+)', b)
        for s in spells[:2]:
            lines += self.spell(s, depth)
        return lines

    def mgef(self, edid: str, mag: str, dur: str, depth: int) -> list[str]:
        b = self.r['MGEF'].get(edid)
        if not b:
            return [f'{"  " * depth}MGEF {edid} (vanilla) magnitude {mag} duration {dur}']
        arch, av = field(b, 'Archetype'), edid_of(field(b, 'Actor Value'))
        cast, deliv = field(b, 'Casting Type'), field(b, 'Delivery')
        line = f'{"  " * depth}{edid}: {arch}{" " + av if av and av != "NULL" else ""}, magnitude {mag}, ' \
               f'duration {dur} ({cast}, {deliv})'
        lines = [line]
        perk = edid_of(field(b, 'Perk to Apply'))
        if perk and perk != 'NULL':
            lines += self.perk(perk, depth + 1)
        expl = edid_of(field(b, 'Explosion'))
        if expl and expl != 'NULL':
            lines += self.explosion(expl, depth + 1)
        script = field(b, 'ScriptName')
        if script:
            lines.append(f'{"  " * (depth + 1)}script {script}')
        return lines

    def effects(self, block: str, depth: int) -> list[str]:
        lines = []
        # each effect: EFID, its EFIT values, then any conditions (CTDA) until the next EFID
        for chunk in re.split(r'\n\s+Effect\n', block)[1:]:
            m = re.search(r'EFID - Base Effect = (\S+).*?Magnitude = ([\d.\-]+).*?Duration = (\d+)', chunk, re.S)
            if not m:
                continue
            lines += self.mgef(m.group(1), m.group(2), m.group(3), depth)
            for c in re.finditer(r'Type = ([01]+)\n.*?Comparison Value = ([\d.\-]+)\n.*?Function = (\S+)'
                                 r'(?:\n.*?Parameter #1 = (\S+))?', chunk, re.S):
                lines.append(f'{"  " * (depth + 1)}if {c.group(3)}'
                             f'{"(" + c.group(4) + ")" if c.group(4) and c.group(4) != "00" else ""} '
                             f'[{c.group(1)}] {c.group(2)}')
        return lines

    def spell(self, edid: str, depth: int) -> list[str]:
        b = self.r['SPEL'].get(edid) or self.r['ENCH'].get(edid)
        if not b:
            return [f'{"  " * depth}spell {edid} (vanilla)']
        return [f'{"  " * depth}spell {edid}'] + self.effects(b, depth + 1)

    def explosion(self, edid: str, depth: int) -> list[str]:
        b = self.r['EXPL'].get(edid)
        if not b:
            return [f'{"  " * depth}explosion {edid} (vanilla)']
        return [f'{"  " * depth}explosion {edid}: damage {field(b, "Damage")}, radius {field(b, "Outer Radius")}']

    def legendary(self, omod: str) -> list[str]:
        b = self.r['OMOD'][omod]
        out = [f'### {field(b, "FULL - Name")}  `{omod}`', f'> {field(b, "DESC - Description")}', '```']
        for fn, prop, v1, v2 in self.props(omod):
            out.append(f'{prop} {fn} {v1}{" / " + v2 if v2 else ""}')
            if prop == 'Enchantments':
                e = edid_of(v1)
                eb = self.r['ENCH'].get(e)
                if eb:
                    out.append(f'  ENCH {e} ({field(eb, "Casting Type")}, {field(eb, "Delivery")})')
                    out += self.effects(eb, 2)
            elif prop == 'OverrideProjectile':
                pb = self.r['PROJ'].get(edid_of(v1))
                if pb:
                    out.append(f'  PROJ type {field(pb, "Type")}, speed {field(pb, "Speed")}, gravity '
                               f'{field(pb, "Gravity")}')
                    ex = edid_of(re.search(r'\n\s+Explosion = (\S+ ?.*)', pb).group(1)) if re.search(
                        r'\n\s+Explosion = (?!1|0)\S', pb) else ''
                    if ex and ex != 'NULL':
                        out += self.explosion(ex, 2)
        out.append('```')
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('export')
    ap.add_argument('--out', default='')
    ap.add_argument('--only', nargs='*', default=[])
    a = ap.parse_args()
    cat = Catalog(Path(a.export))
    names = sorted(cat.r['OMOD'])
    if a.only:
        names = [n for n in names if any(o.lower() in (n + field(cat.r['OMOD'][n], 'FULL - Name')).lower()
                                         for o in a.only)]
    text = '\n'.join(line for n in names for line in cat.legendary(n) + [''])
    if a.out:
        Path(a.out).write_text('# CLM catalog (generated by tools/audit/catalog.py)\n\n' + text, encoding='utf8')
        print(f'{len(names)} legendaries -> {a.out}')
    else:
        print(text)


if __name__ == '__main__':
    main()
