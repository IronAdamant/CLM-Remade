"""Flag legendaries whose description promises a mechanism their effects do not contain.

    python tools/audit/promises.py docs/CATALOG.md

A coarse first pass over the catalog (tools/audit/catalog.py): for each description, every promise word below must
be matched by evidence somewhere in that legendary's effect chain (properties, enchantments, magic effects, perks,
explosions). Flags need a human look - wording can be loose - but a flag usually means a missing effect.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# promise (regex on the description) -> evidence (regex on the effect chain)
RULES = [
    (r'bleed', r'Bleed'),
    (r'crippl', r'Crippl|LimbDam|Cripple'),
    (r'frenz|rage in|enrag|induces rage', r'Frenzy|Rage'),
    (r'vampir|drain|leech|restores? health|heal', r'Absorb|Heal|RestoreHealth|Health, magnitude|Vampir'),
    (r'burn|fire damage|on fire|incendiar|ignit', r'dtFire|Fire|Burn|Incendiar|Flame|Molotov'),
    (r'freez|cryo', r'Cryo|Freeze|Frost|dtCryo'),
    (r'stagger', r'Stagger'),
    (r'flying|push|knock', r'Push|GrandSlam|Knock|Stagger|Ragdoll'),
    (r'explo', r'xplosion|xplosive|EXP|Missile|Grenade|Mine'),
    (r'critical', r'Crit'),
    (r'penetrat|armou?r piercing|ignores? .*(armou?r|resist)', r'Penetrat|Resistance|ArmorPenetration|Resist'),
    (r'sneak attack', r'Sneak'),
    (r'stun|paraly', r'Paraly|Stun'),
    (r'poison', r'Poison'),
    (r'radiat|radioact', r'Rad'),
    (r'shock|electric|lightning', r'Electr|Shock|Lightning'),
    (r'silenc|suppress', r'Silenc|Suppress'),
    (r'invisib|undetect|stealth|ghostly|chameleon', r'Stealth|Chameleon|Invis|Undetect|Ghost|Sneak'),
    (r'fire ?rate|attack speed|faster attack', r'Speed'),
    (r'recoil', r'Recoil'),
    (r'\brange\b', r'Range'),
    (r'accura', r'Cone|Accura|Aim|Sway'),
    (r'ammo capacity|magazine|clip size|\bammo\b', r'Ammo|Capacity'),
    (r'reload', r'Reload'),
    (r'damage resist', r'DamageResist|Resistance'),
    (r'carry', r'CarryWeight|Carry'),
    (r'vats', r'VATS|Vats'),
    (r'never-?ending|infinite', r'Ammo|NeverEnding|Neverending'),
]


def entries(text: str):
    for block in text.split('\n### ')[1:]:
        head = block.splitlines()[0]
        desc = re.search(r'\n> (.*)', block)
        chain = block.split('```', 1)[1] if '```' in block else ''
        yield head, desc.group(1) if desc else '', chain


def main():
    text = Path(sys.argv[1]).read_text(encoding='utf8')
    flagged = 0
    for head, desc, chain in entries(text):
        missing = [p for p, ev in RULES if re.search(p, desc, re.I) and not re.search(ev, chain)]
        if missing:
            flagged += 1
            print(f'{head}\n    "{desc[:200]}"\n    missing: {", ".join(missing)}')
    print(f'\n{flagged} legendaries flagged')


if __name__ == '__main__':
    main()
