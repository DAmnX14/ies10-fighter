"""Utilidades de interfaz: texto arcade, degradados, paneles, CRT y transiciones."""
import math
import pygame
import config as C
from game import assets

_cache = {}
ACCENTS = {'Á': ('A', 'acute'), 'É': ('E', 'acute'), 'Í': ('I', 'acute'), 'Ó': ('O', 'acute'),
           'Ú': ('U', 'acute'), 'Ñ': ('N', 'tilde'), 'Ü': ('U', 'diaer')}


def render(f, s, color):
    """Renderiza texto; dibuja a mano los acentos de las mayúsculas (la fuente
    pixel no los trae a tamaño completo). Devuelve una superficie con alfa."""
    if not any(ch in ACCENTS for ch in s):
        raw = f.render(s, False, color)
        out = pygame.Surface(raw.get_size(), pygame.SRCALPHA)
        out.blit(raw, (0, 0))
        return out
    plain = ''.join(ACCENTS[ch][0] if ch in ACCENTS else ch for ch in s)
    raw = f.render(plain, False, color)
    size = f.get_height()
    pad = max(3, size // 3)
    out = pygame.Surface((raw.get_width(), raw.get_height() + pad), pygame.SRCALPHA)
    out.blit(raw, (0, pad))
    u = max(1, size // 8)
    for i, ch in enumerate(s):
        if ch not in ACCENTS:
            continue
        x0 = f.size(plain[:i])[0]
        w = f.size(plain[i])[0]
        cx = x0 + w // 2
        kind = ACCENTS[ch][1]
        if kind == 'acute':
            for k in range(3):
                pygame.draw.rect(out, color, (cx - u + k * u, pad - u * (k + 1) + u, u * 2, u))
        elif kind == 'tilde':
            pts = [(cx - 3 * u, pad - u), (cx - 2 * u, pad - 2 * u), (cx - u, pad - 2 * u), (cx + u, pad - u),
                   (cx + 2 * u, pad - u), (cx + 3 * u, pad - 2 * u)]
            for (x, y) in pts:
                pygame.draw.rect(out, color, (x, y, u, u))
        else:
            pygame.draw.rect(out, color, (cx - 2 * u, pad - 2 * u, u, u))
            pygame.draw.rect(out, color, (cx + u, pad - 2 * u, u, u))
    return out


def text(s, size, color=C.WHITE):
    return render(assets.font(size), s, color)


def text_outline(s, size, color=C.WHITE, outline=(0, 0, 0), w=None, shadow=True):
    key = ('o', s, size, color, outline, w, shadow)
    if key in _cache:
        return _cache[key]
    w = w or max(2, size // 8)
    f = assets.font(size)
    base = render(f, s, color)
    ol = render(f, s, outline)
    W, Hh = base.get_width() + w * 2 + (w if shadow else 0), base.get_height() + w * 2 + (w if shadow else 0)
    surf = pygame.Surface((W, Hh), pygame.SRCALPHA)
    if shadow:
        for dx in range(-w, w + 1):
            for dy in range(-w, w + 1):
                surf.blit(ol, (w + dx + w, w + dy + w))
    for dx in range(-w, w + 1):
        for dy in range(-w, w + 1):
            if dx * dx + dy * dy <= w * w + 1:
                surf.blit(ol, (w + dx, w + dy))
    surf.blit(base, (w, w))
    if len(_cache) > 600:
        _cache.clear()
    _cache[key] = surf
    return surf


def text_gradient(s, size, top=(255, 250, 140), bottom=(255, 90, 0), outline=(40, 0, 20), w=None,
                  extrude=0, extrude_color=(120, 20, 10)):
    key = ('g', s, size, top, bottom, outline, w, extrude, extrude_color)
    if key in _cache:
        return _cache[key]
    w = w or max(2, size // 13)
    f = assets.font(size)
    mask = render(f, s, C.WHITE)
    mw, mh = mask.get_size()
    grad = pygame.Surface((mw, mh), pygame.SRCALPHA)
    for y in range(mh):
        k = y / max(1, mh - 1)
        col = tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3))
        pygame.draw.line(grad, col, (0, y), (mw, y))
    # brillo
    pygame.draw.line(grad, (255, 255, 255), (0, int(mh * 0.28)), (mw, int(mh * 0.28)), max(1, size // 16))
    g = mask.copy()
    g.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    ol = render(f, s, outline)
    ex = render(f, s, extrude_color)
    W, Hh = mw + w * 2 + extrude, mh + w * 2 + extrude
    surf = pygame.Surface((W, Hh), pygame.SRCALPHA)
    for e in range(extrude, 0, -1):
        for dx in range(-w, w + 1):
            for dy in range(-w, w + 1):
                if dx * dx + dy * dy <= w * w + 1:
                    surf.blit(ol, (w + dx + e, w + dy + e))
        surf.blit(ex, (w + e, w + e))
    for dx in range(-w, w + 1):
        for dy in range(-w, w + 1):
            if dx * dx + dy * dy <= w * w + 1:
                surf.blit(ol, (w + dx, w + dy))
    surf.blit(g, (w, w))
    _cache[key] = surf
    return surf


def blit_center(surf, img, cx, cy):
    surf.blit(img, (int(cx - img.get_width() / 2), int(cy - img.get_height() / 2)))


def panel(surf, rect, color=(10, 15, 40, 200), border=(255, 214, 10), w=3):
    r = pygame.Rect(rect)
    s = pygame.Surface(r.size, pygame.SRCALPHA)
    s.fill(color)
    surf.blit(s, r.topleft)
    pygame.draw.rect(surf, (0, 0, 0), r.inflate(4, 4), 2)
    pygame.draw.rect(surf, border, r, w)


_scan = None


def crt(surf):
    global _scan
    if _scan is None:
        _scan = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
        for y in range(0, C.HEIGHT, 3):
            pygame.draw.line(_scan, (0, 0, 0, 55), (0, y), (C.WIDTH, y))
        for i in range(30):
            a = int(90 * (1 - i / 30) ** 2)
            pygame.draw.rect(_scan, (0, 0, 0, a), (i, i, C.WIDTH - 2 * i, C.HEIGHT - 2 * i), 1)
    surf.blit(_scan, (0, 0))


def stat_bar(surf, x, y, w, h, value, maxv, color):
    pygame.draw.rect(surf, (0, 0, 0), (x - 2, y - 2, w + 4, h + 4))
    pygame.draw.rect(surf, (40, 40, 60), (x, y, w, h))
    seg = w / maxv
    for i in range(int(value)):
        pygame.draw.rect(surf, color, (x + i * seg + 1, y + 1, seg - 2, h - 2))


class Transition:
    """Barrido diagonal estilo arcade entre pantallas."""

    def __init__(self, duration=24):
        self.t = 0
        self.d = duration
        self.phase = 'out'      # out: tapando; in: destapando
        self.active = False
        self.callback = None

    def start(self, callback):
        self.active = True
        self.phase = 'out'
        self.t = 0
        self.callback = callback

    def update(self):
        if not self.active:
            return
        self.t += 1
        if self.phase == 'out' and self.t >= self.d:
            if self.callback:
                self.callback()
            self.phase = 'in'
            self.t = 0
        elif self.phase == 'in' and self.t >= self.d:
            self.active = False

    def draw(self, surf):
        if not self.active:
            return
        k = self.t / self.d
        if self.phase == 'in':
            k = 1 - k
        k = k * k * (3 - 2 * k)
        stripes = 12
        sh = C.HEIGHT / stripes
        for i in range(stripes):
            delay = i / stripes * 0.4
            kk = max(0, min(1, (k - delay) / 0.6)) if k < 1 else 1
            w = (C.WIDTH + 200) * kk
            x0 = -100 if i % 2 == 0 else C.WIDTH + 100 - w
            col = (12, 10, 30) if i % 2 == 0 else (20, 16, 50)
            pygame.draw.polygon(surf, col, [(x0, i * sh), (x0 + w + 60, i * sh), (x0 + w, (i + 1) * sh + 1),
                                            (x0 - 60, (i + 1) * sh + 1)])
        if k > 0.98:
            surf.fill((12, 10, 30))
            logo = text_gradient('IES 10 FIGHTER', 28)
            blit_center(surf, logo, C.WIDTH / 2, C.HEIGHT / 2)


def pulse(t, speed=0.1):
    return 0.5 + 0.5 * math.sin(t * speed)
