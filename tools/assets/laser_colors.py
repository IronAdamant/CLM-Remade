"""Generate CLM's coloured laser assets from the vanilla red laser.

Laser colour in Fallout 4 comes from small gradient textures (colour lookup tables) used by the effect
shaders, not from the models. For each colour this script:
  - rotates the hue of the vanilla red gradients (main, ring, impact wave), keeping their brightness,
    white-hot core and fade;
  - copies the vanilla red beam and muzzle-flash models with the gradient paths pointed at the new textures,
    and rescales the beam shader's brightness for the colour's luminance (red is dark, so vanilla boosts it 20x);
  - copies the vanilla light-blue impact models (white-based, unlike the red ones whose shaders carry a red
    tint) with their gradients pointed at the new textures.

Usage (needs AgentCreationKit on PYTHONPATH and the game installed):
    python tools/assets/laser_colors.py --game "D:/Steam/steamapps/common/Fallout 4" --out data
Prints the light colour to use for each colour's LIGH record.
"""
from __future__ import annotations

import argparse
import re
import colorsys
import struct
import tempfile
from pathlib import Path

import numpy as np

from ack.archive import extract_general, extract_textures
from ack.nif import Nif, parse_effect_shader

BS = chr(92)
# name: hue rotation in degrees from vanilla red
COLORS = {'Green': 120, 'Purple': 275, 'Gold': 48, 'Orange': 24, 'Pink': 320, 'DeepBlue': 225}
VANILLA_RED_LIGHT = (255, 17, 17)   # WeapLightLaserBeam
VANILLA_RED_DECAL = (236, 70, 70)   # LaserRedSmallImpact decal colour
RED_BEAM_SCALE = 20.0               # LaserRifleBeamRed.nif main shader brightness


def grad_path(name: str, clm: bool = False) -> str:
    parts = ['textures', 'Effects', 'Gradients'] + (['CLM'] if clm else []) + [name]
    return BS.join(parts)


def read_dds_bgra(path: Path) -> np.ndarray:
    d = path.read_bytes()
    h, w = struct.unpack_from('<II', d, 12)
    return np.frombuffer(d[148:148 + w * h * 4], np.uint8).reshape(h, w, 4)


def write_dds_bgra(path: Path, arr: np.ndarray) -> None:
    h, w = arr.shape[:2]
    hdr = struct.pack('<4sIIIIIII11I', b'DDS ', 124, 0x1 | 0x2 | 0x4 | 0x8 | 0x1000, h, w, w * 4, 0, 1, *([0] * 11))
    hdr += struct.pack('<II4sIIIII', 32, 0x4, b'DX10', 0, 0, 0, 0, 0) + struct.pack('<IIIII', 0x1000, 0, 0, 0, 0)
    hdr += struct.pack('<IIIII', 87, 3, 0, 1, 0)  # DXGI B8G8R8A8_UNORM, 2D
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(hdr + np.ascontiguousarray(arr).tobytes())


def rotate_hue(bgra: np.ndarray, degrees: float) -> np.ndarray:
    out = bgra.copy()
    f = bgra.astype(float) / 255
    for y in range(bgra.shape[0]):
        for x in range(bgra.shape[1]):
            b, g, r, _ = f[y, x]
            hh, s, v = colorsys.rgb_to_hsv(r, g, b)
            nr, ng, nb = colorsys.hsv_to_rgb((hh + degrees / 360) % 1, s, v)
            out[y, x, :3] = [round(nb * 255), round(ng * 255), round(nr * 255)]
    return out


def luminance(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def beam_scale(degrees: float) -> float:
    r, g, b = colorsys.hsv_to_rgb(degrees / 360, 1, 1)
    return max(2.0, round(RED_BEAM_SCALE * luminance(1, 0, 0) / luminance(r, g, b), 2))


def rotate_rgb(rgb: tuple[int, int, int], degrees: float) -> tuple[int, int, int]:
    r, g, b = (c / 255 for c in rgb)
    hh, s, v = colorsys.rgb_to_hsv(r, g, b)
    return tuple(round(c * 255) for c in colorsys.hsv_to_rgb((hh + degrees / 360) % 1, s, v))


def patched_model(src: bytes, swaps: dict[str, str], beam_scale_value: float | None = None,
                  tint: tuple[float, float, float] | None = None, addons: dict[int, int] | None = None) -> bytes:
    """Copy a vanilla effect model: swap gradient paths, fix base colours, optionally rescale the beam and
    repoint add-on nodes.

    The effect shader multiplies the gradient colour by its base colour, so a tinted base colour leaks into every
    recolour (the vanilla muzzle flash's glow has a red-orange base, which turned purple into red in game).
    Tinted base colours are set to `tint` if given (spark add-ons colour themselves this way), otherwise white.
    `addons` remaps BSValueNode add-on indexes (shared particle effects the model attaches at runtime).
    """
    n = Nif(src)
    for old, new in swaps.items():
        n.replace_sized_string(old, new)
    for i, t, s, e in n.block_ranges():
        if t == 'BSValueNode' and addons:
            value_at = e - 5  # BSValueNode ends with: int value, byte flags
            value, = struct.unpack_from('<i', n.data, value_at)
            if value in addons:
                struct.pack_into('<i', n.data, value_at, addons[value])
        if t != 'BSEffectShaderProperty':
            continue
        d = parse_effect_shader(bytes(n.data[s:e]))
        r, g, b, a = d['base_color']
        if max(r, g, b) - min(r, g, b) > 0.05:  # tinted, not grey/white
            struct.pack_into('<3f', n.data, s + d['color_offset'], *(tint or (1.0, 1.0, 1.0)))
        if beam_scale_value is not None and d['color_scale'] == RED_BEAM_SCALE:
            struct.pack_into('<f', n.data, s + d['color_offset'] + 16, beam_scale_value)
    out = bytes(n.data)
    chk = Nif(out)
    assert chk.blocks_offset + sum(chk.sizes) + 8 == len(out), 'block table mismatch'
    # Guard: a recoloured model must not keep any vanilla red / light-blue colour lookup.
    leftover = sorted({p for _, _, p in chk.sized_strings()
                       if 'gradients' in p.lower() and BS + 'CLM' + BS not in p and re.search(r'red|ltblue', p, re.I)})
    if leftover:
        raise RuntimeError(f'vanilla colour gradients left in model: {leftover}')
    return out


# Add-on nodes: shared particle effects (sparks, smoke, impact wave) that models attach by a global index,
# defined by ADDN records. The vanilla laser models point at red (or light-blue) add-ons, so each colour gets its
# own. Indexes are global across the game and all mods. Official content stays below 1000 in per-DLC blocks
# (base 0-283, Automatron 400s, Far Harbor 550s, Nuka-World 600s, Contraptions 800s, Vault-Tec 900s, Creation Club
# 353-399). An earlier build used 5565000+ and the game crashed, so CLM uses the small free block 1500-1599.
ADDON_BASE = 1500
ADDON_KINDS = {  # kind: (vanilla light-blue ADDN index it replaces, source model, how it gets its colour)
    'MuzSparks': (64, 'MPSMuzSparksLaser02LtBlue.nif', 'tint'),
    'ImpactSparks': (66, 'MPSLaserImpactSparksLtBlue.nif', 'tint'),
    'ImpactSmoke': (65, 'MPSSmokeLaserImpactLtBlue.nif', 'gradient'),
    'ImpactWave': (62, 'MPSLaserWaveImpactLtBlue.nif', 'gradient'),
}
RED_MUZZLE_SPARKS_ADDON = 37  # MPSMuzSparksLaser02, referenced by the vanilla red muzzle flash
VANILLA_RED_SPARKS = (255, 64, 64)  # MPSLaserImpactSparks base colour (1.0, 0.25, 0.25)


def addon_index(colour_no: int, kind: str) -> int:
    return ADDON_BASE + colour_no * 10 + list(ADDON_KINDS).index(kind) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    ap.add_argument('--out', required=True, help="mod's data folder")
    a = ap.parse_args()
    data, out = Path(a.game) / 'Data', Path(a.out)

    def eff(n):
        return 'meshes' + BS + 'effects' + BS + n.lower()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        models = ['LaserRifleBeamRed.nif', 'MuzLaserRifle01.nif', 'ImpactLaserLtBlueSmall.nif',
                  'ImpactLaserBlueVsShell.nif'] + [src for _, src, _ in ADDON_KINDS.values()]
        extract_general(data / 'Fallout4 - Meshes.ba2', [eff(m) for m in models], tmp)
        grad_names = ('WepLaserRed01Grad', 'WepLaserRedRingGrad', 'LaserImpactWaveGrad', 'SmokeLaserMuzFlash01Grad')
        for ba2 in sorted(data.glob('Fallout4 - Textures*.ba2')):
            extract_textures(ba2, [grad_path(n + '.dds') for n in grad_names], tmp)
        mesh = {m: (tmp / 'Meshes' / 'Effects' / m).read_bytes() for m in models}
        grads = {n: read_dds_bgra(tmp / 'Textures' / 'Effects' / 'Gradients' / (n + '.dds')) for n in grad_names}

    gdir = out / 'Textures' / 'Effects' / 'Gradients' / 'CLM'
    mdir = out / 'Meshes' / 'Effects' / 'CLM'
    mdir.mkdir(parents=True, exist_ok=True)
    table = []
    for no, (name, deg) in enumerate(COLORS.items(), start=1):
        write_dds_bgra(gdir / f'WepLaser{name}01Grad.dds', rotate_hue(grads['WepLaserRed01Grad'], deg))
        write_dds_bgra(gdir / f'WepLaser{name}RingGrad.dds', rotate_hue(grads['WepLaserRedRingGrad'], deg))
        write_dds_bgra(gdir / f'LaserImpactWave{name}Grad.dds', rotate_hue(grads['LaserImpactWaveGrad'], deg))
        write_dds_bgra(gdir / f'SmokeLaserMuzFlash{name}Grad.dds', rotate_hue(grads['SmokeLaserMuzFlash01Grad'], deg))

        def clm(n):
            return grad_path(n, clm=True)

        red = {grad_path('WepLaserRed01Grad.dds'): clm(f'WepLaser{name}01Grad.dds'),
               grad_path('WepLaserRedRingGrad.dds'): clm(f'WepLaser{name}RingGrad.dds')}
        blue = {}
        for prefix in ('textures', 'Textures'):
            def gp(n, p=prefix):
                return BS.join([p, 'Effects', 'Gradients', n])
            blue[gp('WepLaserLtBlue01Grad.dds')] = clm(f'WepLaser{name}01Grad.dds')
            blue[gp('WepLaserLtBlueRingGrad.dds')] = clm(f'WepLaser{name}RingGrad.dds')
            blue[gp('LaserImpactWaveLtBlueGrad.dds')] = clm(f'LaserImpactWave{name}Grad.dds')
            blue[gp('SmokeLaserMuzFlashLtBlueGrad.dds')] = clm(f'SmokeLaserMuzFlash{name}Grad.dds')
        idx = {kind: addon_index(no, kind) for kind in ADDON_KINDS}
        blue_addons = {vanilla: idx[kind] for kind, (vanilla, _, _) in ADDON_KINDS.items()}
        sparks_tint = tuple(c / 255 for c in rotate_rgb(VANILLA_RED_SPARKS, deg))

        (mdir / f'LaserRifleBeam{name}.nif').write_bytes(
            patched_model(mesh['LaserRifleBeamRed.nif'], red, beam_scale(deg)))
        (mdir / f'MuzLaserRifle{name}.nif').write_bytes(
            patched_model(mesh['MuzLaserRifle01.nif'], red, addons={RED_MUZZLE_SPARKS_ADDON: idx['MuzSparks']}))
        (mdir / f'ImpactLaser{name}Small.nif').write_bytes(
            patched_model(mesh['ImpactLaserLtBlueSmall.nif'], blue, addons=blue_addons))
        (mdir / f'ImpactLaser{name}VsShell.nif').write_bytes(
            patched_model(mesh['ImpactLaserBlueVsShell.nif'], blue, addons=blue_addons))
        for kind, (vanilla, src, mode) in ADDON_KINDS.items():
            model = patched_model(mesh[src], blue, tint=sparks_tint if mode == 'tint' else None)
            (mdir / f'MPS{kind}{name}.nif').write_bytes(model)
            table.append(','.join([name, kind, str(idx[kind]), BS.join(['Effects', 'CLM', f'MPS{kind}{name}.nif']),
                                   str(vanilla)]))
        print(f'{name:9} hue +{deg:3}  beam brightness {beam_scale(deg):5}  light RGB {rotate_rgb(VANILLA_RED_LIGHT, deg)}'
              f'  decal RGB {rotate_rgb(VANILLA_RED_DECAL, deg)}  add-ons {min(idx.values())}-{max(idx.values())}')
    # Machine-readable add-on table for the xEdit script that creates the ADDN records.
    Path(__file__).with_name('laser_addons.csv').write_text(
        'colour,kind,index,model,replaces_vanilla\n' + '\n'.join(table) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
