"""Cinemática de apertura original: Pantoja vs Parada y aparición del logo."""
import math
import random
import pygame
import config as C
from game import assets, ui
from screens.common import Scene, nav, logo, draw_fighter, AnimPlayer, menu_background

# línea de tiempo (ticks a 60 fps)
T_PRESENTS = 0
T_PANTOJA = 150
T_PARADA = 320
T_EYES = 490
T_STAGE = 650
T_CLASH = 860
T_LOGO = 900
T_END = 1130


class IntroScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.audio = game.audio
        self.audio.music('musica_intro', loop=False, fade=0)
        self.pan = AnimPlayer('pantoja', 'idle')
        self.par = AnimPlayer('parada', 'idle')
        self.sparks = []
        self.shake = 0
        self.flash = 0
        self.fired = set()
        self.stage = None

    def once(self, key):
        if key in self.fired:
            return False
        self.fired.add(key)
        return True

    def handle_event(self, e):
        if nav(e) in ('ok', 'back'):
            self.finish()

    def finish(self):
        from screens.main_menu import TitleScene
        self.game.change(lambda: TitleScene(self.game))

    def update(self):
        super().update()
        t = self.t
        A = self.audio
        if t == 20:
            A.play('moneda')
        if t == T_PANTOJA and self.once('p'):
            A.play('golpe_fuerte'); A.announce('loc_pantoja'); self.flash = 8; self.shake = 14
            self.pan.set('presentacion', False, 'idle')
        if t == T_PARADA and self.once('q'):
            A.play('golpe_fuerte'); A.announce('loc_parada'); self.flash = 8; self.shake = 14
            self.par.set('presentacion', False, 'idle')
        if t == T_EYES and self.once('e'):
            A.play('ultimate_activar'); self.flash = 6
        if t == T_EYES + 80 and self.once('vs'):
            A.play('ko_impacto'); self.shake = 20
        if t == T_STAGE and self.once('s'):
            A.play('publico', 0.7)
            self.pan.set('presentacion', False, 'idle'); self.par.set('presentacion', False, 'idle')
        if t == T_STAGE + 150 and self.once('j'):
            A.play('salto'); A.voice('pantoja', 'grito_2'); A.voice('parada', 'grito_1')
            self.pan.set('saltar_adelante', False, None); self.par.set('saltar_adelante', False, None)
        if t == T_CLASH and self.once('c'):
            A.play('explosion'); A.play('golpe_fuerte'); self.flash = 30; self.shake = 30
        if t == T_LOGO + 30 and self.once('l'):
            A.play('ko_impacto'); A.announce('loc_titulo'); self.shake = 26
            for _ in range(80):
                a = random.uniform(0, math.tau); v = random.uniform(4, 18)
                self.sparks.append([C.WIDTH / 2, C.HEIGHT / 2 - 40, math.cos(a) * v, math.sin(a) * v,
                                    random.randint(30, 70), random.choice([C.YELLOW, C.ORANGE, C.WHITE, (255, 80, 160)])])
        if t >= T_END:
            self.finish()
        self.pan.update(); self.par.update()
        self.shake = max(0, self.shake - 1)
        self.flash = max(0, self.flash - 1)
        for s in self.sparks:
            s[0] += s[2]; s[1] += s[3]; s[3] += 0.25; s[4] -= 1
        self.sparks = [s for s in self.sparks if s[4] > 0]

    # ------------------------------------------------------------- escenas
    def speed_bg(self, surf, color, direction):
        surf.fill(tuple(c // 5 for c in color))
        for i in range(40):
            y = (i * 37 + self.t * 3) % C.HEIGHT
            L = 200 + (i * 53) % 400
            x = (self.t * 40 * direction + i * 211) % (C.WIDTH + L) - L
            pygame.draw.line(surf, tuple(min(255, c // 2 + 40) for c in color), (x, y), (x + L, y), 2 + i % 4)

    def name_slam(self, surf, txt, sub, color, t0, side):
        k = min(1.0, (self.t - t0) / 10)
        img = ui.text_gradient(txt, 86, (255, 255, 255), color, extrude=8)
        sc = 3 - 2 * k
        im = pygame.transform.scale(img, (int(img.get_width() * sc), int(img.get_height() * sc)))
        x = C.WIDTH * (0.68 if side > 0 else 0.32)
        ui.blit_center(surf, im, x, 300)
        if self.t - t0 > 18:
            s = ui.text_outline(sub, 22, C.YELLOW)
            ui.blit_center(surf, s, x, 390)
            q = ui.text_outline('“' + {'PANTOJA': 'Te paso por arriba como un colectivo',
                                       'PARADA': 'Nadie me ve venir'}[txt] + '”', 14, C.WHITE)
            ui.blit_center(surf, q, x, 440)

    def draw(self, surf):
        t = self.t
        canvas = surf
        if t < T_PANTOJA:
            surf.fill((0, 0, 0))
            a = min(255, t * 6) if t < 110 else max(0, 255 - (t - 110) * 7)
            from screens.common import arcetech_logo
            lg0 = pygame.transform.scale(arcetech_logo(), (arcetech_logo().get_width() * 2, arcetech_logo().get_height() * 2))
            lg0.set_alpha(min(255, t * 6) if t < 110 else max(0, 255 - (t - 110) * 7))
            ui.blit_center(surf, lg0, C.WIDTH / 2, C.HEIGHT / 2 - 110)
            img = ui.text_outline('ARCE TECH PRESENTA', 26, (230, 255, 235))
            img.set_alpha(a)
            ui.blit_center(surf, img, C.WIDTH / 2, C.HEIGHT / 2)
            img2 = ui.text('UN JUEGO DEL IES N.º 10', 12, (150, 150, 190))
            img2.set_alpha(a)
            ui.blit_center(surf, img2, C.WIDTH / 2, C.HEIGHT / 2 + 50)
        elif t < T_PARADA:
            self.speed_bg(surf, (255, 70, 160), 1)
            k = min(1.0, (t - T_PANTOJA) / 14)
            x = -200 + 520 * k
            self.pan.draw(surf, x, 690, 1, 5, glow=(255, 70, 160))
            self.name_slam(surf, 'PANTOJA', 'EL MARIDO DE PARADA', (255, 70, 160), T_PANTOJA, 1)
        elif t < T_EYES:
            self.speed_bg(surf, (40, 210, 110), -1)
            k = min(1.0, (t - T_PARADA) / 14)
            x = C.WIDTH + 200 - 520 * k
            self.par.draw(surf, x, 690, -1, 5, glow=(40, 210, 110))
            self.name_slam(surf, 'PARADA', 'EL BESA PERRO', (40, 210, 110), T_PARADA, -1)
        elif t < T_STAGE:
            self.draw_eyes(surf, t - T_EYES)
        elif t < T_LOGO:
            self.draw_stage(surf, t - T_STAGE)
        else:
            self.draw_logo(surf, t - T_LOGO)
        # sacudida y destello
        if self.shake:
            cp = surf.copy()
            surf.fill((0, 0, 0))
            surf.blit(cp, (random.randint(-self.shake, self.shake), random.randint(-self.shake, self.shake)))
        if self.flash:
            s = pygame.Surface((C.WIDTH, C.HEIGHT)); s.fill((255, 255, 255)); s.set_alpha(min(255, self.flash * 25))
            surf.blit(s, (0, 0))
        # bandas de cine
        if T_PANTOJA <= t < T_LOGO:
            pygame.draw.rect(surf, (0, 0, 0), (0, 0, C.WIDTH, 60))
            pygame.draw.rect(surf, (0, 0, 0), (0, C.HEIGHT - 60, C.WIDTH, 60))
        sk = ui.text('ENTER: SALTAR', 10, (120, 120, 140))
        surf.blit(sk, (C.WIDTH - sk.get_width() - 16, C.HEIGHT - 26))

    def draw_eyes(self, surf, lt):
        surf.fill((0, 0, 0))
        k = min(1.0, lt / 16)
        for i, (name, col, side) in enumerate((('pantoja', (255, 70, 160), 1), ('parada', (40, 210, 110), -1))):
            por = assets.character(name).portrait
            h = 72
            band = por.subsurface((0, int(h * 0.30), 72, int(h * 0.26)))   # franja de los ojos
            img = pygame.transform.scale(band, (C.WIDTH // 2 + 300, int((C.WIDTH // 2 + 300) * band.get_height() / 72)))
            if side < 0:
                img = pygame.transform.flip(img, True, False)
            y = 90 + i * 280
            x = (-C.WIDTH + (C.WIDTH * 0.9) * k) if side > 0 else (C.WIDTH - (C.WIDTH * 0.9) * k + 300 - 300)
            x += lt * 0.6 * side
            clip = pygame.Rect(0, y, C.WIDTH, 250)
            surf.set_clip(clip)
            surf.blit(img, (x if side > 0 else x, y + 125 - img.get_height() / 2))
            surf.set_clip(None)
            pygame.draw.rect(surf, col, (0, y - 4, C.WIDTH, 4)); pygame.draw.rect(surf, col, (0, y + 250, C.WIDTH, 4))
        if lt > 80:
            kk = min(1.0, (lt - 80) / 8)
            vs = ui.text_gradient('VS', 120, (255, 255, 255), C.RED, extrude=10)
            sc = 2.5 - 1.5 * kk
            vs = pygame.transform.scale(vs, (int(vs.get_width() * sc), int(vs.get_height() * sc)))
            ui.blit_center(surf, vs, C.WIDTH / 2, C.HEIGHT / 2)
            # rayo
            pts = [(C.WIDTH / 2 + random.randint(-30, 30), y) for y in range(60, C.HEIGHT - 60, 40)]
            pygame.draw.lines(surf, (255, 255, 200), False, pts, 4)

    def draw_stage(self, surf, lt):
        menu_background(surf, self.t, (60, 20, 60))
        ground = 650
        k = min(1.0, lt / 30)
        if lt < 150:
            x1 = 260 + 80 * k; x2 = C.WIDTH - 260 - 80 * k
            y1 = y2 = ground
        else:
            j = (lt - 150) / 60.0
            x1 = 340 + (C.WIDTH / 2 - 380) * j
            x2 = C.WIDTH - 340 - (C.WIDTH / 2 - 380) * j
            y1 = y2 = ground - math.sin(min(1, j) * math.pi) * 260
        for (x, y, c) in ((x1, ground, (0, 0, 0)), (x2, ground, (0, 0, 0))):
            pygame.draw.ellipse(surf, (0, 0, 0), (x - 80, ground - 12, 160, 24))
        self.pan.draw(surf, x1, y1, 1, 3)
        self.par.draw(surf, x2, y2, -1, 3)
        if lt < 150:
            txt = ui.text_outline('EN EL AULA DEL IES 10... SÓLO UNO QUEDARÁ EN PIE', 16, C.WHITE)
            txt.set_alpha(min(255, lt * 8))
            ui.blit_center(surf, txt, C.WIDTH / 2, 110)
        if 180 < lt:
            pygame.draw.line(surf, (255, 255, 255), (C.WIDTH / 2 - 400, C.HEIGHT / 2), (C.WIDTH / 2 + 400, C.HEIGHT / 2), 2)

    def draw_logo(self, surf, lt):
        surf.fill((6, 4, 18))
        # rayos de luz giratorios
        cx, cy = C.WIDTH / 2, C.HEIGHT / 2 - 40
        s = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
        for i in range(16):
            a = i * math.tau / 16 + lt * 0.01
            pygame.draw.polygon(s, (255, 180, 40, 28), [(cx, cy), (cx + math.cos(a) * 1200, cy + math.sin(a) * 1200),
                                                        (cx + math.cos(a + 0.12) * 1200, cy + math.sin(a + 0.12) * 1200)])
        surf.blit(s, (0, 0))
        lg = logo()
        if lt < 30:
            k = 0
            surf.blit(pygame.Surface((1, 1)), (0, 0))
        else:
            k = min(1.0, (lt - 30) / 10)
            sc = 3.0 - 2.0 * k
            im = pygame.transform.scale(lg, (int(lg.get_width() * sc), int(lg.get_height() * sc)))
            ui.blit_center(surf, im, cx, cy)
        for sp in self.sparks:
            pygame.draw.rect(surf, sp[5], (sp[0], sp[1], 5, 5))
        if lt > 70:
            c = ui.text('© 2026 ARCE TECH - IES N.º 10', 12, (180, 180, 210))
            ui.blit_center(surf, c, cx, C.HEIGHT - 70)
