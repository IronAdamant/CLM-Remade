"""Configuration holotape: hide each setting option while it is the active setting (author's request, 2026-10-11).

Choosing an option hides it and brings back whichever option was active before, so the menu shows only real
choices. For every configuration terminal, each menu item's script fragment is read from source/User (what it really
sets, not what its label says) and the item gets conditions "show unless every global it sets already has that value":
    GetGlobalValue(G1) != v1  OR  GetGlobalValue(G2) != v2  OR ...
An item that sets one global gets a single condition. The loot drop-rate menu (a terminal script, not fragments) uses
A1ALMLOOTRATE: item N hides while it equals N - 1. Re-runnable: managed items get their conditions rewritten.

Usage: python terminal_hide_selected.py <plugin.esp>   (edits in place; FO4Edit must not have it open)
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402
from ack.plugin.records import Subrecord  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
FRAGMENTS = REPO / 'source' / 'User' / 'Fragments' / 'Terminals'
FN_GET_GLOBAL_VALUE = 74
OP_NE, FLAG_OR = 1 << 5, 0x01
RATE_TERM, RATE_GLOBAL = 'A1ALMTERM_Holotape_Config_LootRate', 'A1ALMLOOTRATE'


def ctda(op_flags: int, value: float, glob: int) -> Subrecord:
    return Subrecord('CTDA', struct.pack('<B3sfH2sIIIIi', op_flags, b'\0\0\0', value, FN_GET_GLOBAL_VALUE, b'\0\0',
                                         glob, 0, 0, 0, -1))


def fragment_sets(script: str) -> dict[int, list[tuple[str, float]]]:
    """Menu item ID -> [(global, value)] from a terminal fragment script (Fragment_Terminal_NN sets ...)."""
    text = (FRAGMENTS / f'{script}.psc').read_text(encoding='utf8')
    out = {}
    for m in re.finditer(r'Function Fragment_Terminal_(\d+)\(.*?\n(.*?)EndFunction', text, re.S):
        sets = re.findall(r'(\w+)\.SetValue\(([-\d.]+)\)', m.group(2))
        if sets:
            out[int(m.group(1))] = [(g, float(v)) for g, v in sets]
    return out


def set_item_conditions(term, item_id: int, conds: list[Subrecord]) -> None:
    subs = term.subrecords
    starts = [i for i, s in enumerate(subs) if s.sig == 'ITXT'] + [len(subs)]
    for k in range(len(starts) - 1):
        a, b = starts[k], starts[k + 1]
        ids = [struct.unpack('<H', s.data)[0] for s in subs[a:b] if s.sig == 'ITID']
        if ids == [item_id]:
            # keep the item's own fields, replace its conditions (they come last in an item)
            while b > a and subs[b - 1].sig not in ('ITXT', 'RNAM', 'ANAM', 'ITID', 'TNAM', 'UNAM', 'VNAM', 'CTDA',
                                                    'CIS1', 'CIS2'):
                b -= 1  # (the last item may be followed by other record fields)
            body = [s for s in subs[a:b] if s.sig not in ('CTDA', 'CIS1', 'CIS2')]
            subs[a:b] = body + conds
            term.mark_dirty()
            return
    raise SystemExit(f'{term.edid}: no menu item {item_id}')


def main():
    path = sys.argv[1]
    p = Plugin.load(path)
    glob = {r.edid: r.formid for r in p.records('GLOB') if p.is_own(r.formid)}
    for term in p.records('TERM'):
        if 'Config' not in term.edid:
            continue
        if term.edid == RATE_TERM:
            for item in (1, 2, 3):
                set_item_conditions(term, item, [ctda(OP_NE, float(item - 1), glob[RATE_GLOBAL])])
                print(f'{term.edid} item {item}: hidden while {RATE_GLOBAL} == {item - 1}')
            continue
        vmad = term.get('VMAD')
        scripts = set(re.findall(rb'Fragments:Terminals:(TERM_\w+)', vmad.data)) if vmad else set()
        for script in scripts:
            for item, sets in sorted(fragment_sets(script.decode()).items()):
                conds = [ctda(OP_NE | (FLAG_OR if i < len(sets) - 1 else 0), v, glob[g])
                         for i, (g, v) in enumerate(sets)]
                set_item_conditions(term, item, conds)
                print(f'{term.edid} item {item}: hidden while ' + ' and '.join(f'{g} == {v:g}' for g, v in sets))
    p.save(path)


if __name__ == '__main__':
    main()
