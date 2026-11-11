"""Reproducción de animaciones de personajes a partir de los spritesheets.

Cada animación es una tira PNG (assets/characters/<p>/<p>_<anim>.png) con cuadros de
tamaño uniforme; su duración por cuadro (ticks a 60 fps) y si se repite están en
<p>_meta.json. En combate, Fighter usa el mismo meta para sincronizar golpes y cuadros.
"""
import pygame
import config as C
from game import assets


def draw_fighter(surf, name, anim, frame, x, y, facing=1, scale=C.SCALE, glow=None):
    spr = assets.character(name)
    img, dx, dy = spr.frame_surface(anim, frame, facing, scale)
    if glow:
        g = img.copy()
        g.fill(glow + (0,), special_flags=pygame.BLEND_RGB_MULT)
        for ox, oy in ((-4, 0), (4, 0), (0, -4), (0, 4)):
            surf.blit(g, (x + dx + ox, y + dy + oy))
    surf.blit(img, (x + dx, y + dy))


class AnimPlayer:
    """Reproduce una animación de personaje fuera del combate."""

    def __init__(self, name, anim='idle', loop=True, then='idle'):
        self.name = name
        self.spr = assets.character(name)
        self.set(anim, loop, then)

    def set(self, anim, loop=True, then='idle'):
        self.anim, self.loop, self.then = anim, loop, then
        self.frame = 0
        self.tick = 0

    def update(self):
        info = self.spr.info(self.anim)
        self.tick += 1
        if self.tick >= info['dur']:
            self.tick = 0
            self.frame += 1
            if self.frame >= info['frames']:
                if self.loop:
                    self.frame = 0
                elif self.then:
                    self.set(self.then, True, None)
                else:
                    self.frame = info['frames'] - 1

    def draw(self, surf, x, y, facing=1, scale=C.SCALE, glow=None):
        draw_fighter(surf, self.name, self.anim, self.frame, x, y, facing, scale, glow)


