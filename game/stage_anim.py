"""Fondos animados: se animan partes de la imagen fija de cada escenario.

Técnicas (estilo fondos de juegos de pelea arcade, sin imágenes nuevas):
- PÚBLICO: la zona de cada grupo se corta en columnas (≈ una por persona) y la parte de
  arriba (cabezas, brazos, torso) sube y baja con su propio ritmo. Cuando hay golpes
  fuertes o un K.O. el público se agita más (Stage.excite).
- BANDERAS: ondulan desplazando cada columna con una onda que crece lejos del mástil.
- LUCES: brillo aditivo que respira, con algún parpadeo ocasional.
- AGUA: chorros y destellos en la fuente de la plaza.
- PÁJAROS: siluetas que cruzan el cielo del patio al atardecer.
Las coordenadas están en px del escenario ya escalado (las mismas del mundo del juego).
"""
import math
import random
import pygame

# grupos de público: (x0, y0, x1, y1, ancho de columna, amplitud px, velocidad)
STAGE_ANIM = {
    'aula': dict(
        crowd=[(25, 355, 505, 525, 62, 3, 1.0),          # alumnos a la izquierda (sobre los bancos)
               (632, 355, 690, 440, 58, 2, 0.8),         # la que se asoma en la puerta
               (882, 350, 942, 470, 60, 2, 0.9),         # el que se asoma del otro lado
               (972, 250, 1470, 525, 70, 3, 1.1)],       # alumnos a la derecha
        lights=[], flags=[], fountain=None, birds=False),
    'plaza': dict(
        crowd=[(0, 635, 250, 760, 58, 3, 1.1),
               (1160, 640, 1315, 760, 52, 3, 1.0)],
        lights=[(323, 455, 18)],
        flags=[(368, 362, 398, 398), (418, 362, 448, 400), (496, 362, 526, 402), (544, 364, 574, 402),
               (608, 366, 638, 402), (828, 362, 858, 398), (904, 364, 934, 400), (956, 366, 986, 400),
               (1010, 368, 1040, 402), (1050, 368, 1080, 402), (1126, 366, 1158, 402)],
        fountain=dict(jets=[(560, 655), (650, 640), (745, 655)], water=(410, 690, 990, 770)), birds=False),
    'gloriosa': dict(
        crowd=[(0, 355, 350, 560, 70, 3, 1.2),           # hinchas de adelante a la izquierda
               (282, 352, 548, 420, 30, 2, 1.3),         # fila del fondo a la izquierda
               (1040, 340, 1430, 422, 32, 2, 1.3)],      # fila del fondo a la derecha
        lights=[(515, 125, 34), (710, 105, 40), (752, 180, 30), (870, 113, 26), (992, 130, 30),
                (1140, 172, 30), (1250, 75, 34)],
        flags=[], fountain=None, birds=False),
    'patio': dict(
        crowd=[(20, 372, 190, 455, 42, 2, 1.0),
               (290, 352, 490, 405, 40, 2, 0.9),
               (868, 345, 920, 410, 52, 2, 1.0),
               (1120, 352, 1165, 410, 45, 2, 1.0),
               (1280, 375, 1418, 455, 46, 3, 1.1)],
        lights=[(888, 232, 60), (1168, 268, 22), (406, 290, 18)],
        flags=[(578, 70, 598, 140, 'pole_left'), (1226, 330, 1282, 366, 'wall')],
        fountain=None, birds=True),
}


def _glow(radius, color):
    s = pygame.Surface((radius * 2, radius * 2))
    s.fill((0, 0, 0))
    for i in range(radius, 0, -1):
        k = (1 - i / radius) ** 2
        pygame.draw.circle(s, tuple(int(c * k) for c in color), (radius, radius), i)
    return s


class StageAnimator:
    def __init__(self, stage):
        self.stage = stage
        cfg = STAGE_ANIM.get(stage.id, {})
        bg = stage.bg
        rnd = random.Random(hash(stage.id) & 0xffff)
        self.excitement = 0.0
        self.t = 0
        # público: columnas recortadas del fondo
        self.cols = []
        for (x0, y0, x1, y1, cw, amp, spd) in cfg.get('crowd', []):
            x = x0
            while x < x1:
                w = min(cw, x1 - x)
                rect = pygame.Rect(x, y0, w, y1 - y0)
                rect = rect.clip(bg.get_rect())
                if rect.w > 2 and rect.h > 2:
                    self.cols.append(dict(img=bg.subsurface(rect).copy(), x=rect.x, y=rect.y, amp=amp,
                                          spd=spd * rnd.uniform(0.75, 1.3), ph=rnd.uniform(0, 6.283),
                                          jump=rnd.random() < 0.45))
                x += w
        # banderas
        self.flags = []
        for f in cfg.get('flags', []):
            x0, y0, x1, y1 = f[:4]
            kind = f[4] if len(f) > 4 else 'pole_left'
            rect = pygame.Rect(x0, y0, x1 - x0, y1 - y0).clip(bg.get_rect())
            img = bg.subsurface(rect).copy()
            self.flags.append(dict(img=img, x=rect.x, y=rect.y, kind=kind, ph=rnd.uniform(0, 6.283)))
        # luces
        warm = (255, 235, 180) if stage.id != 'gloriosa' else (210, 230, 255)
        self.lights = [dict(x=x, y=y, levels=[_glow(r, tuple(int(c * k) for c in warm)) for k in
                                              (0.20, 0.30, 0.40, 0.50)], ph=rnd.uniform(0, 6.283), r=r)
                       for (x, y, r) in cfg.get('lights', [])]
        self.flick = {}
        self.fountain = cfg.get('fountain')
        self.drops = []
        self.birds = [] if cfg.get('birds') else None

    def excite(self, amount):
        self.excitement = min(3.0, self.excitement + amount)

    def update(self):
        self.t += 1
        self.excitement *= 0.985
        if self.fountain:
            for (jx, jy) in self.fountain['jets']:
                for _ in range(2):
                    self.drops.append([jx + random.uniform(-4, 4), jy, random.uniform(-1.2, 1.2),
                                       random.uniform(-4.2, -3.0), 40])
            for d in self.drops:
                d[0] += d[2]; d[1] += d[3]; d[3] += 0.18; d[4] -= 1
            wy = self.fountain['water'][1] + 8
            self.drops = [d for d in self.drops if d[4] > 0 and d[1] < wy]
        if self.birds is not None:
            if random.random() < 0.006 and len(self.birds) < 4:
                self.birds.append([-20.0, random.uniform(25, 130), random.uniform(0.8, 1.6), random.uniform(0, 6)])
            for b in self.birds:
                b[0] += b[2]; b[3] += 0.25
            self.birds = [b for b in self.birds if b[0] < self.stage.w + 30]
        for i in range(len(self.lights)):
            if self.flick.get(i, 0) > 0:
                self.flick[i] -= 1
            elif random.random() < 0.002:
                self.flick[i] = random.randint(3, 9)

    def draw(self, surf, ox, oy):
        t = self.t
        W, H = surf.get_size()
        ex = 1.0 + self.excitement
        # público
        for c in self.cols:
            sx = ox + c['x']
            if sx > W or sx + c['img'].get_width() < 0:
                continue
            s = math.sin(t * 0.09 * c['spd'] * (1 + 0.35 * self.excitement) + c['ph'])
            if c['jump']:
                dy = -c['amp'] * ex * max(0.0, s)              # salta
            else:
                dy = -c['amp'] * 0.6 * ex * (s * 0.5 + 0.5)    # se balancea
            if abs(dy) >= 0.5:
                surf.blit(c['img'], (sx, oy + c['y'] + round(dy)))
        # banderas
        for f in self.flags:
            img = f['img']
            w, h = img.get_size()
            for x in range(w):
                k = x / max(1, w - 1) if f['kind'] == 'pole_left' else 0.5
                dy = math.sin(t * 0.16 - x * 0.35 + f['ph']) * (0.6 + 2.6 * k)
                surf.blit(img, (ox + f['x'] + x, oy + f['y'] + round(dy)), (x, 0, 1, h))
        # luces
        for i, L in enumerate(self.lights):
            if self.flick.get(i, 0) and (self.flick[i] // 2) % 2:
                continue
            lv = int((math.sin(t * 0.05 + L['ph']) * 0.5 + 0.5) * (len(L['levels']) - 1) + 0.5)
            g = L['levels'][lv]
            surf.blit(g, (ox + L['x'] - L['r'], oy + L['y'] - L['r']), special_flags=pygame.BLEND_RGB_ADD)
        # fuente
        if self.fountain:
            for d in self.drops:
                pygame.draw.rect(surf, (200, 235, 255), (ox + d[0], oy + d[1], 2, 2))
            x0, y0, x1, y1 = self.fountain['water']
            rnd = random.Random(t // 6)
            for _ in range(14):
                px, py = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
                pygame.draw.rect(surf, (235, 250, 255), (ox + px, oy + py, 2, 1))
        # pájaros
        if self.birds:
            for b in self.birds:
                x, y = ox + b[0], oy + b[1]
                wing = 3 * math.sin(b[3])
                pygame.draw.lines(surf, (30, 20, 40), False, [(x - 5, y - wing), (x, y), (x + 5, y - wing)], 2)
