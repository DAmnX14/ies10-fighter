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


def main():
    os.makedirs(OUT, exist_ok=True)
    spark(40, 7, [(255, 230, 90, 255), (255, 255, 255, 255), (255, 255, 255, 255)], 'chispa_golpe')
    spark(64, 8, [(255, 90, 40, 255), (255, 220, 80, 255), (255, 255, 255, 255)], 'chispa_fuerte', 10)
    spark(36, 6, [(80, 170, 255, 255), (200, 240, 255, 255), (255, 255, 255, 255)], 'chispa_bloqueo', 6)
    dust(); sound_wave(); notes(); big_note_beam(); badge(); shockwave(); explosion(); aura()
    tornado(); energy_fist(); fist_trail(); flash_star()
    with open(os.path.join(OUT, 'effects_meta.json'), 'w') as f:
        json.dump(META, f, indent=1)
    print('efectos:', len(META))


if __name__ == '__main__':
    main()
