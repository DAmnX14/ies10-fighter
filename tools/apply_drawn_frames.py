"""
Aplica cuadros DIBUJADOS (no deformados por el rig) sobre las tiras generadas.

Cada personaje puede tener assets/characters/<p>/dibujados/dibujados.json con poses
dibujadas (p. ej. generadas con SpriteCook a partir de su ilustración). Para cada pose:
  - "alto" (o "ancho" si "acostado"): tamaño final en px nativos (el personaje de pie mide
    lo mismo que en sus otras animaciones, sin deformar: misma escala en X e Y),
  - "reemplaza": {animación: [cuadros]} que pasan a usar ese dibujo,
  - "aire" (opcional): pose en el aire, se ubica a la altura del cuadro que reemplaza,
  - "respirar" (opcional): el torso sube y baja 1-2 px en el reposo (los pies quedan fijos),
  - "golpea" (opcional): articulación que golpea; se recoloca en el punto más adelantado
    del dibujo para que la hitbox coincida con el puño o el pie.
El dibujo se escala, se apoya con los pies en el suelo (ancla 112,170) alineado con los pies
del cuadro que reemplaza, y se actualizan el recorte (bbox) y las articulaciones del meta.
Se corre solo al final de build_sprites.py; también:  python tools/apply_drawn_frames.py [personaje]
"""
import os, sys, json
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FW, FH, AX, AY = 240, 176, 112, 170
BREATH = [0, 0, 1, 1, 2, 1, 1, 0]          # px que baja el torso en cada cuadro del reposo


def _fit(img, cfg):
    a = np.asarray(img.convert('RGBA'))
    ys, xs = np.where(a[..., 3] > 20)
    img = img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    if cfg.get('acostado'):
        k = cfg['ancho'] / img.width
    else:
        k = cfg['alto'] / img.height
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    # reducción con alfa premultiplicado (sin halos) y alfa binario (pixel art nítido)
    arr = np.asarray(img.convert('RGBA')).astype(np.float32)
    arr[..., :3] *= arr[..., 3:4] / 255
    small = np.asarray(Image.fromarray(arr.astype(np.uint8), 'RGBA').resize((w, h), Image.LANCZOS)).astype(np.float32)
    al = small[..., 3:4]
    rgb = np.where(al > 1, small[..., :3] * 255 / np.maximum(al, 1), 0)
    out = np.zeros((h, w, 4), np.uint8)
    m = al[..., 0] > 110
    out[m, :3] = np.clip(rgb[m], 0, 255).astype(np.uint8)
    out[m, 3] = 255
    return out


def _feet_x(a, low_rows=6):
    ys, xs = np.where(a[..., 3] > 0)
    if not len(ys):
        return 0
    sel = ys >= ys.max() - low_rows
    return float(xs[sel].mean())


def apply(name):
    d = os.path.join(ROOT, 'assets', 'characters', name)
    cfgp = os.path.join(d, 'dibujados', 'dibujados.json')
    if not os.path.exists(cfgp):
        return 0
    cfg = json.load(open(cfgp, encoding='utf-8'))
    metap = os.path.join(d, f'{name}_meta.json')
    meta = json.load(open(metap, encoding='utf-8'))
    n = 0
    for pose, pc in cfg['poses'].items():
        src = os.path.join(d, 'dibujados', pose + '.png')
        if not os.path.exists(src):
            print('  falta', src)
            continue
        drawn = _fit(Image.open(src), pc)
        dh, dw = drawn.shape[:2]
        for anim, frames in pc['reemplaza'].items():
            info = meta['animations'][anim]
            strip = np.array(Image.open(os.path.join(d, info['file'])).convert('RGBA'))
            for fi in frames:
                if fi >= info['frames']:
                    continue
                cell = strip[:, fi * FW:(fi + 1) * FW]
                # mismo apoyo horizontal que el cuadro reemplazado
                fx_old = _feet_x(cell) if cell[..., 3].any() else AX
                if pc.get('acostado'):
                    x0b, _, x1b, _ = info['bbox'][fi]
                    left = int(round((x0b + x1b) / 2 - dw / 2))
                else:
                    left = int(round(fx_old - _feet_x(drawn)))
                left = max(0, min(FW - dw, left))
                if pc.get('aire'):
                    # pose en el aire (salto): misma altura que el cuadro que reemplaza
                    top = info['bbox'][fi][3] - dh
                else:
                    top = AY + 1 - dh                            # pies sobre el suelo
                top = max(0, top)
                new = np.zeros((FH, FW, 4), np.uint8)
                hh = min(dh, FH - top)
                new[top:top + hh, left:left + dw] = drawn[:hh]
                if pc.get('respirar'):
                    # respiración: sólo la parte de arriba del cuerpo baja 1-2 px (los pies no se mueven)
                    dy = BREATH[fi % len(BREATH)]
                    if dy:
                        cut = top + int(dh * 0.55)
                        upper = new[top:cut].copy()
                        new[top:cut] = 0
                        sl = new[top + dy:cut + dy]
                        m = upper[:len(sl), ..., 3] > 0
                        sl[m] = upper[:len(sl)][m]
                strip[:, fi * FW:(fi + 1) * FW] = new
                ys, xs = np.where(new[..., 3] > 0)
                info['bbox'][fi] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
                j = info['joints'][fi]
                if pc.get('golpea'):
                    # el punto más adelantado del dibujo (puño / pie) pasa a ser la articulación que golpea
                    xr = xs.max()
                    yr = float(ys[xs >= xr - 2].mean())
                    jn = pc['golpea']
                    j[jn] = [float(xr - 3), round(yr, 1)]
                    if jn == 'f_an':
                        j['f_toe'] = [float(xr), round(yr, 1)]
                n += 1
            Image.fromarray(strip, 'RGBA').save(os.path.join(d, info['file']))
    json.dump(meta, open(metap, 'w', encoding='utf-8'))
    print(f'  {name}: {n} cuadros dibujados aplicados')
    return n


if __name__ == '__main__':
    chars = sys.argv[1:] or sorted(os.listdir(os.path.join(ROOT, 'assets', 'characters')))
    for c in chars:
        apply(c)
