"""Reproducción de animaciones de personajes a partir de los spritesheets.

Cada animación es una tira PNG (assets/characters/<p>/<p>_<anim>.png) con cuadros de
tamaño uniforme; su duración por cuadro (ticks a 60 fps) y si se repite están en
<p>_meta.json. En combate, Fighter usa el mismo meta para sincronizar golpes y cuadros.
"""
import pygame
import config as C
from game import assets


def draw_fighter(surf, name, anim, frame, x, y, facing=1, scale=C.SCALE, glow=None, alpha=None):
    """Dibuja un luchador fuera del combate con el mismo renderer que en la pelea."""
    return assets.character(name).renderer.draw(surf, x, y, anim, frame, facing, scale, glow=glow, alpha=alpha)


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
        if self.tick >= max(1, round(info['dur'] / self.spr.profile.anim_speed)):
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


