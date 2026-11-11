"""Carga y caché de recursos (sprites, efectos, fuentes, imágenes)."""
import os
import json
import pygame
import config as C

_fonts = {}
_images = {}


def font(size):
    if size not in _fonts:
        try:
            _fonts[size] = pygame.font.Font(C.FONT_PATH, size)
        except (OSError, FileNotFoundError):
            _fonts[size] = pygame.font.SysFont('couriernew', size, bold=True)
    return _fonts[size]


def image(path, alpha=True):
    if path not in _images:
        img = pygame.image.load(path)
        _images[path] = img.convert_alpha() if alpha else img.convert()
    return _images[path]


class Strip:
    """Animación cargada desde una tira horizontal, recortada por cuadro."""

    def __init__(self, path, fw, fh, n):
        sheet = image(path)
        self.frames = []          # (surface recortada, offset_x, offset_y) en px nativos
        for i in range(n):
            sub = sheet.subsurface((i * fw, 0, fw, fh))
            r = sub.get_bounding_rect()
            if r.w == 0:
                r = pygame.Rect(0, 0, 1, 1)
            self.frames.append((sub.subsurface(r).copy(), r.x, r.y))
        self.n = n


class CharacterSprites:
    def __init__(self, name):
        self.name = name
        d = os.path.join(C.CHAR_DIR, name)
        with open(os.path.join(d, f'{name}_meta.json'), encoding='utf-8') as f:
            self.meta = json.load(f)
        self.fw, self.fh = self.meta['frame_w'], self.meta['frame_h']
        self.ax, self.ay = self.meta['anchor']
        self.anims = {}
        for an, info in self.meta['animations'].items():
            self.anims[an] = Strip(os.path.join(d, info['file']), self.fw, self.fh, info['frames'])
        self.portrait = image(os.path.join(d, f'{name}_retrato.png'))
        self._scaled = {}

    def info(self, anim):
        return self.meta['animations'][anim]

    def joint(self, anim, idx, j):
        return self.meta['animations'][anim]['joints'][idx][j]

    def bbox(self, anim, idx):
        return self.meta['animations'][anim]['bbox'][idx]

    def frame_surface(self, anim, idx, facing, scale=C.SCALE):
        """Devuelve (surface escalada, dx, dy) relativos al ancla del suelo."""
        key = (anim, idx, facing, scale)
        hit = self._scaled.get(key)
        if hit is None:
            surf, ox, oy = self.anims[anim].frames[idx]
            s = pygame.transform.scale(surf, (surf.get_width() * scale, surf.get_height() * scale))
            if facing < 0:
                s = pygame.transform.flip(s, True, False)
                dx = -(ox + surf.get_width() - self.ax) * scale
            else:
                dx = (ox - self.ax) * scale
            dy = (oy - self.ay) * scale
            hit = (s, dx, dy)
            if len(self._scaled) > 700:
                self._scaled.clear()
            self._scaled[key] = hit
        return hit


_char_cache = {}


def character(name):
    if name not in _char_cache:
        _char_cache[name] = CharacterSprites(name)
    return _char_cache[name]


class Effects:
    def __init__(self):
        with open(os.path.join(C.FX_DIR, 'effects_meta.json')) as f:
            self.meta = json.load(f)
        self.frames = {}
        for k, m in self.meta.items():
            sheet = image(os.path.join(C.FX_DIR, m['file']))
            fr = []
            for i in range(m['frames']):
                sub = sheet.subsurface((i * m['w'], 0, m['w'], m['h']))
                fr.append(pygame.transform.scale(sub, (m['w'] * C.SCALE, m['h'] * C.SCALE)))
            self.frames[k] = fr
        self._tinted = {}

    def tinted(self, name, color):
        key = (name, color)
        if key not in self._tinted:
            out = []
            for f in self.frames[name]:
                s = f.copy()
                s.fill(color + (255,), special_flags=pygame.BLEND_RGBA_MULT)
                out.append(s)
            self._tinted[key] = out
        return self._tinted[key]


_fx = None


def effects():
    global _fx
    if _fx is None:
        _fx = Effects()
    return _fx


def preload_all():
    for c in C.CHARACTERS:
        character(c)
    effects()
