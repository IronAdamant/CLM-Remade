"""Build the PlayStation (PS4/PS5) version of CLM from the finished PC plugins: no custom scripts, no custom assets.

    python tools/release/playstation.py --game "D:/Steam/steamapps/common/Fallout 4"      (also run by package.py)
    python tools/release/playstation.py --test-install     try it on PC: the PS plugins replace the PC ones in Data
    python tools/release/playstation.py --test-restore     put the PC plugins back

PlayStation mods may not include scripts or assets: the upload is the plugins only. The settings and the Legendary
Picker already work without scripts (chemistry station items). Author's decisions (2026-10-12), applied to copies of
data/, written to dist/PlayStation/:
- every CLM script is detached (VMAD removed where all its scripts are CLM's; vanilla scripts stay);
- the holotapes are never given or craftable (A1ALMHOLOTAPES = 0): playing one runs a script; the perk holotape's
  perks become "CLM Perk" magazines made at the chemistry station (category CLM Perks): reading one adds the perk
  (adding only: removing a perk needs a script);
- legendaries that need CLM assets are left out (recipes and loot drops removed): the six new laser colours
  (Energized) and the five new Disintegratin' colours; Disintegratin' (Green) goes back to the plasma "goo" (vanilla
  CritPlasma); the Kellogg spawn (custom face files);
- Midas' borrows Disintegratin' (Gold)'s gold dust (CLM art): vanilla red ash instead, caps unchanged;
- BioReactive (all) and Singularity: vanilla Fortune Finder's script instead of CLM's on-hit one: they explode on
  killing hits only;
- Vampiric, Raging, Annihilating, Reaper's Embrace, Reclaimer's: 1.09's Absorb Health (BloodDrain) instead of the
  scripted drain: heals on every hit except killing blows;
- Auto-Medical / Aid Patch: instead of the scripted auto-stimpak, regenerate about 6% of health per second (a
  stimpak's rate: 30% over 5 s) while health is at or below 20% / 50%; no stimpak used, no cooldown. Vanilla's
  RegenerateHealthAbility restores health directly (heal rate does nothing in combat: fCombatHealthRegenRateMult is
  0); it restores a fixed amount per second, so the amount steps up with the player's level (HEAL_TIERS);
- Face Bustin': the explode-after-death effect has no script, so targets are not blown apart (text says so);
- the other legendaries whose effect is a CLM script stay, with a PlayStation note in their description;
- loot mode: its drop perk was given by a scripted quest. Instead a "CLM Loot Manual" magazine (BOOK teaching the
  loot perk, as vanilla magazines teach perks) is made once at the chemistry station
  (CLM Settings) while Loot mode is on. The perk's own conditions still check the Loot mode setting.
"""
from __future__ import annotations

import argparse
import csv
import re
import shutil
import struct
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / 'tools' / 'config'))
sys.path.insert(0, 'D:/Coding Projects/AgentCreationKit')
from ack.plugin import Plugin, Record, Group, Subrecord  # noqa: E402
from settings import ITEMS, setting_global, on_conds, ctda, OP_EQ, CATEGORY  # noqa: E402

MAIN = 'Custom Legendary Modifications Remade.esp'
OUT = REPO / 'dist' / 'PlayStation'
SCRIPTS = REPO / 'data' / 'SCRIPTS'

COLOURS = ['Green', 'Purple', 'Gold', 'Orange', 'Pink', 'DeepBlue']
LEFT_OUT = ([f'A1ALMOMOD_Legendary_Weapon_Energized_Laser_{c}' for c in COLOURS] +
            [f'A1ALMOMOD_Legendary_Weapon_Contact_Disintegration_Variant_{c}' for c in COLOURS if c != 'Green'] +
            ['A1ALMOMOD_Legendary_Weapon_Custom_Spawning_Hostile_UniqueNPC_Kellog'])
DISINTEGRATIN_GREEN = 'A1ALMOMOD_Legendary_Weapon_Contact_Disintegration_Variant_Green'
GREEN_SWAPS = {'A1ALMSPEL_CritLaserGreen': 0x00139F8C, 'A1ALMEFSH_CritLaserGreen': 0x00139F97,   # CritPlasma, CritPlasmaFXS
               'A1ALMACTI_AshPileGreen': 0x00139F8D}                                             # GooPile01
DRAIN_TO_ABSORB = 'A1ALMMGEF_Target_Effect_Hostile_BloodDrain'
STIM = {'A1ALMOMOD_Legendary_Armour_StimpakSelfHeal': (0.20, 'Auto-heals you whenever your health is at or below 20%: '
                                                              'you regenerate about 6% of your health per second (as fast as a stimpak), '
                                                              'without using stimpaks. (PlayStation version.)'),
        'A1ALMOMOD_Legendary_Armour_StimpakSelfHeal_AidPatch': (0.50, 'Auto-heals you whenever your health is at or below 50%: '
                                                                       'you regenerate about 6% of your health per second (as fast as a '
                                                                       'stimpak), without using stimpaks. (PlayStation version.)')}
REGENERATE_HEALTH = 0x00102149           # RegenerateHealthAbility: constant restore health, per second
# (from level, health per second): about 6% of a level-L player's health with Endurance 5 (105 + 5 x (L - 1))
HEAL_TIERS = [(1, 7), (10, 11), (25, 17), (50, 25), (75, 32), (100, 40)]
FACE_BUSTIN = 'A1ALMEnch_FaF_Contact_Effect_Target_Hostile_FaceBusting'
NOTE_SCRIPT = ' (PlayStation: this effect needs a script, which PlayStation mods cannot have, so it does nothing there.)'
NOTE_PART = ' (PlayStation: part of this effect needs a script, which PlayStation mods cannot have; that part does nothing there.)'
NOTE_DRAIN = ' (PlayStation: heals on every hit except killing blows.)'
NOTE_FACE = ' (PlayStation: targets are not blown apart.)'
NOTE_KILL_ONLY = ' (PlayStation: explodes only on killing hits.)'
NOTE_MIDAS =' (PlayStation: they turn to ordinary ash, not gold dust.)'
MIDAS, CRIT_LASER = 'A1ALMOMOD_Legendary_Weapon_Midas', 0x000731B2      # vanilla CritLaser (red ash)
MAGAZINE = 'PerkMagLiveAndLove09'          # vanilla magazine used as the Loot Manual's template
FN_HAS_PERK, FN_GET_HEALTH_PERCENTAGE, FN_GET_LEVEL, OP_GE, OP_LT, OP_LE = 448, 430, 80, 3 << 5, 4 << 5, 5 << 5
BEFORE_BOOK = {'GMST', 'KYWD', 'LCRT', 'AACT', 'TRNS', 'CMPO', 'TXST', 'GLOB', 'DMGT', 'CLAS', 'FACT', 'HDPT', 'EYES',
               'RACE', 'SOUN', 'ASPC', 'MGEF', 'LTEX', 'ENCH', 'SPEL', 'ACTI', 'TACT', 'ARMO'}


def zstr(text: str) -> bytes:
    return text.encode('cp1252') + b'\0'


class Edit:
    def __init__(self, p: Plugin, main: Plugin):
        self.p, self.main = p, main
        self.own = {r.formid: r for r in p.records() if p.is_own(r.formid)}

    def see(self, edid: str) -> int:
        """Form ID of a main-plugin record as seen from this plugin"""
        r = self.main.by_edid(edid)
        if self.p is self.main:
            return r.formid
        return (self.p.masters.index(MAIN) << 24) | (r.formid & 0xFFFFFF)

    def remove(self, rec: Record) -> None:
        for g in self.p.groups:
            if rec in g.children:
                g.children.remove(rec)
                hedr = self.p.header.get('HEDR')
                v, n, nxt = struct.unpack('<fII', hedr.data)
                hedr.data = struct.pack('<fII', v, n - 1, nxt)
                self.p.header.mark_dirty()
                return
        raise ValueError(f'{rec} is not top-level')

    def add(self, rec: Record) -> Record:
        hedr = self.p.header.get('HEDR')
        v, n, nxt = struct.unpack('<fII', hedr.data)
        rec.formid = (len(self.p.masters) << 24) | nxt
        hedr.data = struct.pack('<fII', v, n + 1, nxt + 1)
        self.p.header.mark_dirty()
        group = self.p.top_group(rec.sig)
        if group is None:
            tail = self.p.groups[0].tail
            group = Group(rec.sig.encode('latin1'), 0, tail, [])
            at = next((i for i, g in enumerate(self.p.groups) if g.label_sig not in BEFORE_BOOK), len(self.p.groups))
            self.p.groups.insert(at, group)
        group.children.append(rec)
        self.own[rec.formid] = rec
        return rec


def custom_scripts() -> set[str]:
    return {p.relative_to(SCRIPTS).with_suffix('').as_posix().replace('/', ':').lower() for p in SCRIPTS.rglob('*.pex')} | \
        {p.stem.lower() for p in SCRIPTS.rglob('*.pex')}


def vmad_scripts(v: bytes, custom: set[str]) -> tuple[set[str], bool]:
    """CLM script names in a VMAD, and whether it names any other (vanilla) script"""
    tokens = {m.decode().lower() for m in re.findall(rb'[A-Za-z][\w:]{3,}', v)}
    mine = {t for t in tokens if t in custom}
    known_vanilla = {t for t in tokens if t in VANILLA}
    return mine, bool(known_vanilla)


VANILLA: set[str] = set()


def detach_scripts(e: Edit, custom: set[str]) -> list[str]:
    detached = []
    for r in list(e.own.values()):
        v = r.get('VMAD')
        if v is None:
            continue
        mine, vanilla = vmad_scripts(v.data, custom)
        if not mine:
            continue
        if vanilla:
            raise SystemExit(f'{r.edid}: CLM and vanilla scripts in one VMAD - handle by hand')
        r.subrecords[:] = [s for s in r.subrecords if s.sig != 'VMAD']
        r.mark_dirty()
        detached.append(r.edid)
    return detached


def reference_graph(e: Edit) -> dict[int, set[int]]:
    ids = set(e.own)
    graph = {}
    for fid, r in e.own.items():
        out = set()
        for s in r.subrecords:
            d = s.data
            for o in range(0, len(d) - 3):
                v = struct.unpack_from('<I', d, o)[0]
                if v in ids and v != fid:
                    out.add(v)
        graph[fid] = out
    return graph


def reaches(graph, start: int, targets: set[int], stop: set[int]) -> bool:
    seen, q = {start}, deque([start])
    while q:
        f = q.popleft()
        for n in graph.get(f, ()):
            if n in targets:
                return True
            if n not in seen and n not in stop:
                seen.add(n)
                q.append(n)
    return False


def append_desc(r: Record, note: str) -> None:
    d = r.get('DESC')
    text = d.zstring if d else ''
    if note.strip() not in text:
        r.set('DESC', zstr(text + note))


def build(game: Path) -> None:
    global VANILLA
    data = game / 'Data'
    custom = custom_scripts()
    # CLM's own sources can be in Scripts/Source/User too (loose installs, xbox.py stage): never vanilla
    VANILLA = {p.stem.lower() for root in [data / 'Scripts/Source/Base'] +
               [d for d in (data / 'Scripts/Source').iterdir() if d.is_dir()] for p in root.rglob('*.psc')} - custom
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    fo = Plugin.load(data / 'Fallout4.esm')
    magazine = fo.by_edid(MAGAZINE)
    main = Plugin.load(REPO / 'data' / MAIN)
    plugins = {MAIN: main}
    report = []

    m = Edit(main, main)
    platforms = {}     # legendary editor ID -> (status, PlayStation detail), for platforms.csv
    from mcm import perk_list
    perks = perk_list(main)            # from the perk holotape's fragments, before its scripts are detached
    fid = lambda edid: main.by_edid(edid).formid
    # BioReactive / Singularity: back to vanilla Fortune Finder's script, which explodes on killing hits only
    explode_on_kill = set()
    for r in main.records('MGEF'):
        v = r.get('VMAD').data if main.is_own(r.formid) and r.get('VMAD') is not None else b''
        if b'A1ALMMGEF_ExplodeOnHitEffect' in v:
            blast = struct.unpack_from('<I', v, len(v) - 4)[0]        # its one property, the explosion
            w = lambda s: struct.pack('<H', len(s)) + s.encode('ascii')
            r.set('VMAD', struct.pack('<hhH', 6, 2, 1) + w('FortuneFinderCapsScript') + b'\0' + struct.pack('<H', 1) +
                  w('PerkExplosionMoneyShotFortuneFinder') + b'\x01\x01' + struct.pack('<HhI', 0, -1, blast))
            r.mark_dirty()
            explode_on_kill.add(r.formid)
            report.append(f'kill-only explosion: {r.edid}')
    # scripted effects that get a PlayStation stand-in (so their users are not "script-only")
    fallback_mgefs ={r.formid for r in main.records('MGEF') if main.is_own(r.formid) and
                      re.search(r'DrainOnHit|ExplodeAfterDeath|HealLikeStimpak', r.edid)}
    script_mgefs = {f for f, r in m.own.items() if r.sig == 'MGEF' and r.get('VMAD') is not None and
                    vmad_scripts(r.get('VMAD').data, custom)[0]} - fallback_mgefs

    # Vampiric family: 1.09's Absorb Health
    absorb = fid(DRAIN_TO_ABSORB)
    reverted = set()
    for r in main.records('ENCH'):
        if not main.is_own(r.formid):
            continue
        changed = False
        for s in r.subrecords:
            if s.sig == 'EFID' and struct.unpack('<I', s.data)[0] in fallback_mgefs and \
                    'DrainOnHit' in m.own[struct.unpack('<I', s.data)[0]].edid:
                s.data = struct.pack('<I', absorb)
                changed = True
        if changed:
            r.mark_dirty()
            reverted.add(r.formid)
            report.append(f'absorb: {r.edid}')
    # auto-stimpak: restore about 6% of health per second at or below the threshold
    for omod, (threshold, text) in STIM.items():
        o = main.by_edid(omod)
        ench = next(r for r in main.records('ENCH') if main.is_own(r.formid) and struct.pack('<I', r.formid) in o.get('DATA').data)
        subs = [s for s in ench.subrecords if s.sig not in ('EFID', 'EFIT', 'CTDA', 'CIS1', 'CIS2')]
        for i, (level, amount) in enumerate(HEAL_TIERS):
            subs += [Subrecord('EFID', struct.pack('<I', REGENERATE_HEALTH)),
                     Subrecord('EFIT', struct.pack('<fII', float(amount), 0, 0)),
                     Subrecord('CTDA', ctda(OP_LE, threshold, FN_GET_HEALTH_PERCENTAGE, 0)),
                     Subrecord('CTDA', ctda(OP_GE, level, FN_GET_LEVEL, 0))]
            if i + 1 < len(HEAL_TIERS):
                subs.append(Subrecord('CTDA', ctda(OP_LT, HEAL_TIERS[i + 1][0], FN_GET_LEVEL, 0)))
        ench.subrecords[:] = subs
        ench.mark_dirty()
        o.set('DESC', zstr(text))
        report.append(f'regenerate: {omod} via {ench.edid}')
        platforms[omod] = ('PlayStation: changed', 'regenerates health while low instead of using a stimpak')
    # Disintegratin' (Green): back to vanilla plasma goo
    for edid in (DISINTEGRATIN_GREEN, 'A1ALMMGEF_Target_Effect_Hostile_Disintegration_Green'):
        r = main.by_edid(edid)
        for s in r.subrecords:
            for old, new in GREEN_SWAPS.items():
                s.data = s.data.replace(struct.pack('<I', fid(old)), struct.pack('<I', new))
        r.mark_dirty()

    # Midas': its gold dust is Disintegratin' (Gold)'s CLM art; vanilla ash instead (its caps need no art)
    r = main.by_edid(MIDAS)
    for s in r.subrecords:
        for old, new in ((fid('A1ALMSPEL_CritLaserGold'), CRIT_LASER),
                         (fid('A1ALMEnch_FaF_Contact_Custom_Effect_Disintegration_Gold'),
                          fid('A1ALMEnch_FaF_Contact_Custom_Effect_Disintegration_Red'))):
            s.data = s.data.replace(struct.pack('<I', old), struct.pack('<I', new))
    append_desc(r, NOTE_MIDAS)
    r.mark_dirty()
    report.append(f'midas note: {r.get("FULL").zstring}')
    platforms[MIDAS] = ('PlayStation: changed', "ordinary ash instead of gold dust (the gold is CLM's own art)")

    graph = reference_graph(m)
    face = fid(FACE_BUSTIN)
    for r in main.records('OMOD'):
        if not main.is_own(r.formid) or not r.get('FULL') or r.edid in LEFT_OUT or r.edid in STIM:
            continue
        if reaches(graph, r.formid, script_mgefs, set()):
            # all of its enchantments' effects scripted -> nothing works; otherwise only part of it
            effects = [struct.unpack('<I', s.data)[0] for f in graph[r.formid] if m.own[f].sig == 'ENCH'
                       for s in m.own[f].subrecords if s.sig == 'EFID']
            effects = [x for x in effects if x in m.own]
            whole = effects and all(x in script_mgefs or reaches(graph, x, script_mgefs, set()) for x in effects)
            append_desc(r, NOTE_SCRIPT if whole else NOTE_PART)
            report.append(f'{"script" if whole else "part-script"} note: {r.get("FULL").zstring}')
            if whole:
                platforms[r.edid] = ('PC and Xbox only', 'needs a script: does nothing on PlayStation')
            else:
                parts = sorted({(m.own[x].get('FULL').zstring if m.own[x].get('FULL') else m.own[x].edid)
                                for x in effects if x in script_mgefs or reaches(graph, x, script_mgefs, set())})
                platforms[r.edid] = ('PlayStation: partly', 'does nothing there: ' + '; '.join(parts))
        elif face in graph[r.formid]:
            append_desc(r, NOTE_FACE)
            report.append(f'face note: {r.get("FULL").zstring}')
            platforms[r.edid] = ('PlayStation: changed', 'targets are not blown apart')
        elif reaches(graph, r.formid, explode_on_kill, set()):
            append_desc(r, NOTE_KILL_ONLY)
            report.append(f'kill-only note: {r.get("FULL").zstring}')
            platforms[r.edid] = ('PlayStation: changed', 'explodes only on killing hits (the every-hit version needs a script)')
        elif graph[r.formid] & reverted:
            append_desc(r, NOTE_DRAIN)
            report.append(f'drain note: {r.get("FULL").zstring}')
            platforms[r.edid] = ('PlayStation: changed', 'heals on every hit except killing blows')

    # left out: recipes and loot drops
    gone = {fid(e) for e in LEFT_OUT}
    loose = {struct.unpack('<I', main.by_edid(e).get('LNAM').data)[0] for e in LEFT_OUT if main.by_edid(e).get('LNAM')}
    for c in [r for r in main.records('COBJ') if main.is_own(r.formid)]:
        cn = c.get('CNAM')
        if cn and struct.unpack('<I', cn.data)[0] in gone:
            m.remove(c)
            report.append(f'removed recipe {c.edid}')
    for l in main.records('LVLI'):
        if not main.is_own(l.formid):
            continue
        entries = [s for s in l.subrecords if s.sig == 'LVLO' and struct.unpack_from('<I', s.data, 4)[0] in loose]
        if entries:
            l.subrecords[:] = [s for s in l.subrecords if s not in entries]
            cnt = next(s for s in l.subrecords if s.sig == 'LLCT')
            cnt.data = bytes([cnt.data[0] - len(entries)])
            l.mark_dirty()
            report.append(f'loot: {len(entries)} out of {l.edid}')

    # holotapes: never given or craftable
    g = main.by_edid('A1ALMHOLOTAPES')
    g.set('FLTV', struct.pack('<f', 0.0))

    # loot mode: a Loot Manual magazine, and the Loot mode setting's text
    for name, p in plugins.items():
        e = m if p is main else Edit(p, main)
        pre = 'A1ALM'
        perk = p.by_edid(f'{pre}PERK_Loot')
        book = magazine.copy()
        label = 'CLM Loot Manual'
        book.subrecords[:] = [Subrecord('EDID', zstr(f'{pre}BOOK_LootManual'))] + [
            Subrecord(s.sig, {'FULL': zstr(label), 'DESC': b'\0', 'CNAM': b'\0',
                              'DNAM': s.data[:1] + struct.pack('<I', perk.formid) + s.data[5:]}.get(s.sig, s.data))
            for s in book.subrecords if s.sig != 'EDID']    # keeps the magazine keywords and vanilla script
        book.mark_dirty()
        e.add(book)
        tmpl = main.by_edid('co_A1ALMSET_DropLow').copy()
        tmpl.subrecords[:] = [Subrecord('EDID', zstr(f'co_{pre}BOOK_LootManual')),
                              Subrecord('DESC', zstr('Loot mode on PlayStation: read this once to start getting CLM loot '
                                                     'drops. If nothing drops, drop the manual and pick it up again.')),
                              *[Subrecord('CTDA', d) for d in on_conds(e.see(ITEMS['loot'][0]), e.see(setting_global('loot')))],
                              Subrecord('CTDA', ctda(OP_EQ, 0.0, FN_HAS_PERK, perk.formid)),
                              Subrecord('CTDA', ctda(OP_EQ, 0.0, 47, book.formid)),
                              Subrecord('CNAM', struct.pack('<I', book.formid)),
                              tmpl.get('BNAM'),
                              Subrecord('FNAM', struct.pack('<I', e.see(CATEGORY[0]))),
                              Subrecord('INTV', struct.pack('<HH', 1, 0))]
        tmpl.mark_dirty()
        e.add(tmpl)
        report.append(f'{name}: {book.edid}')
        detached = detach_scripts(e, custom)
        report.append(f'{name}: scripts detached from {len(detached)} records')
    # CLM perks: the perk holotape is a script, so each perk becomes a magazine made at the chemistry station (category
    # "CLM Perks"); reading it adds the perk, as vanilla perk magazines do. Without scripts a perk cannot be removed.
    cat = main.by_edid(CATEGORY[0]).copy()
    cat.subrecords[:] = [Subrecord('EDID', zstr('A1ALMKW_RecipeFilter_Perks'))] + [
        Subrecord(s.sig, zstr('CLM Perks') if s.sig == 'FULL' else s.data) for s in cat.subrecords if s.sig != 'EDID']
    cat.mark_dirty()
    m.add(cat)
    for page, edid, name in perks:
        perk = main.by_edid(edid)
        book_id = f'A1ALMBOOK_Perk_{edid.removeprefix("A1ALMPERK_")}'
        book = magazine.copy()
        book.subrecords[:] = [Subrecord('EDID', zstr(book_id))] + [
            Subrecord(s.sig, {'FULL': zstr(f'CLM Perk: {name}'), 'DESC': b'\0', 'CNAM': b'\0',
                              'DNAM': s.data[:1] + struct.pack('<I', perk.formid) + s.data[5:]}.get(s.sig, s.data))
            for s in book.subrecords if s.sig != 'EDID']
        book.mark_dirty()
        m.add(book)
        tmpl = main.by_edid('co_A1ALMSET_DropLow').copy()
        tmpl.subrecords[:] = [Subrecord('EDID', zstr(f'co_{book_id}')),
                              Subrecord('DESC', zstr(f'{page}: read this to gain the perk {name}. On PlayStation a perk '
                                                     'cannot be removed again (the perk holotape needs scripts).')),
                              Subrecord('CTDA', ctda(OP_EQ, 0.0, FN_HAS_PERK, perk.formid)),
                              Subrecord('CTDA', ctda(OP_EQ, 0.0, 47, book.formid)),
                              Subrecord('CNAM', struct.pack('<I', book.formid)),
                              tmpl.get('BNAM'),
                              Subrecord('FNAM', struct.pack('<I', cat.formid)),
                              Subrecord('INTV', struct.pack('<HH', 1, 0))]
        tmpl.mark_dirty()
        m.add(tmpl)
    report.append(f'perks: {len(perks)} perk magazines (category CLM Perks)')

    for r in (main.by_edid('co_A1ALMSET_ModeLoot'), main.by_edid('co_A1ALMSET_ModeLoot_Switch')):
        r.set('DESC', zstr('Legendaries drop from the enemies you kill instead of being crafted. A dropped CLM holotape '
                           'unlocks its whole family; OP legendaries also need a Legendary Core. Replaces Free crafting. '
                           'On PlayStation, also make the CLM Loot Manual (CLM Settings) once to start getting drops.'))
    # the 2.1 concise view: saves from before 2.1 get "Show all" from a script elsewhere, not on PlayStation
    r = main.by_edid('co_A1ALMSET_ShowAll')
    r.set('DESC', zstr('Show every legendary, as before 2.1. Without it, the concise view: one legendary per group of '
                       'similar effects; to show just one group, make its "CLM Group" item (category CLM Groups). '
                       'PlayStation: a save from before 2.1 needs this to keep every legendary shown.'))

    for name, p in plugins.items():
        p.save(OUT / name)
    (OUT / 'build_report.txt').write_text('\n'.join(report) + '\n', encoding='utf8')
    for e in LEFT_OUT:
        platforms[e] = ('PC and Xbox only', 'left out on PlayStation: needs ' + (
            "Kellogg's custom face files" if 'Kellog' in e else "CLM's own art (PlayStation mods cannot have assets)"))
    platforms[DISINTEGRATIN_GREEN] = ('PlayStation: changed', "vanilla plasma goo instead of CLM's green ash")
    with open(OUT / 'platforms.csv', 'w', encoding='utf8', newline='') as f:   # for the private tracking sheet
        w = csv.writer(f)
        w.writerow(['editor_id', 'status', 'playstation'])
        w.writerows([e, *v] for e, v in sorted(platforms.items()))
    print(f'PlayStation plugins in {OUT} ({len(report)} changes, see build_report.txt; platforms.csv)')


TEST_BACKUP = REPO / 'work' / 'pc_plugins_during_ps_test'


def test_swap(game: Path, install: bool) -> None:
    """PC test of the PlayStation build: swap the plugins in the game's Data folder (scripts and assets that are
    still there loose are not used: the PS plugins attach no CLM script and reach no CLM asset)."""
    data = game / 'Data'
    names = [MAIN]
    if install:
        if TEST_BACKUP.exists() and any(TEST_BACKUP.iterdir()):
            raise SystemExit(f'{TEST_BACKUP} is not empty: restore first')
        TEST_BACKUP.mkdir(parents=True, exist_ok=True)
        for n in names:
            shutil.copy(data / n, TEST_BACKUP / n)
            shutil.copy(OUT / n, data / n)
        print('PlayStation plugins installed for testing; PC plugins saved in', TEST_BACKUP)
    else:
        for n in names:
            shutil.copy(TEST_BACKUP / n, data / n)
            (TEST_BACKUP / n).unlink()
        print('PC plugins restored')


def main_():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', default='D:/Steam/steamapps/common/Fallout 4')
    ap.add_argument('--test-install', action='store_true')
    ap.add_argument('--test-restore', action='store_true')
    a = ap.parse_args()
    if a.test_install or a.test_restore:
        test_swap(Path(a.game), a.test_install)
    else:
        build(Path(a.game))


if __name__ == '__main__':
    main_()
