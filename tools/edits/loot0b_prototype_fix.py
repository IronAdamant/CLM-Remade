"""Loot mode prototype, fix after the first in-game test (2026-10-10).

1. The unlock holotape stayed in the inventory and granted no perk. Every vanilla book that grants a perk carries
   the PerkMagKeyword and FeaturedItem keywords; the prototype had removed them. Put both back (still no script).
2. A loose mod alone did not reveal its legendary: the workbench lists a mod only when a recipe for it is visible.
   Jumpy (100%)'s unlocked recipe now shows with the unlock perk OR at least one loose mod in the inventory:
     [0] HasPerk(A1ALMPERK_Unlock_Jumpy) == 1   OR
     [1] GetItemCount(loose mod) >= 1
   xEdit shows the CTDA type byte as a confusing flag string, so these bytes are written directly.

Usage: python loot0b_prototype_fix.py <plugin.esp>   (edits in place; FO4Edit must not have it open)
"""
import struct
import sys

sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin  # noqa: E402
from ack.plugin.records import Subrecord  # noqa: E402

PERK_MAG_KEYWORD = 0x001D4A70     # Fallout4.esm (master index 0)
FEATURED_ITEM = 0x001B3FAC
FN_HAS_PERK, FN_GET_ITEM_COUNT = 448, 47
OP_EQ, OP_GE, FLAG_OR = 0 << 5, 3 << 5, 0x01
RUN_ON_SUBJECT = 0


def ctda(op_flags: int, value: float, function: int, param1: int) -> bytes:
    return struct.pack('<B3sfH2sIIIIi', op_flags, b'\0\0\0', value, function, b'\0\0', param1, 0,
                       RUN_ON_SUBJECT, 0, -1)


path = sys.argv[1]
p = Plugin.load(path)

book = p.by_edid('A1ALMBOOK_Unlock_Jumpy')
if not book.get('KWDA'):
    i = next(i for i, s in enumerate(book.subrecords) if s.sig == 'DATA')
    book.subrecords[i:i] = [Subrecord('KSIZ', struct.pack('<I', 2)),
                            Subrecord('KWDA', struct.pack('<II', FEATURED_ITEM, PERK_MAG_KEYWORD))]
    book.mark_dirty()
    print('holotape: keywords restored')

perk = p.by_edid('A1ALMPERK_Unlock_Jumpy').formid
loose = p.by_edid('A1ALMMISC_LooseMod_Armor_PerkV_Fortify_Jumpy_100').formid
recipe = p.by_edid('co_A1ALMOMOD_Legendary_Armor_PerkV_Fortify_Jumpy_100_Unlocked')
conds = [s for s in recipe.subrecords if s.sig == 'CTDA']
assert len(conds) == 2, conds
conds[0].data = ctda(OP_EQ | FLAG_OR, 1.0, FN_HAS_PERK, perk)
conds[1].data = ctda(OP_GE, 1.0, FN_GET_ITEM_COUNT, loose)
recipe.mark_dirty()
print(f'recipe: HasPerk {perk:08X} == 1 OR GetItemCount {loose:08X} >= 1')
p.save(path)
