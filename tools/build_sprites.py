"""
Genera todos los spritesheets de los personajes a partir de los sprites fuente.
Uso:  python tools/build_sprites.py   (desde la carpeta del proyecto)
Salida: assets/characters/<personaje>/<personaje>_<anim>.png + <personaje>_meta.json
"""
import os, sys, json, math
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from rig import RigCharacter, CANVAS_W, CANVAS_H, ANCHOR_X, ANCHOR_Y, SS
from anim_defs import ANIM_ORDER, get_anim, has_anim

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CHARS = ['pantoja', 'parada', 'nehuen', 'luciano', 'nico', 'angel', 'facu', 'pedro', 'emi', 'denis']
JOINTS = ['f_ha', 'b_ha', 'f_an', 'b_an', 'f_toe', 'b_toe', 'head', 'neck', 'pelvis',
          'f_el', 'b_el', 'f_kn', 'b_kn']


def frames_for(char, name):
    a = get_anim(char, name)
    if 'func' in a:
        n, fn = a['func']
        return [fn(i / n) for i in range(n)], a
    return [k for k, n in a['keys']], a


def render_grounded(rc, kf):
    """Renderiza un cuadro sin que el cuerpo se hunda debajo del piso.
    Antes, al caer o levantarse, el cuerpo quedaba ~5 px (15 px en pantalla)
    por debajo del suelo y se cortaba con el borde del cuadro."""
    kf = dict(kf)
    u_px = (rc.H / SS) / 100.0              # px nativos por unidad de pose
    limit = ANCHOR_Y + 2
    for _ in range(12):
        p = rc.resolve(kf)
        img, P = rc.render(p)
        ys = np.where(img[..., 3].any(1))[0]
        if not len(ys) or ys.max() <= limit:
            break
        exc = (ys.max() - (ANCHOR_Y + 1)) / u_px
        if ys.max() >= CANVAS_H - 1:
            exc = max(exc, 4.0)                    # cortado: no se ve cuánto sobra
        if kf.get('lrel', 0) >= 0.5 or kf.get('rot', 0):
            kf['ry'] = kf.get('ry', 0) - exc       # todo el cuerpo sube
        else:
            for s_ in 'bf':                        # pies apoyados: sube el pie que se hunde
                if s_ + 'f_abs' in kf:
                    x, y = kf[s_ + 'f_abs']; kf[s_ + 'f_abs'] = (x, y - exc)
                else:
                    x, y = kf.get(s_ + 'f', (0, 0)); kf[s_ + 'f'] = (x, min(y, 0) - exc * 0.5)
    return p, img, P


def portrait(rc, src_dir, name):
    """Retrato cuadrado encuadrado sobre la cabeza real (pelo + cara + mentón), así
    todas las caras quedan centradas y del mismo tamaño en los recuadros."""
    from rig import segment, SKELETONS
    sk = SKELETONS[name]
    img, fg = segment(f'{src_dir}/{sk["src"]}', name)
    hx, hy = sk['head']; nx, ny = sk['neck']
    hl = math.hypot(nx - hx, ny - hy)
    yy, xx = np.mgrid[0:fg.shape[0], 0:fg.shape[1]]
    ecx, ecy = (hx + nx) / 2, (hy + ny) / 2 - 0.12 * hl
    ell = (((xx - ecx) / (0.62 * hl)) ** 2 + ((yy - ecy) / (0.85 * hl)) ** 2 <= 1) & fg & (yy < ny + 0.05 * hl)
    ys, xs = np.where(ell)
    if len(xs) > 50:
        x0b, x1b, y0b, y1b = np.percentile(xs, 1), np.percentile(xs, 99), ys.min(), np.percentile(ys, 99)
        size = int(max(x1b - x0b, y1b - y0b) * 1.22)
        cx, cy = int((x0b + x1b) / 2), int((y0b + y1b) / 2 + size * 0.04)
    else:
        size = int((ny - hy) * 1.55)
        cx, cy = int((hx + nx) / 2), int((hy + ny) / 2 + size * 0.06)
    x0, y0 = cx - size // 2, cy - size // 2
    pad = size
    imgp = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    fgp = cv2.copyMakeBorder(fg.astype(np.uint8), pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    crop = imgp[y0 + pad:y0 + pad + size, x0 + pad:x0 + pad + size]
    m = fgp[y0 + pad:y0 + pad + size, x0 + pad:x0 + pad + size]
    rgba = np.dstack([crop, m * 255]).astype(np.uint8)
    small = cv2.resize(rgba, (72, 72), interpolation=cv2.INTER_AREA)
    small[..., 3] = np.where(small[..., 3] > 110, 255, 0)
    return small


def main():
    src = os.path.join(ROOT, 'assets', 'source')
    only = [a for a in sys.argv[1:] if a in CHARS]
    for name in (only or CHARS):
        print('==', name, flush=True)
        rc = RigCharacter(name, src)
        rc.build_palette()
        out_dir = os.path.join(ROOT, 'assets', 'characters', name)
        os.makedirs(out_dir, exist_ok=True)
        meta = dict(name=name, frame_w=CANVAS_W, frame_h=CANVAS_H, anchor=[ANCHOR_X, ANCHOR_Y],
                    height=round(rc.H / SS), animations={})
        sheet_rows = []
        for an in ANIM_ORDER:
            if not has_anim(name, an):
                continue
            kfs, spec = frames_for(name, an)
            frames, joints, boxes = [], [], []
            for kf in kfs:
                p, img, P = render_grounded(rc, kf)
                frames.append(img)
                jd = {j: [round(v, 1) for v in rc.to_native(P[j])] for j in JOINTS}
                if p.get('_swap'):
                    jd['b_ha'], jd['b_el'] = jd['f_ha'], jd['f_el']
                joints.append(jd)
                ys, xs = np.where(img[..., 3] > 0)
                boxes.append([int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
                             if len(xs) else [0, 0, 1, 1])
            strip = np.concatenate(frames, 1)
            Image.fromarray(strip, 'RGBA').save(os.path.join(out_dir, f'{name}_{an}.png'))
            meta['animations'][an] = dict(file=f'{name}_{an}.png', frames=len(frames),
                                          dur=spec.get('dur', 5), loop=spec.get('loop', False),
                                          joints=joints, bbox=boxes)
            sheet_rows.append(strip)
            print(f'  {an}: {len(frames)} cuadros', flush=True)
        with open(os.path.join(out_dir, f'{name}_meta.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f)
        # retrato
        por = portrait(rc, src, name)
        Image.fromarray(por, 'RGBA').save(os.path.join(out_dir, f'{name}_retrato.png'))
        # hoja completa (vista previa / documentación)
        W = max(r.shape[1] for r in sheet_rows)
        full = np.zeros((CANVAS_H * len(sheet_rows), W, 4), np.uint8)
        for i, r in enumerate(sheet_rows):
            full[i * CANVAS_H:(i + 1) * CANVAS_H, :r.shape[1]] = r
        Image.fromarray(full, 'RGBA').save(os.path.join(out_dir, f'{name}_spritesheet_completo.png'))


if __name__ == '__main__':
    main()
