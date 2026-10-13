"""Nexus description: write the HTML (paste into Nexus's editor) and BBCode versions from nexus_description.md.

    python tools/release/description.py

Handles what the description uses: a title (#) and its italic tagline, sections (##), paragraphs, bulleted lists,
**bold** and *italic*.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

REL = Path(__file__).resolve().parents[2] / 'docs' / 'release'
SRC = REL / 'nexus_description.md'


def inline(text: str, fmt: str) -> str:
    if fmt == 'html':
        text = html.escape(text, quote=False)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        return re.sub(r'(?<!\*)\*(?!\*)(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
    return re.sub(r'(?<!\*)\*(?!\*)(.+?)\*', r'[i]\1[/i]', text)


def blocks(md: str):
    """(kind, payload): title, tagline, h2, p, list."""
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith('# '):
            yield 'title', line[2:]
            i += 1
        elif line.startswith('## '):
            yield 'h2', line[3:]
            i += 1
        elif line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                items.append(lines[i][2:])
                i += 1
            yield 'list', items
        elif re.fullmatch(r'\*[^*].*\*', line.strip()):
            yield 'tagline', line.strip()[1:-1]
            i += 1
        else:
            yield 'p', line
            i += 1


def to_html(md: str) -> str:
    out = ['<!doctype html>', '<html lang="en"><head><meta charset="utf-8"><title>CLM Nexus description</title></head>',
           '<body>', '<!-- Open in a browser, Ctrl+A, Ctrl+C, paste into the Nexus description editor. Generated from '
           'nexus_description.md. -->']
    for kind, x in blocks(md):
        if kind == 'title':
            out.append(f'<h1>{inline(x, "html")}</h1>')
        elif kind == 'tagline':
            out.append(f'<p><i>{inline(x, "html")}</i></p>')
        elif kind == 'h2':
            out.append(f'<h2>{inline(x, "html")}</h2>')
        elif kind == 'p':
            out.append(f'<p>{inline(x, "html")}</p>')
        else:
            out += ['<ul>'] + [f'<li>{inline(item, "html")}</li>' for item in x] + ['</ul>']
    return '\n'.join(out + ['</body></html>']) + '\n'


def to_bbcode(md: str) -> str:
    out = []
    for kind, x in blocks(md):
        if kind == 'title':
            out.append(f'[center][size=6][b]{inline(x, "bb")}[/b][/size]')
        elif kind == 'tagline':
            out.append(f'[size=3]{inline(x, "bb")}[/size][/center]')
        elif kind == 'h2':
            out += ['', f'[size=4][b]{inline(x, "bb")}[/b][/size]']
        elif kind == 'p':
            out.append(inline(x, 'bb'))
        else:
            out += ['[list]'] + [f'[*]{inline(item, "bb")}' for item in x] + ['[/list]']
    return '\n'.join(out) + '\n'


def main():
    md = SRC.read_text(encoding='utf8')
    (REL / 'nexus_description.html').write_text(to_html(md), encoding='utf8')
    (REL / 'nexus_description.bbcode').write_text(to_bbcode(md), encoding='utf8')
    print('nexus_description.html and .bbcode written')


if __name__ == '__main__':
    main()
