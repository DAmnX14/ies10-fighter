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
from anim_defs import ANIM_ORDER, get_anim

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CHARS = ['pantoja', 'parada', 'nehuen', 'luciano']
JOINTS = ['f_ha', 'b_ha', 'f_an', 'b_an', 'f_toe', 'b_toe', 'head', 'neck', 'pelvis',
          'f_el', 'b_el', 'f_kn', 'b_kn']


def frames_for(char, name):
    a = get_anim(char, name)
    if 'func' in a:
        n, fn = a['func']
        return [fn(i / n) for i in range(n)], a
    return [k for k, n in a['keys']], a


def portrait(rc, src_dir, name):
    from rig import segment, SKELETONS
    sk = SKELETONS[name]
    img, fg = segment(f'{src_dir}/{sk["src"]}', name)
    hx, hy = sk['head']; nx, ny = sk['neck']
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
    for name in CHARS:
        print('==', name, flush=True)
        rc = RigCharacter(name, src)
        rc.build_palette()
        out_dir = os.path.join(ROOT, 'assets', 'characters', name)
        os.makedirs(out_dir, exist_ok=True)
        meta = dict(name=name, frame_w=CANVAS_W, frame_h=CANVAS_H, anchor=[ANCHOR_X, ANCHOR_Y],
                    height=round(rc.H / SS), animations={})
        sheet_rows = []
        for an in ANIM_ORDER:
            kfs, spec = frames_for(name, an)
            frames, joints, boxes = [], [], []
            for kf in kfs:
                p = rc.resolve(kf)
                img, P = rc.render(p)
                frames.append(img)
                joints.append({j: [round(v, 1) for v in rc.to_native(P[j])] for j in JOINTS})
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
