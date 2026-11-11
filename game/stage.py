"""Escenario: el aula del IES 10 (escenario.jpg) con iluminación, ambiente y profundidad."""
import math
import random
import pygame
import config as C


class Stage:
    def __init__(self):
        raw = pygame.image.load(C.BG_PATH).convert()
        k = C.STAGE_HEIGHT / raw.get_height()          # misma escala en X e Y: no se deforma
        self.k = k
        self.w = int(raw.get_width() * k)
        self.h = C.STAGE_HEIGHT
        self.bg = pygame.transform.smoothscale(raw, (self.w, self.h))
        self.ground_y = int(C.GROUND_SRC_Y * k)
        self.left = 150
        self.right = self.w - 150
        self.t = 0
        self.flicker = 0
        # motas de polvo en la luz
        self.motes = [[random.uniform(0, self.w), random.uniform(80, self.ground_y), random.uniform(0.1, 0.4),
                       random.uniform(0, 6.28)] for _ in range(70)]
        self._make_overlays()
        self.dim = 0.0

    def _make_overlays(self):
        W, H = C.WIDTH, C.HEIGHT
        # viñeta
        self.vignette = pygame.Surface((W, H), pygame.SRCALPHA)
        for i in range(60):
            a = int(150 * (i / 60) ** 2.2)
            pygame.draw.rect(self.vignette, (0, 0, 0, a), (i * 3 - 180 + 180, 0, 0, 0))
        steps = 40
        for i in range(steps):
            a = int(110 * (1 - i / steps) ** 2)
            pygame.draw.rect(self.vignette, (0, 0, 0, a), (i * 4, i * 2, W - i * 8, H - i * 4), 4)
        # luz cenital sobre el piso (pool)
        self.pool = pygame.Surface((900, 200))
        self.pool.fill((0, 0, 0))
        for i in range(30):
            r = 1 - i / 30
            v = int(1.2 * i)
            pygame.draw.ellipse(self.pool, (v, v, int(v * 0.85)),
                                (450 - 450 * r, 100 - 100 * r, 900 * r, 200 * r))
        # haces de luz desde las ventanas/puerta
        self.shaft = pygame.Surface((self.w, self.h))
        self.shaft.fill((0, 0, 0))
        for i, x in enumerate((self.w * 0.38, self.w * 0.47, self.w * 0.56)):
            pygame.draw.polygon(self.shaft, (16, 15, 12), [(x, 0), (x + 70, 0), (x + 260, self.ground_y),
                                                                  (x + 120, self.ground_y)])
        # siluetas de primer plano (público borroso) para dar profundidad
        self.fg = pygame.Surface((self.w + 600, 170), pygame.SRCALPHA)
        rnd = random.Random(7)
        x = -40
        while x < self.w + 600:
            if rnd.random() < 0.62:
                hx = x + rnd.randint(0, 30)
                hr = rnd.randint(34, 50)
                col = (10, 14, 18, 235)
                pygame.draw.ellipse(self.fg, col, (hx - hr * 1.7, 170 - hr * 1.6, hr * 3.4, hr * 2.4))
                pygame.draw.circle(self.fg, col, (hx, 170 - hr * 1.9), hr)
                if rnd.random() < 0.35:   # brazo levantado
                    pygame.draw.line(self.fg, col, (hx + hr, 170 - hr * 1.3), (hx + hr * 1.6, 170 - hr * 3.0), 16)
                    pygame.draw.circle(self.fg, col, (int(hx + hr * 1.6), int(170 - hr * 3.0)), 11)
                x += rnd.randint(220, 420)
            else:
                x += rnd.randint(120, 260)
        self.fg = pygame.transform.smoothscale(pygame.transform.smoothscale(self.fg, (self.fg.get_width() // 4, 42)),
                                               self.fg.get_size())

    def update(self):
        self.t += 1
        if self.flicker > 0:
            self.flicker -= 1
        elif random.random() < 0.004:
            self.flicker = random.randint(4, 14)
        for m in self.motes:
            m[3] += 0.02
            m[0] += math.sin(m[3]) * 0.3
            m[1] -= m[2]
            if m[1] < 60:
                m[1] = self.ground_y; m[0] = random.uniform(0, self.w)

    def draw_back(self, surf, cam):
        ox, oy = cam.to_screen(0, 0)
        surf.blit(self.bg, (ox, oy))
        surf.blit(self.shaft, (ox, oy), special_flags=pygame.BLEND_RGB_ADD)
        # destello de tubo fluorescente
        if self.flicker > 0 and (self.flicker // 2) % 2 == 0:
            s = pygame.Surface((C.WIDTH, int(C.HEIGHT * 0.55)), pygame.SRCALPHA)
            s.fill((0, 0, 0, 55))
            surf.blit(s, (0, 0))
        for m in self.motes:
            x, y = cam.to_screen(m[0], m[1])
            if -5 < x < C.WIDTH + 5:
                a = 120 + int(80 * math.sin(m[3] * 3))
                pygame.draw.rect(surf, (255, 250, 220), (x, y, 2, 2)) if a > 140 else None
        px, py = cam.to_screen(cam.x + C.WIDTH / 2, self.ground_y)
        surf.blit(self.pool, (px - 450, py - 120), special_flags=pygame.BLEND_RGB_ADD)
        if self.dim > 0.01:
            s = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 10, int(200 * self.dim)))
            surf.blit(s, (0, 0))

    def draw_shadow(self, surf, cam, x, y, scale=1.0):
        h = self.ground_y - y
        k = max(0.35, 1 - h / 500) * scale
        w, hh = int(170 * k), int(30 * k)
        sx, sy = cam.to_screen(x, self.ground_y)
        s = pygame.Surface((w, hh), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, int(120 * k)), (0, 0, w, hh))
        surf.blit(s, (sx - w // 2, sy - hh // 2))

    def draw_front(self, surf, cam):
        # primer plano con paralaje (se mueve más rápido que el fondo)
        fx = -cam.x * 1.35 - 150 + cam.ox
        surf.blit(self.fg, (fx, C.HEIGHT - 150 + cam.oy * 1.3 + (cam.base_y - cam.y) * 0.3))
        surf.blit(self.vignette, (0, 0))
