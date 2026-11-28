"""
Genera los spritesheets de efectos especiales (pixel-art procedural, original).
Salida: assets/effects/<efecto>.png (tira horizontal) + effects_meta.json
Tamaño nativo; el juego los escala x3 como a los personajes.
"""
import os, json, math
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'assets', 'effects')
rng = np.random.default_rng(4)
META = {}


def new(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def save(name, frames, dur=3, loop=False):
    w, h = frames[0].size
    strip = Image.new('RGBA', (w * len(frames), h))
    for i, f in enumerate(frames):
        strip.paste(f, (i * w, 0))
    strip.save(os.path.join(OUT, name + '.png'))
    META[name] = dict(file=name + '.png', w=w, h=h, frames=len(frames), dur=dur, loop=loop)


def outline(im, color=(20, 10, 30, 255)):
    a = np.asarray(im).copy()
    al = a[..., 3] > 0
    grow = np.zeros_like(al)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            grow |= np.roll(np.roll(al, dy, 0), dx, 1)
    edge = grow & ~al
    a[edge] = color
    return Image.fromarray(a, 'RGBA')


def star(d, cx, cy, r_in, r_out, n, rot, fill):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def spark(size, n, cols, name, rays=8, dur=2):
    frames = []
    for i in range(n):
        im, d = new(size, size)
        c = size / 2; t = i / (n - 1)
        R = size * 0.5 * (0.35 + 0.65 * t)
        if t < 0.85:
            star(d, c, c, R * 0.25, R, rays, i * 0.35, cols[0])
            star(d, c, c, R * 0.15, R * 0.65, rays, i * 0.35 + 0.2, cols[1])
            d.ellipse([c - R * 0.25 * (1 - t), c - R * 0.25 * (1 - t), c + R * 0.25 * (1 - t),
                       c + R * 0.25 * (1 - t)], fill=cols[2])
        for k in range(rays):
            a = k * 2 * math.pi / rays + 0.2
            r0, r1 = R * (0.8 + t * 0.4), R * (1.0 + t * 0.6)
            if t > 0.2:
                d.line([(c + r0 * math.cos(a), c + r0 * math.sin(a)),
                        (c + r1 * math.cos(a), c + r1 * math.sin(a))], fill=cols[1], width=1)
        frames.append(outline(im) if t < 0.85 else im)
    save(name, frames, dur)


def dust():
    frames = []
    pts = [(rng.uniform(-1, 1), rng.uniform(0.2, 1)) for _ in range(9)]
    for i in range(7):
        im, d = new(48, 24); t = i / 6
        for k, (dx, dy) in enumerate(pts):
            x = 24 + dx * 20 * (0.3 + t); y = 22 - dy * 12 * (0.4 + t)
            r = (5 - k % 3) * (1 - t * 0.7) + 1
            col = (200, 190, 170, int(230 * (1 - t)))
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        frames.append(im)
    save('polvo', frames, 3)


def sound_wave():
    frames = []
    for i in range(4):
        im, d = new(56, 48)
        for k in range(4):
            r = 8 + k * 6 + i * 1.5
            col = [(255, 80, 170, 255), (255, 160, 220, 255), (255, 255, 255, 255), (200, 40, 140, 255)][(k + i) % 4]
            d.arc([28 - r - 14, 24 - r, 28 + r - 14, 24 + r], -55, 55, fill=col, width=3)
        # mano cornuda
        d.rectangle([4, 20, 11, 30], fill=(240, 60, 60, 255))
        d.rectangle([4, 12, 6, 20], fill=(230, 170, 120, 255)); d.rectangle([9, 12, 11, 20], fill=(230, 170, 120, 255))
        frames.append(outline(im))
    save('onda_metal', frames, 4, True)


def note_shape(d, x, y, col, s=1.0, double=False):
    d.ellipse([x, y + 8 * s, x + 6 * s, y + 13 * s], fill=col)
    d.rectangle([x + 5 * s, y, x + 6.5 * s, y + 11 * s], fill=col)
    if double:
        d.ellipse([x + 9 * s, y + 6 * s, x + 15 * s, y + 11 * s], fill=col)
        d.rectangle([x + 14 * s, y - 2 * s, x + 15.5 * s, y + 9 * s], fill=col)
        d.polygon([(x + 5 * s, y), (x + 15.5 * s, y - 2 * s), (x + 15.5 * s, y + 1 * s), (x + 5 * s, y + 3 * s)], fill=col)
    else:
        d.polygon([(x + 6 * s, y), (x + 11 * s, y + 4 * s), (x + 10 * s, y + 6 * s), (x + 6 * s, y + 3 * s)], fill=col)


def notes():
    frames = []
    cols = [(80, 200, 255, 255), (255, 220, 60, 255), (255, 255, 255, 255)]
    for i in range(4):
        im, d = new(48, 36)
        for k in range(3):
            y = 6 + k * 9 + 3 * math.sin(i * 1.57 + k * 2)
            note_shape(d, 6 + k * 13, y, cols[(k + i) % 3], 1.0, k == 1)
        frames.append(outline(im))
    save('notas', frames, 4, True)


def big_note_beam():
    frames = []
    for i in range(4):
        im, d = new(96, 64)
        for y in range(16, 48):
            a = 1 - abs(y - 32) / 16
            col = (int(80 + 175 * a), int(180 + 75 * a), 255, int(255 * (0.4 + 0.6 * a)))
            d.line([(0, y), (95, y)], fill=col)
        for k in range(4):
            x = (k * 26 + i * 7) % 96
            note_shape(d, x, 18 + 6 * math.sin(k + i), (255, 230, 80, 255), 1.4, k % 2 == 0)
        frames.append(im)
    save('rayo_notas', frames, 3, True)


def badge():
    frames = []
    for i in range(8):
        im, d = new(28, 28)
        sx = abs(math.cos(i * math.pi / 8))
        w = max(2, int(22 * sx))
        x0 = 14 - w // 2
        d.rectangle([x0, 6, x0 + w, 22], fill=(245, 245, 235, 255), outline=(30, 30, 40, 255))
        if w > 10:
            d.rectangle([x0 + 2, 9, x0 + w * 0.4, 18], fill=(70, 120, 200, 255))
            d.line([(x0 + w * 0.5, 11), (x0 + w - 3, 11)], fill=(30, 30, 40, 255))
            d.line([(x0 + w * 0.5, 15), (x0 + w - 3, 15)], fill=(30, 30, 40, 255))
        d.line([(14, 0), (14, 6)], fill=(200, 160, 40, 255), width=2)
        frames.append(im)
    save('credencial', frames, 2, True)


def shockwave():
    frames = []
    for i in range(6):
        im, d = new(140, 48); t = i / 5
        for k in range(5):
            h = 40 * (1 - k * 0.15) * (0.6 + 0.4 * math.sin(t * math.pi + k))
            x = 10 + k * 26
            col = [(255, 120, 40, 255), (255, 200, 60, 255), (255, 80, 160, 255)][(k + i) % 3]
            d.polygon([(x, 47), (x + 13, 47 - h), (x + 26, 47)], fill=col)
        for k in range(10):
            x, y = rng.uniform(5, 135), rng.uniform(10, 40)
            d.rectangle([x, y, x + 3, y + 3], fill=(120, 90, 70, 255))
        frames.append(outline(im))
    save('onda_choque', frames, 3, True)


def explosion():
    frames = []
    for i in range(11):
        im, d = new(96, 96); t = i / 10
        R = 10 + 38 * math.sqrt(t)
        cols = [(255, 255, 220), (255, 220, 80), (255, 130, 30), (200, 40, 30), (70, 50, 50)]
        for k, cc in enumerate(cols):
            r = R * (1 - k * 0.17) if t < 0.5 else R * (1 - k * 0.17) * (1 - (t - 0.5) * (0.3 + k * 0.1))
            idx = min(4, max(0, (4 - k) // 2 + int(t * 3)))
            col = cols[idx]
            for b in range(8):
                a = b * math.pi / 4 + k
                bx, by = 48 + r * 0.35 * math.cos(a), 48 + r * 0.35 * math.sin(a)
                rr = r * 0.6
                d.ellipse([bx - rr, by - rr, bx + rr, by + rr], fill=col + (255 if t < 0.8 else int(255 * (1 - t) * 5),))
        frames.append(im)
    save('explosion', frames, 3)


def aura():
    frames = []
    for i in range(6):
        im, d = new(80, 130)
        for k in range(14):
            x = 40 + 30 * math.sin(k * 1.7 + i * 0.9)
            h = 40 + 50 * abs(math.sin(k * 2.3 + i))
            w = 10 + 6 * math.sin(k)
            y0 = 125 - h - (i * 9 + k * 13) % 30
            a = 120 + 100 * ((k + i) % 3) // 2
            d.polygon([(x - w, 128), (x, y0), (x + w, 128)], fill=(255, 255, 255, int(a)))
        arr = np.asarray(im).astype(np.float32)
        yy, xx = np.mgrid[0:130, 0:80]
        fall = (yy / 130.0) ** 1.3 * np.clip(1 - np.abs(xx - 40) / 40.0, 0, 1) ** 0.6
        arr[..., 3] *= fall
        frames.append(Image.fromarray(arr.astype(np.uint8), 'RGBA'))
    save('aura', frames, 3, True)


def tornado():
    frames = []
    for i in range(6):
        im, d = new(64, 110)
        for y in range(0, 110, 4):
            w = 6 + y * 0.25
            off = 6 * math.sin(y * 0.15 + i * 1.1)
            col = [(40, 220, 110, 230), (150, 255, 180, 230), (20, 140, 70, 230)][(y // 4 + i) % 3]
            d.ellipse([32 + off - w, y, 32 + off + w, y + 6], outline=col, width=2)
        frames.append(im)
    save('tornado', frames, 2, True)


def energy_fist():
    frames = []
    for i in range(4):
        im, d = new(90, 64)
        for k in range(6):
            r = 30 - k * 4
            col = [(255, 210, 60, 140), (255, 240, 150, 180), (255, 255, 255, 220), (180, 120, 255, 160)][(k + i) % 4]
            d.ellipse([60 - r, 32 - r * 0.8, 60 + r, 32 + r * 0.8], fill=col)
        for k in range(8):
            y = 8 + k * 6
            d.line([(0 + (i * 9 + k * 7) % 30, y), (40 + (i * 9 + k * 7) % 30, y)], fill=(255, 230, 120, 200), width=2)
        # puño
        d.rectangle([52, 22, 76, 42], fill=(255, 245, 200, 255), outline=(120, 70, 0, 255))
        for f in range(4):
            d.line([(70, 24 + f * 5), (76, 24 + f * 5)], fill=(150, 90, 0, 255))
        frames.append(im)
    save('puno_energia', frames, 3, True)


def fist_trail():
    frames = []
    for i in range(3):
        im, d = new(48, 24)
        for k in range(5):
            y = 4 + k * 4
            d.line([(4 + k * 3 + i * 4, y), (40 - k * 2, y)], fill=(255, 255, 255, 120 + 25 * k), width=2)
        frames.append(im)
    save('estela', frames, 2, True)


def flash_star():
    im, d = new(64, 64)
    for k in range(3):
        star(d, 32, 32, 3 + k, 30 - k * 8, 4, math.pi / 4 * k, [(255, 255, 255, 255), (255, 240, 150, 255), (255, 200, 60, 255)][k])
    save('destello', [im], 4)


def lightning():
    frames = []
    for i in range(4):
        im, d = new(48, 176)
        r = np.random.default_rng(20 + i)
        for width, col in ((7, (255, 230, 60, 255)), (3, (255, 255, 255, 255))):
            x = 24; pts = [(x, 0)]
            rr = np.random.default_rng(20 + i)
            for y in range(16, 177, 16):
                x = int(np.clip(x + rr.integers(-13, 14), 8, 40)); pts.append((x, y))
            d.line(pts, fill=col, width=width, joint='curve')
        for k in range(3):
            y0 = int(r.integers(30, 130)); x0 = int(r.integers(14, 34)); s_ = 1 if k % 2 else -1
            d.line([(x0, y0), (x0 + 12 * s_, y0 + 14), (x0 + 8 * s_, y0 + 26)], fill=(255, 240, 120, 255), width=2)
        frames.append(outline(im, (90, 60, 160, 255)))
    save('rayo', frames, 2, True)


def maple_leaf_pts(cx, cy, s, ang):
    half = [(0, -1.0), (0.15, -0.65), (0.33, -0.72), (0.27, -0.25), (0.55, -0.5), (0.62, -0.33), (0.95, -0.38),
            (0.82, -0.08), (0.95, 0.02), (0.52, 0.38), (0.58, 0.55), (0.08, 0.48), (0.08, 0.95)]
    pts = half + [(-x, y) for x, y in reversed(half)]
    c, sn = math.cos(ang), math.sin(ang)
    return [(cx + (x * c - y * sn) * s, cy + (x * sn + y * c) * s) for x, y in pts]


def leaf():
    frames = []
    for i in range(6):
        im, d = new(30, 30)
        d.polygon(maple_leaf_pts(15, 15, 12, i * math.pi / 3), fill=(50, 210, 110, 255))
        d.polygon(maple_leaf_pts(15, 15, 6, i * math.pi / 3), fill=(150, 255, 170, 255))
        frames.append(outline(im, (10, 60, 30, 255)))
    save('hoja', frames, 2, True)


# ------------------------------------------------------------------ efectos de los personajes nuevos
GLYPHS = {   # mini tipografía 3x5 para código y números
    '{': ['011', '010', '110', '010', '011'], '}': ['110', '010', '011', '010', '110'],
    '<': ['001', '010', '100', '010', '001'], '>': ['100', '010', '001', '010', '100'],
    '/': ['001', '001', '010', '100', '100'], ';': ['000', '010', '000', '010', '100'],
    '0': ['111', '101', '101', '101', '111'], '1': ['010', '110', '010', '010', '111'],
    '2': ['111', '001', '111', '100', '111'], '3': ['111', '001', '111', '001', '111'],
    '4': ['101', '101', '111', '001', '001'], '5': ['111', '100', '111', '001', '111'],
    '6': ['111', '100', '111', '101', '111'], '7': ['111', '001', '010', '010', '010'],
    '8': ['111', '101', '111', '101', '111'], '9': ['111', '101', '111', '001', '111'],
    '+': ['000', '010', '111', '010', '000'], 'x': ['000', '101', '010', '101', '000'],
    '=': ['000', '111', '000', '111', '000'], '?': ['111', '001', '011', '000', '010'],
}


def glyph(d, ch, x, y, col, s=1):
    for r, row in enumerate(GLYPHS[ch]):
        for c, v in enumerate(row):
            if v == '1':
                d.rectangle([x + c * s, y + r * s, x + c * s + s - 1, y + r * s + s - 1], fill=col)


def code_proj():
    frames = []
    for i in range(4):
        im, d = new(44, 30)
        d.rounded_rectangle([2, 3, 41, 26], 4, fill=(10, 30, 20, 230), outline=(80, 255, 120, 255))
        txt = ['{;}', '</>', '{0}', '<1>'][i]
        for k, ch in enumerate(txt):
            glyph(d, ch, 8 + k * 10, 8, (120, 255, 150, 255), 2)
        frames.append(outline(im, (0, 60, 20, 255)))
    save('codigo', frames, 3, True)


def column(name, draw_item, base_col, n=4, items=9, seed=0):
    """Columna de 48x176 (para ataques que caen sobre el rival)."""
    frames = []
    for i in range(n):
        im, d = new(48, 176)
        for y in range(176):
            a = int(110 * (1 - abs(y - 88) / 88) + 30)
            d.line([(14, y), (33, y)], fill=base_col + (a,))
        r = np.random.default_rng(seed)
        for k in range(items):
            x = int(r.integers(4, 30)); y = int((r.integers(0, 176) + i * 22) % 176)
            draw_item(d, x, y, k)
        frames.append(im)
    save(name, frames, 2, True)


def cat_shape(d, x, y, s=1.0, run=0, col=(255, 140, 30, 255), dark=(200, 90, 20, 255)):
    """Gato naranja original, de perfil, corriendo hacia la derecha."""
    d.ellipse([x + 4 * s, y + 6 * s, x + 24 * s, y + 16 * s], fill=col)                     # cuerpo
    d.ellipse([x + 20 * s, y + 2 * s, x + 32 * s, y + 12 * s], fill=col)                    # cabeza
    d.polygon([(x + 21 * s, y + 4 * s), (x + 22 * s, y - 2 * s), (x + 26 * s, y + 3 * s)], fill=col)   # oreja
    d.polygon([(x + 27 * s, y + 3 * s), (x + 30 * s, y - 2 * s), (x + 31 * s, y + 5 * s)], fill=col)
    for k in range(3):                                                                         # rayas
        d.line([(x + (8 + k * 5) * s, y + 7 * s), (x + (10 + k * 5) * s, y + 11 * s)], fill=dark, width=max(1, int(s)))
    d.rectangle([x + 28 * s, y + 6 * s, x + 29 * s, y + 7 * s], fill=(30, 20, 10, 255))       # ojo
    d.line([(x + 4 * s, y + 9 * s), (x - 3 * s, y + (4 + 3 * run) * s)], fill=col, width=max(2, int(2 * s)))  # cola
    for k, ph in enumerate((0, 1, 0, 1)):                                                      # patas
        ox = x + (7 + k * 5) * s; off = (2 if (ph + run) % 2 else -2) * s
        d.line([(ox, y + 14 * s), (ox + off, y + 19 * s)], fill=dark, width=max(2, int(1.5 * s)))


def cat_proj():
    frames = []
    for i in range(4):
        im, d = new(40, 28)
        cat_shape(d, 5, 6, 1.0, i)
        frames.append(outline(im, (60, 25, 5, 255)))
    save('gato', frames, 3, True)


def cats_column():
    def item(d, x, y, k):
        im2 = Image.new('RGBA', (40, 28)); cat_shape(ImageDraw.Draw(im2), 5, 6, 0.7, k)
        d._image.paste(im2.rotate(-90 if k % 2 else -70, expand=True), (x - 6, y - 10), im2.rotate(-90 if k % 2 else -70, expand=True))
    column('gatos', item, (255, 160, 60), items=7, seed=3)


def dove_proj():
    frames = []
    for i in range(4):
        im, d = new(36, 28)
        up = i % 2 == 0
        d.ellipse([8, 11, 26, 19], fill=(250, 250, 255, 255))                     # cuerpo
        d.ellipse([22, 8, 30, 15], fill=(250, 250, 255, 255))                     # cabeza
        d.polygon([(30, 11), (34, 12), (30, 13)], fill=(255, 180, 60, 255))       # pico
        d.polygon([(8, 15), (1, 11), (2, 19)], fill=(235, 235, 250, 255))         # cola
        if up:
            d.polygon([(12, 13), (20, 13), (14, 1), (9, 3)], fill=(230, 235, 255, 255))
        else:
            d.polygon([(12, 15), (20, 15), (15, 26), (10, 24)], fill=(230, 235, 255, 255))
        d.point((27, 10), fill=(20, 20, 40, 255))
        # ramita de olivo
        d.line([(31, 14), (35, 18)], fill=(90, 160, 60, 255), width=1)
        d.point((34, 16), fill=(120, 200, 80, 255))
        frames.append(outline(im, (80, 100, 160, 255)))
    save('paloma', frames, 3, True)


def plane_proj():
    frames = []
    for i in range(4):
        im, d = new(32, 20)
        dy = [0, 1, 0, -1][i]
        d.polygon([(2, 6 + dy), (30, 10 + dy), (2, 16 + dy)], fill=(255, 255, 255, 255))
        d.polygon([(2, 10 + dy), (30, 10 + dy), (8, 13 + dy)], fill=(200, 210, 230, 255))
        d.line([(4, 8 + dy), (28, 10 + dy)], fill=(150, 170, 220, 255))
        frames.append(outline(im, (40, 50, 90, 255)))
    save('avion', frames, 3, True)


def ball(d, cx, cy, r, rot):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))
    for k in range(5):
        a = rot + k * 2 * math.pi / 5
        px, py = cx + r * 0.55 * math.cos(a), cy + r * 0.55 * math.sin(a)
        rr = r * 0.22
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(30, 30, 40, 255))
    d.ellipse([cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2], fill=(30, 30, 40, 255))


def ball_proj():
    frames = []
    for i in range(4):
        im, d = new(26, 26)
        ball(d, 13, 13, 10, i * 0.6)
        frames.append(outline(im))
    save('pelota', frames, 2, True)
    frames = []
    for i in range(4):
        im, d = new(72, 72)
        for k in range(4):                                       # estela roja y blanca
            col = (230, 30, 50, 140) if k % 2 == 0 else (255, 255, 255, 140)
            d.ellipse([2 + k * 4, 20 + k * 2, 30 + k * 4, 52 - k * 2], fill=col)
        ball(d, 44, 36, 24, i * 0.5)
        frames.append(outline(im))
    save('pelota_gigante', frames, 2, True)


def ai_beam():
    frames = []
    for i in range(4):
        im, d = new(96, 64)
        for y in range(16, 48):
            a = 1 - abs(y - 32) / 16
            d.line([(0, y), (95, y)], fill=(int(40 + 120 * a), int(160 + 95 * a), 255, int(255 * (0.35 + 0.65 * a))))
        r = np.random.default_rng(30 + i)
        nodes = [(int(r.integers(4, 92)), int(r.integers(20, 44))) for _ in range(7)]
        for a_, b_ in zip(nodes, nodes[1:]):
            d.line([a_, b_], fill=(255, 255, 255, 200), width=1)
        for x, y in nodes:
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255, 255))
        frames.append(im)
    save('rayo_ia', frames, 3, True)


def code_column():
    chars = '{}<>/;01'
    column('lluvia_codigo', lambda d, x, y, k: glyph(d, chars[k % len(chars)], x, y, (120, 255, 150, 255), 3),
           (60, 220, 100), items=12, seed=5)


def numbers_column():
    chars = '9x8=72+?'
    column('numeros', lambda d, x, y, k: glyph(d, chars[k % len(chars)], x, y, (255, 245, 150, 255), 3),
           (255, 230, 120), items=11, seed=6)


def light_column():
    frames = []
    for i in range(4):
        im, d = new(48, 176)
        w = [10, 16, 20, 14][i]
        for x in range(24 - w, 24 + w):
            a = 1 - abs(x - 24) / w
            d.line([(x, 0), (x, 175)], fill=(255, 255, int(200 + 55 * a), int(255 * a)))
        for k in range(6):
            y = (k * 30 + i * 9) % 176
            star(d, 24 + (k % 2 * 2 - 1) * 10, y, 1, 4, 4, 0, (255, 255, 255, 255))
        frames.append(im)
    save('luz', frames, 2, True)


def confetti_column():
    def item(d, x, y, k):
        col = (230, 30, 50, 255) if k % 2 == 0 else (255, 255, 255, 255)
        d.polygon([(x, y), (x + 5, y + 2), (x + 3, y + 7), (x - 2, y + 5)], fill=col)
    frames = []
    for i in range(4):
        im, d = new(96, 176)
        r = np.random.default_rng(8)
        for k in range(40):
            x = int(r.integers(2, 92)); y = int((r.integers(0, 176) + i * 14) % 176)
            item(d, x, y, k)
        frames.append(im)
    save('papelitos', frames, 2, True)


def heart_shape(d, cx, cy, s, col):
    d.ellipse([cx - s, cy - s * 0.6, cx, cy + s * 0.3], fill=col)
    d.ellipse([cx, cy - s * 0.6, cx + s, cy + s * 0.3], fill=col)
    d.polygon([(cx - s, cy - s * 0.05), (cx + s, cy - s * 0.05), (cx, cy + s)], fill=col)


def hearts():
    frames = []
    for i in range(4):
        im, d = new(24, 24)
        s = [8, 9, 10, 9][i]
        heart_shape(d, 12, 11, s, (255, 60, 120, 255))
        heart_shape(d, 10, 9, s * 0.35, (255, 170, 200, 255))
        frames.append(outline(im, (120, 10, 50, 255)))
    save('corazon', frames, 4, True)


def anger():
    frames = []
    for i in range(4):
        im, d = new(24, 24)
        k = [0, 1, 2, 1][i]
        for a in range(4):
            ang = a * math.pi / 2 + math.pi / 4
            x0, y0 = 12 + math.cos(ang) * 3, 12 + math.sin(ang) * 3
            x1, y1 = 12 + math.cos(ang) * (9 + k), 12 + math.sin(ang) * (9 + k)
            d.line([(x0, y0), (x1, y1)], fill=(255, 40, 40, 255), width=3)
        frames.append(outline(im, (90, 0, 0, 255)))
    save('enojo', frames, 3, True)


def friendship():
    frames = []
    for i in range(4):
        im, d = new(32, 32)
        star(d, 16, 16, 3, 7 + i % 2 * 3, 4, i * 0.4, (255, 240, 120, 255))
        star(d, 6, 8, 1, 3, 4, 0, (255, 255, 255, 255))
        star(d, 26, 24, 1, 3 + i % 2, 4, 0, (255, 255, 255, 255))
        frames.append(im)
    save('brillo', frames, 4, True)



# ------------------------------------------------------------------ Nehuen bostero (azul y oro)
BLUE = (20, 60, 170, 255)
BLUE_D = (10, 30, 100, 255)
GOLD = (255, 205, 40, 255)


def scarf():
    """Bufanda azul y oro que vuela girando (original, sin escudos)."""
    frames = []
    for i in range(4):
        im, d = new(48, 30)
        ph = i * math.pi / 2
        pts_top, pts_bot = [], []
        for k in range(9):
            x = 4 + k * 5
            y = 15 + 6 * math.sin(ph + k * 0.8)
            pts_top.append((x, y - 5)); pts_bot.append((x, y + 5))
        d.polygon(pts_top + pts_bot[::-1], fill=BLUE)
        for k in range(9):                                   # franjas amarillas
            if k % 3 == 1:
                x = 4 + k * 5
                y = 15 + 6 * math.sin(ph + k * 0.8)
                d.rectangle([x - 2, y - 5, x + 2, y + 5], fill=GOLD)
        for k in (0, 8):                                     # flecos
            x = 4 + k * 5
            y = 15 + 6 * math.sin(ph + k * 0.8)
            for f in range(-4, 5, 2):
                d.line([(x, y + f), (x + (-4 if k == 0 else 4), y + f + 1)], fill=GOLD, width=1)
        frames.append(outline(im, (5, 15, 50, 255)))
    save('bufanda', frames, 3, True)


def xeneize_beam():
    frames = []
    for i in range(4):
        im, d = new(96, 64)
        for y in range(14, 50):
            a = 1 - abs(y - 32) / 18
            gold = abs(y - 32) < 6
            col = (255, 210, 60, int(255 * (0.6 + 0.4 * a))) if gold else (30, 80, 200, int(255 * (0.35 + 0.65 * a)))
            d.line([(0, y), (95, y)], fill=col)
        for k in range(5):
            x = (k * 22 + i * 9) % 96
            star(d, x, 32 + (k % 2 * 2 - 1) * 10, 1, 4, 4, 0, (255, 255, 255, 255))
        frames.append(im)
    save('rayo_xeneize', frames, 3, True)


def confetti_boca():
    frames = []
    for i in range(4):
        im, d = new(96, 176)
        r = np.random.default_rng(9)
        for k in range(40):
            x = int(r.integers(2, 92)); y = int((r.integers(0, 176) + i * 14) % 176)
            col = BLUE if k % 2 == 0 else GOLD
            d.polygon([(x, y), (x + 5, y + 2), (x + 3, y + 7), (x - 2, y + 5)], fill=col)
        frames.append(im)
    save('papelitos_boca', frames, 2, True)


def main():
    os.makedirs(OUT, exist_ok=True)
    lightning(); leaf()
    spark(40, 7, [(255, 230, 90, 255), (255, 255, 255, 255), (255, 255, 255, 255)], 'chispa_golpe')
    spark(64, 8, [(255, 90, 40, 255), (255, 220, 80, 255), (255, 255, 255, 255)], 'chispa_fuerte', 10)
    spark(36, 6, [(80, 170, 255, 255), (200, 240, 255, 255), (255, 255, 255, 255)], 'chispa_bloqueo', 6)
    dust(); sound_wave(); notes(); big_note_beam(); badge(); shockwave(); explosion(); aura()
    tornado(); energy_fist(); fist_trail(); flash_star()
    code_proj(); cat_proj(); cats_column(); dove_proj(); plane_proj(); ball_proj(); ai_beam()
    code_column(); numbers_column(); light_column(); confetti_column(); hearts(); anger(); friendship()
    scarf(); xeneize_beam(); confetti_boca()
    with open(os.path.join(OUT, 'effects_meta.json'), 'w') as f:
        json.dump(META, f, indent=1)
    print('efectos:', len(META))


if __name__ == '__main__':
    main()
