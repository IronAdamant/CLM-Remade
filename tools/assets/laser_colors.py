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


def patched_model(src: bytes, swaps: dict[str, str], beam_scale_value: float | None = None) -> bytes:
    n = Nif(src)
    for old, new in swaps.items():
        n.replace_sized_string(old, new)
    if beam_scale_value is not None:
        for i, t, s, e in n.block_ranges():
            if t == 'BSEffectShaderProperty':
                d = parse_effect_shader(bytes(n.data[s:e]))
                if d['color_scale'] == RED_BEAM_SCALE:
                    struct.pack_into('<f', n.data, s + d['color_offset'] + 16, beam_scale_value)
    out = bytes(n.data)
    chk = Nif(out)
    assert chk.blocks_offset + sum(chk.sizes) + 8 == len(out), 'block table mismatch'
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    ap.add_argument('--out', required=True, help="mod's data folder")
    a = ap.parse_args()
    data, out = Path(a.game) / 'Data', Path(a.out)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        extract_general(data / 'Fallout4 - Meshes.ba2',
                        ['meshes' + BS + 'effects' + BS + n for n in ('laserriflebeamred.nif', 'muzlaserrifle01.nif',
                                                                    'impactlaserltbluesmall.nif', 'impactlaserbluevsshell.nif')], tmp)
        for ba2 in sorted(data.glob('Fallout4 - Textures*.ba2')):
            extract_textures(ba2, [grad_path(n) for n in ('WepLaserRed01Grad.dds', 'WepLaserRedRingGrad.dds',
                                                          'LaserImpactWaveGrad.dds')], tmp)
        beam = (tmp / 'Meshes' / 'Effects' / 'LaserRifleBeamRed.nif').read_bytes()
        muzzle = (tmp / 'Meshes' / 'Effects' / 'MuzLaserRifle01.nif').read_bytes()
        main_grad = read_dds_bgra(tmp / 'Textures' / 'Effects' / 'Gradients' / 'WepLaserRed01Grad.dds')
        ring_grad = read_dds_bgra(tmp / 'Textures' / 'Effects' / 'Gradients' / 'WepLaserRedRingGrad.dds')
        wave_grad = read_dds_bgra(tmp / 'Textures' / 'Effects' / 'Gradients' / 'LaserImpactWaveGrad.dds')
        impact_small = (tmp / 'Meshes' / 'Effects' / 'ImpactLaserLtBlueSmall.nif').read_bytes()
        impact_shell = (tmp / 'Meshes' / 'Effects' / 'ImpactLaserBlueVsShell.nif').read_bytes()

    for name, deg in COLORS.items():
        gdir = out / 'Textures' / 'Effects' / 'Gradients' / 'CLM'
        write_dds_bgra(gdir / f'WepLaser{name}01Grad.dds', rotate_hue(main_grad, deg))
        write_dds_bgra(gdir / f'WepLaser{name}RingGrad.dds', rotate_hue(ring_grad, deg))
        write_dds_bgra(gdir / f'LaserImpactWave{name}Grad.dds', rotate_hue(wave_grad, deg))
        swaps = {grad_path('WepLaserRed01Grad.dds'): grad_path(f'WepLaser{name}01Grad.dds', clm=True),
                 grad_path('WepLaserRedRingGrad.dds'): grad_path(f'WepLaser{name}RingGrad.dds', clm=True)}
        mdir = out / 'Meshes' / 'Effects' / 'CLM'
        mdir.mkdir(parents=True, exist_ok=True)
        (mdir / f'LaserRifleBeam{name}.nif').write_bytes(patched_model(beam, swaps, beam_scale(deg)))
        (mdir / f'MuzLaserRifle{name}.nif').write_bytes(patched_model(muzzle, swaps))
        blue = {}
        for prefix in ('textures', 'Textures'):
            gp = lambda n, p=prefix: BS.join([p, 'Effects', 'Gradients', n])
            blue[gp('WepLaserLtBlue01Grad.dds')] = grad_path(f'WepLaser{name}01Grad.dds', clm=True)
            blue[gp('WepLaserLtBlueRingGrad.dds')] = grad_path(f'WepLaser{name}RingGrad.dds', clm=True)
            blue[gp('LaserImpactWaveLtBlueGrad.dds')] = grad_path(f'LaserImpactWave{name}Grad.dds', clm=True)
        (mdir / f'ImpactLaser{name}Small.nif').write_bytes(patched_model(impact_small, blue))
        (mdir / f'ImpactLaser{name}VsShell.nif').write_bytes(patched_model(impact_shell, blue))
        print(f'{name:9} hue +{deg:3}  beam brightness {beam_scale(deg):5}  light RGB {rotate_rgb(VANILLA_RED_LIGHT, deg)}'
              f'  decal RGB {rotate_rgb(VANILLA_RED_DECAL, deg)}')


if __name__ == '__main__':
    main()
