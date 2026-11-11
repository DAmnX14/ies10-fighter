"""Partículas, efectos con sprites, anillos de impacto y textos flotantes."""
import math
import random
import pygame
from game import assets


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'g', 'life', 'max', 'color', 'size', 'shape', 'drag')

    def __init__(self, x, y, vx, vy, color, life=30, size=6, g=0.35, shape='sq', drag=0.98):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.color, self.life, self.max, self.size, self.g = color, life, life, size, g
        self.shape, self.drag = shape, drag

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += self.g; self.vx *= self.drag
        self.life -= 1
        return self.life > 0

    def draw(self, surf, cam):
        k = self.life / self.max
        s = max(1, int(self.size * (0.4 + 0.6 * k)))
        x, y = cam.to_screen(self.x, self.y)
        if self.shape == 'sq':
            pygame.draw.rect(surf, self.color, (x - s // 2, y - s // 2, s, s))
        elif self.shape == 'line':
            pygame.draw.line(surf, self.color, (x, y), (x - self.vx * 2.5, y - self.vy * 2.5), max(1, s // 2))
        else:
            pygame.draw.circle(surf, self.color, (int(x), int(y)), s)


class SpriteFX:
    def __init__(self, name, x, y, facing=1, tint=None, follow=None, scale=1.0, loops=1, alpha=255,
                 additive=False, offset=(0, 0)):
        fx = assets.effects()
        self.frames = fx.tinted(name, tint) if tint else fx.frames[name]
        self.dur = fx.meta[name]['dur']
        self.x, self.y, self.facing = x, y, facing
        self.t = 0
        self.follow = follow
        self.offset = offset
        self.total = len(self.frames) * self.dur * loops
        self.scale = scale
        self.alpha = alpha
        self.additive = additive

    def update(self):
        self.t += 1
        if self.follow is not None:
            self.x = self.follow.x + self.offset[0] * self.follow.facing
            self.y = self.follow.y + self.offset[1]
        return self.t < self.total

    def draw(self, surf, cam):
        i = (self.t // self.dur) % len(self.frames)
        img = self.frames[i]
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        if self.scale != 1.0:
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
        if self.alpha < 255:
            img = img.copy(); img.set_alpha(self.alpha)
        x, y = cam.to_screen(self.x, self.y)
        surf.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))


class Ring:
    def __init__(self, x, y, color, r0=10, r1=160, life=18, width=8):
        self.x, self.y, self.color = x, y, color
        self.r0, self.r1, self.life, self.max, self.width = r0, r1, life, life, width

    def update(self):
        self.life -= 1
        return self.life > 0

    def draw(self, surf, cam):
        k = 1 - self.life / self.max
        r = self.r0 + (self.r1 - self.r0) * (1 - (1 - k) ** 2)
        x, y = cam.to_screen(self.x, self.y)
        w = max(1, int(self.width * (1 - k)) + 1)
        pygame.draw.circle(surf, self.color, (int(x), int(y)), int(r), w)


class SpeedLines:
    """Líneas de velocidad radiales (efecto de pantalla en ultimates)."""

    def __init__(self, cx, cy, color=(255, 255, 255), life=40):
        self.cx, self.cy, self.color, self.life = cx, cy, color, life

    def update(self):
        self.life -= 1
        return self.life > 0

    def draw(self, surf, cam):
        x, y = cam.to_screen(self.cx, self.cy)
        for _ in range(26):
            a = random.uniform(0, math.tau)
            r0 = random.uniform(260, 420)
            r1 = r0 + random.uniform(200, 600)
            pygame.draw.line(surf, self.color, (x + math.cos(a) * r0, y + math.sin(a) * r0),
                             (x + math.cos(a) * r1, y + math.sin(a) * r1), random.choice((2, 3, 4)))


class FloatText:
    def __init__(self, x, y, text, color, size=18, life=50):
        self.x, self.y, self.text, self.color, self.size, self.life, self.max = x, y, text, color, size, life, life

    def update(self):
        self.life -= 1
        self.y -= 1.2
        return self.life > 0

    def draw(self, surf, cam):
        from game.ui import text_outline
        x, y = cam.to_screen(self.x, self.y)
        img = text_outline(self.text, self.size, self.color)
        if self.life < 15:
            img.set_alpha(int(255 * self.life / 15))
        surf.blit(img, (x - img.get_width() // 2, y))


class FXManager:
    def __init__(self):
        self.back = []     # detrás de los luchadores
        self.front = []    # delante

    def add(self, e, front=True):
        (self.front if front else self.back).append(e)

    def burst(self, x, y, color, n=16, speed=9, size=7, g=0.4, shape='sq', life=28):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = random.uniform(speed * 0.3, speed)
            self.front.append(Particle(x, y, math.cos(a) * v, math.sin(a) * v - 2, color,
                                       random.randint(life // 2, life), size, g, shape))

    def sparks(self, x, y, facing, color, n=10):
        for _ in range(n):
            a = random.uniform(-0.9, 0.9) + (0 if facing > 0 else math.pi)
            v = random.uniform(6, 16)
            self.front.append(Particle(x, y, math.cos(a) * v, math.sin(a) * v, color,
                                       random.randint(10, 18), 6, 0.2, 'line', 0.9))

    def dust(self, x, y, n=1):
        self.back.append(SpriteFX('polvo', x, y - 30))
        for _ in range(6 * n):
            self.back.append(Particle(x + random.uniform(-40, 40), y - 5, random.uniform(-3, 3),
                                      random.uniform(-3, -0.5), (190, 175, 150), 26, 7, 0.08))

    def update(self):
        self.back = [e for e in self.back if e.update()]
        self.front = [e for e in self.front if e.update()]

    def draw_back(self, surf, cam):
        for e in self.back:
            e.draw(surf, cam)

    def draw_front(self, surf, cam):
        for e in self.front:
            e.draw(surf, cam)
