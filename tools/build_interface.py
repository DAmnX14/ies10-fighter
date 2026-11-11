"""
Genera el logotipo original «IES 10 FIGHTER» y el ícono de la ventana.
Uso: python tools/build_interface.py
"""
import os
import sys
import math
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
import pygame
pygame.init()
import config as C
from game import ui

OUT = os.path.join(ROOT, 'assets', 'interface')


def bolt(surf, x, y, s, col, outline=(30, 0, 10)):
    pts = [(0, 0), (40, 0), (22, 38), (46, 38), (-6, 110), (8, 56), (-14, 56)]
    P = [(x + px * s, y + py * s) for px, py in pts]
    pygame.draw.polygon(surf, outline, P, 0)
    P2 = [(x + px * s * 0.86 + 3 * s, y + py * s * 0.9 + 5 * s) for px, py in pts]
    pygame.draw.polygon(surf, col, P2, 0)


def make_logo():
    W, H = 1100, 420
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    # emblema: escudo con «10»
    shield = [(cx - 120, 30), (cx + 120, 30), (cx + 120, 170), (cx, 250), (cx - 120, 170)]
    pygame.draw.polygon(s, (10, 10, 30), [(x + (6 if x > cx else -6 if x < cx else 0), y + (6 if y > 100 else -6))
                                           for x, y in shield])
    pygame.draw.polygon(s, (25, 60, 160), shield)
    inner = [(cx - 100, 46), (cx + 100, 46), (cx + 100, 160), (cx, 228), (cx - 100, 160)]
    pygame.draw.polygon(s, (40, 110, 220), inner)
    st = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(0, 420, 14):
        pygame.draw.line(st, (60, 140, 240, 255), (cx - 100, 46 + i), (cx - 100 + i, 46), 2)
    m = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(m, (255, 255, 255, 255), inner)
    st.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(st, (0, 0))
    pygame.draw.polygon(s, (255, 214, 10), shield, 6)
    bolt(s, cx - 230, 40, 1.2, (255, 214, 10))
    bolt(s, cx + 200, 40, 1.2, (255, 214, 10))
    ten = ui.text_gradient('10', 120, (255, 255, 230), (255, 140, 0), (30, 0, 10), extrude=8)
    s.blit(ten, (cx - ten.get_width() // 2 + 6, 70))
    ies = ui.text_gradient('IES', 40, (255, 255, 255), (170, 210, 255), (10, 10, 40), extrude=3)
    s.blit(ies, (cx - ies.get_width() // 2, 14))
    # «FIGHTER» con cromado y perspectiva (cizalla)
    fi = ui.text_gradient('FIGHTER', 104, (255, 255, 255), (220, 30, 40), (20, 0, 10), extrude=10,
                          extrude_color=(110, 0, 20))
    sh = pygame.Surface((fi.get_width() + 80, fi.get_height()), pygame.SRCALPHA)
    for y in range(fi.get_height()):
        off = int((fi.get_height() - y) * 0.35)
        sh.blit(fi, (off, y), (0, y, fi.get_width(), 1))
    s.blit(sh, (cx - sh.get_width() // 2, 238))
    # destellos
    for (x, y, r) in ((cx - 380, 260, 18), (cx + 400, 330, 14), (cx + 110, 40, 12)):
        for a in range(4):
            ang = a * math.pi / 2
            pygame.draw.line(s, (255, 255, 255), (x, y), (x + math.cos(ang) * r, y + math.sin(ang) * r), 3)
        pygame.draw.circle(s, (255, 255, 200), (x, y), 4)
    r = s.get_bounding_rect()
    return s.subsurface(r).copy()


def make_icon():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    shield = [(4, 4), (60, 4), (60, 38), (32, 60), (4, 38)]
    pygame.draw.polygon(s, (25, 60, 160), shield)
    pygame.draw.polygon(s, (255, 214, 10), shield, 4)
    t = ui.text_outline('10', 20, (255, 214, 10), (40, 0, 0), 2, False)
    s.blit(t, (32 - t.get_width() // 2, 16))
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    pygame.image.save(make_logo(), os.path.join(OUT, 'logo.png'))
    pygame.image.save(make_icon(), os.path.join(OUT, 'icono.png'))
    vs = ui.text_gradient('VS', 130, (255, 255, 255), C.RED, extrude=10)
    pygame.image.save(vs, os.path.join(OUT, 'vs.png'))
    print('interfaz generada')


if __name__ == '__main__':
    main()
