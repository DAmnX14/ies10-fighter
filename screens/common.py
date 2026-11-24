"""Elementos compartidos por las pantallas: fondo arcade, menús, navegación."""
import math
import os
import random
import pygame
import config as C
from game import assets, ui


class Scene:
    def __init__(self, game):
        self.game = game
        self.t = 0

    def handle_event(self, e):
        pass

    def update(self):
        self.t += 1

    def draw(self, surf):
        pass


# --------------------------------------------------------------- navegación
UP = (pygame.K_UP, pygame.K_w)
DOWN = (pygame.K_DOWN, pygame.K_s)
LEFT = (pygame.K_LEFT, pygame.K_a)
RIGHT = (pygame.K_RIGHT, pygame.K_d)
OK = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_f, pygame.K_1, pygame.K_KP1)
BACK = (pygame.K_ESCAPE, pygame.K_BACKSPACE)


def nav(e):
    if e.type != pygame.KEYDOWN:
        return None
    pad = getattr(e, 'pad', None)
    if pad:
        return 'ok' if pad == 'start' else pad
    if getattr(e, 'player', None):
        return None          # botón del mando sin significado en menús
    k = e.key
    if k in UP:
        return 'up'
    if k in DOWN:
        return 'down'
    if k in LEFT:
        return 'left'
    if k in RIGHT:
        return 'right'
    if k in OK:
        return 'ok'
    if k in BACK:
        return 'back'
    return None


# --------------------------------------------------------------- fondo
_bg = {}


def menu_background(surf, t, tint=(30, 20, 80), stage=True):
    if 'stage' not in _bg:
        raw = pygame.image.load(C.BG_PATH).convert()
        k = C.HEIGHT * 1.15 / raw.get_height()
        img = pygame.transform.smoothscale(raw, (int(raw.get_width() * k), int(C.HEIGHT * 1.15)))
        dark = pygame.Surface(img.get_size())
        dark.fill((0, 0, 0))
        dark.set_alpha(165)
        img.blit(dark, (0, 0))
        _bg['stage'] = img
    if stage:
        img = _bg['stage']
        ox = -(img.get_width() - C.WIDTH) / 2 + math.sin(t * 0.004) * (img.get_width() - C.WIDTH) / 2
        surf.blit(img, (ox, -40 + math.sin(t * 0.006) * 20))
    else:
        surf.fill((8, 6, 20))
    s = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
    for i in range(-2, 22):
        x = (i * 90 + t * 1.5) % (C.WIDTH + 400) - 200
        pygame.draw.polygon(s, tint + (40,), [(x, 0), (x + 40, 0), (x - 260, C.HEIGHT), (x - 300, C.HEIGHT)])
    surf.blit(s, (0, 0))
    # franjas superior e inferior
    pygame.draw.rect(surf, (0, 0, 0), (0, 0, C.WIDTH, 8))
    pygame.draw.rect(surf, (0, 0, 0), (0, C.HEIGHT - 8, C.WIDTH, 8))


def logo():
    p = os.path.join(C.UI_DIR, 'logo.png')
    if os.path.exists(p):
        return assets.image(p)
    return ui.text_gradient('IES 10 FIGHTER', 56, extrude=6)


def arcetech_logo():
    p = os.path.join(C.UI_DIR, 'arcetech.png')
    if os.path.exists(p):
        return assets.image(p)
    return ui.text_outline('ARCE TECH', 20, (60, 220, 120))


def help_bar(surf, txt):
    pygame.draw.rect(surf, (0, 0, 0), (0, C.HEIGHT - 38, C.WIDTH, 38))
    pygame.draw.line(surf, C.YELLOW, (0, C.HEIGHT - 38), (C.WIDTH, C.HEIGHT - 38), 2)
    ui.blit_center(surf, ui.text(txt, 12, (220, 220, 240)), C.WIDTH / 2, C.HEIGHT - 19)


from game.animations import draw_fighter, AnimPlayer  # noqa: E402,F401


class Menu:
    """Lista vertical de opciones con animación al pasar por cada una."""

    def __init__(self, items, x, y, spacing=58, size=30, align='center'):
        self.items = items
        self.sel = 0
        self.x, self.y, self.spacing, self.size = x, y, spacing, size
        self.align = align
        self.anim = [0.0] * len(items)
        self.t = 0
        self.flash = 0

    def move(self, d, audio):
        self.sel = (self.sel + d) % len(self.items)
        audio.play('menu_mover')

    def update(self):
        self.t += 1
        self.flash = max(0, self.flash - 1)
        for i in range(len(self.items)):
            target = 1.0 if i == self.sel else 0.0
            self.anim[i] += (target - self.anim[i]) * 0.25

    def draw(self, surf):
        for i, it in enumerate(self.items):
            a = self.anim[i]
            y = self.y + i * self.spacing
            label = it if isinstance(it, str) else it[0]
            if i == self.sel:
                col_top = (255, 255, 255)
                col_bot = C.YELLOW if (self.flash // 3) % 2 == 0 else C.WHITE
                img = ui.text_gradient(label, self.size, col_top, (255, 120, 0), extrude=4)
                sc = 1.0 + 0.12 * a + 0.03 * math.sin(self.t * 0.15)
                img = pygame.transform.scale(img, (int(img.get_width() * sc), int(img.get_height() * sc)))
            else:
                img = ui.text_outline(label, self.size - 6, (170, 170, 200))
            x = self.x + 30 * a if self.align == 'left' else self.x
            if self.align == 'center':
                ui.blit_center(surf, img, x, y)
                w = img.get_width()
                if i == self.sel:
                    off = 18 + 6 * math.sin(self.t * 0.2)
                    for s in (-1, 1):
                        cx = x + s * (w / 2 + off + 10)
                        pts = [(cx - 10 * s, y - 12), (cx + 6 * s, y), (cx - 10 * s, y + 12)]
                        pygame.draw.polygon(surf, (0, 0, 0), [(p[0] + 2, p[1] + 2) for p in pts])
                        pygame.draw.polygon(surf, C.YELLOW, pts)
                    # barra luminosa
                    bar = pygame.Surface((int(w + 140 * a), 6), pygame.SRCALPHA)
                    bar.fill((255, 200, 0, int(120 * a)))
                    surf.blit(bar, (x - bar.get_width() / 2, y + img.get_height() / 2 + 2))
            else:
                surf.blit(img, (x, y - img.get_height() / 2))
