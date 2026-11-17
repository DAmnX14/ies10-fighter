"""Selección de personajes: «ELEGÍ A TU PELOTUDO»."""
import math
import random
import pygame
import config as C
from game import assets, ui
from game.characters_data import CHARACTERS
from screens.common import Scene, menu_background, help_bar, AnimPlayer

STAT_LABELS = [('fuerza', 'FUERZA'), ('velocidad', 'VELOCIDAD'), ('resistencia', 'RESISTENCIA'),
               ('alcance', 'ALCANCE'), ('ejecucion', 'EJECUCIÓN')]
TILE = 150
GAP = 14


class Cursor:
    def __init__(self, idx, color, label):
        self.idx = idx
        self.color = color
        self.label = label
        self.ready = False
        self.player = None
        self.flash = 0


class CharacterSelect(Scene):
    def __init__(self, game, mode):
        super().__init__(game)
        self.mode = mode                         # versus | cpu | training | arcade
        self.audio = game.audio
        self.audio.music('musica_seleccion')
        self.audio.announce('loc_elegi')
        self.c1 = Cursor(0, (255, 50, 50), '1P')
        lab2 = '2P' if mode == 'versus' else ('RIVAL' if mode == 'training' else 'CPU')
        self.c2 = Cursor(1, (40, 140, 255), lab2)
        self.active2 = mode == 'versus'          # P2 elige a la vez
        self.stage = 1                           # en cpu/training: 1 = elige P1, 2 = elige rival
        self.done_t = 0
        self.particles = []
        self.players = {}
        for n in C.CHARACTERS:
            self.players[n] = AnimPlayer(n, 'idle')
        self.side_anim = {1: AnimPlayer(C.CHARACTERS[0]), 2: AnimPlayer(C.CHARACTERS[1])}
        self.bubble = {1: None, 2: None}

    # ------------------------------------------------------------- input
    def tile_rect(self, i):
        cx = C.WIDTH / 2
        x0 = cx - TILE - GAP / 2
        y0 = 205
        if i < 3:                                    # fila de arriba: 3 retratos
            x0 = cx - 1.5 * TILE - GAP
            return pygame.Rect(x0 + i * (TILE + GAP), y0, TILE, TILE)
        return pygame.Rect(x0 + (i - 3) * (TILE + GAP), y0 + TILE + GAP, TILE, TILE)

    def move(self, cur, dx, dy):
        if cur.ready:
            return
        n = len(C.CHARACTERS)
        if dx:
            cur.idx = (cur.idx + dx) % n
        if dy:
            cur.idx = {0: 3, 1: 3, 2: 4, 3: 0, 4: 2}.get(cur.idx, 0)
        self.audio.play('menu_mover')
        side = 1 if cur is self.c1 else 2
        self.side_anim[side] = AnimPlayer(C.CHARACTERS[cur.idx])

    def confirm(self, cur):
        if cur.ready:
            return
        cur.ready = True
        cur.flash = 20
        name = C.CHARACTERS[cur.idx]
        side = 1 if cur is self.c1 else 2
        self.side_anim[side] = AnimPlayer(name, 'presentacion', False, 'idle')
        self.audio.play('seleccion')
        self.audio.announce(f'loc_{name}')
        self.bubble[side] = [CHARACTERS[name]['quote'], 160]
        r = self.tile_rect(cur.idx)
        for _ in range(40):
            a = random.uniform(0, math.tau); v = random.uniform(2, 9)
            self.particles.append([r.centerx, r.centery, math.cos(a) * v, math.sin(a) * v, 40,
                                   CHARACTERS[name]['color']])
        if self.mode in ('cpu', 'training') and cur is self.c1:
            self.stage = 2
            self.c2.idx = (self.c1.idx + 1) % len(C.CHARACTERS)
            self.side_anim[2] = AnimPlayer(C.CHARACTERS[self.c2.idx])

    def cancel(self, cur):
        if cur.ready:
            cur.ready = False
            self.audio.play('menu_atras')
            if self.mode in ('cpu', 'training') and cur is self.c1:
                self.stage = 1
            return True
        return False

    def handle_event(self, e):
        if e.type != pygame.KEYDOWN or self.done_t:
            return
        k = e.key
        p1 = self.game.settings.controls(1)
        p2 = self.game.settings.controls(2)

        def is_(keys, act):
            return k in keys[act]
        single = self.mode != 'versus'
        # ¿qué cursor controla el jugador 1?
        cur1 = self.c1 if (not single or self.stage == 1 or self.mode == 'arcade') else self.c2
        if is_(p1, 'izquierda') or (single and k == pygame.K_LEFT):
            self.move(cur1, -1, 0)
        elif is_(p1, 'derecha') or (single and k == pygame.K_RIGHT):
            self.move(cur1, 1, 0)
        elif is_(p1, 'arriba') or (single and k == pygame.K_UP):
            self.move(cur1, 0, -1)
        elif is_(p1, 'abajo') or (single and k == pygame.K_DOWN):
            self.move(cur1, 0, 1)
        elif is_(p1, 'golpe') or k == pygame.K_RETURN or (single and k in (pygame.K_SPACE, pygame.K_KP_ENTER)):
            self.confirm(cur1)
        elif k in (pygame.K_ESCAPE,) or is_(p1, 'patada'):
            if single and self.stage == 2:
                if not self.cancel(self.c2):
                    self.cancel(self.c1)
            elif not self.cancel(self.c1) and k == pygame.K_ESCAPE:
                from screens.main_menu import TitleScene
                self.audio.play('menu_atras')
                self.game.change(lambda: TitleScene(self.game, True))
        if self.mode == 'versus':
            if is_(p2, 'izquierda'):
                self.move(self.c2, -1, 0)
            elif is_(p2, 'derecha'):
                self.move(self.c2, 1, 0)
            elif is_(p2, 'arriba'):
                self.move(self.c2, 0, -1)
            elif is_(p2, 'abajo'):
                self.move(self.c2, 0, 1)
            elif is_(p2, 'golpe') or k == pygame.K_KP_ENTER:
                self.confirm(self.c2)
            elif is_(p2, 'patada'):
                self.cancel(self.c2)

    # ------------------------------------------------------------- lógica
    def all_ready(self):
        if self.mode == 'arcade':
            return self.c1.ready
        return self.c1.ready and self.c2.ready

    def update(self):
        super().update()
        for a in self.side_anim.values():
            a.update()
        for c in (self.c1, self.c2):
            c.flash = max(0, c.flash - 1)
        for p in self.particles:
            p[0] += p[2]; p[1] += p[3]; p[3] += 0.15; p[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]
        for s in (1, 2):
            if self.bubble[s]:
                self.bubble[s][1] -= 1
                if self.bubble[s][1] <= 0:
                    self.bubble[s] = None
        if self.all_ready():
            self.done_t += 1
            if self.done_t == 100:
                self.launch()

    def launch(self):
        g = self.game
        c1 = C.CHARACTERS[self.c1.idx]
        if self.mode == 'arcade':
            from screens.arcade import ArcadeRun
            run = ArcadeRun(g, c1)
            run.next_fight()
            return
        c2 = C.CHARACTERS[self.c2.idx]
        from screens.versus import VersusScreen
        mode = self.mode
        g.change(lambda: VersusScreen(g, c1, c2, mode))

    # ------------------------------------------------------------- dibujo
    def draw(self, surf):
        t = self.t
        menu_background(surf, t, (90, 20, 40))
        # título
        bounce = math.sin(t * 0.08) * 4
        title = ui.text_gradient('ELEGÍ A TU PELOTUDO', 46, (255, 255, 200), (255, 60, 0), extrude=6)
        ui.blit_center(surf, title, C.WIDTH / 2, 70 + bounce)
        mode_txt = {'versus': 'VERSUS - 2 JUGADORES', 'cpu': '1 JUGADOR VS CPU', 'training': 'ENTRENAMIENTO',
                    'arcade': 'MODO ARCADE'}[self.mode]
        ui.blit_center(surf, ui.text_outline(mode_txt, 14, C.CYAN), C.WIDTH / 2, 130)
        if self.mode in ('cpu', 'training'):
            msg = 'ELEGÍ TU LUCHADOR' if self.stage == 1 else 'ELEGÍ A TU RIVAL'
            if not self.all_ready() and (t // 20) % 2 == 0:
                ui.blit_center(surf, ui.text_outline(msg, 14, C.YELLOW), C.WIDTH / 2, 162)
        # luchadores grandes a los lados
        for side, cur in ((1, self.c1), (2, self.c2)):
            if side == 2 and self.mode == 'arcade':
                self.draw_arcade_preview(surf)
                continue
            if side == 2 and self.mode in ('cpu', 'training') and self.stage == 1:
                self.draw_unknown(surf)
                continue
            name = C.CHARACTERS[cur.idx]
            d = CHARACTERS[name]
            x = 230 if side == 1 else C.WIDTH - 230
            # foco de color
            glow = pygame.Surface((420, 500), pygame.SRCALPHA)
            for i in range(20):
                pygame.draw.ellipse(glow, d['color'] + (6,), (i * 10, i * 12, 420 - i * 20, 500 - i * 24))
            surf.blit(glow, (x - 210, 130))
            pygame.draw.ellipse(surf, (0, 0, 0), (x - 90, 655, 180, 26))
            self.side_anim[side].draw(surf, x, 668, 1 if side == 1 else -1, 2,
                                      glow=(255, 255, 255) if cur.flash and (cur.flash // 3) % 2 else None)
            # nombre y estadísticas
            nm = ui.text_gradient(d['display'], 34, (255, 255, 255), d['color'], extrude=4)
            ui.blit_center(surf, nm, x, 175)
            ui.blit_center(surf, ui.text_outline(d['title'], 12, C.YELLOW), x, 210)
            sx = 40 if side == 1 else C.WIDTH - 40 - 300
            panel_y = 236
            ui.panel(surf, (sx, panel_y, 300, 132), (0, 0, 0, 150), d['color'], 2)
            for i, (k, lab) in enumerate(STAT_LABELS):
                yy = panel_y + 12 + i * 24
                surf.blit(ui.text(lab, 10, C.WHITE), (sx + 10, yy + 2))
                ui.stat_bar(surf, sx + 140, yy, 148, 14, d['stats'][k], 10, d['color'])
            if self.bubble[side]:
                q = ui.text_outline('«' + self.bubble[side][0] + '»', 9, C.WHITE)
                bx = max(10, min(C.WIDTH - q.get_width() - 10, x - q.get_width() / 2))
                ui.panel(surf, (bx - 8, 380, q.get_width() + 16, 36), (0, 0, 0, 210), d['color'], 2)
                surf.blit(q, (bx, 388))
            if cur.ready:
                lab = ui.text_gradient('¡LISTO!', 26, (255, 255, 255), C.YELLOW, extrude=3)
                ui.blit_center(surf, lab, x, 440 + math.sin(t * 0.2) * 4)
        # grilla de retratos
        for i, n in enumerate(C.CHARACTERS):
            r = self.tile_rect(i)
            d = CHARACTERS[n]
            pygame.draw.rect(surf, (0, 0, 0), r.inflate(10, 10))
            pygame.draw.rect(surf, d['color'], r.inflate(6, 6))
            bg = pygame.Surface(r.size); bg.fill(tuple(c // 4 for c in d['color']))
            surf.blit(bg, r.topleft)
            por = pygame.transform.scale(assets.character(n).portrait, (TILE, TILE))
            surf.blit(por, r.topleft)
            lab = ui.text_outline(d['display'], 12, C.WHITE)
            surf.blit(lab, (r.centerx - lab.get_width() / 2, r.bottom - 20))
        # cursores
        for cur in (self.c1, self.c2):
            if cur is self.c2 and self.mode == 'arcade':
                continue
            if cur is self.c2 and self.mode in ('cpu', 'training') and self.stage == 1:
                continue
            r = self.tile_rect(cur.idx)
            both = self.c1.idx == self.c2.idx and not (self.mode in ('cpu', 'training') and self.stage == 1) \
                and self.mode != 'arcade'
            off = 0 if not both else (-4 if cur is self.c1 else 4)
            w = 6 if (t // 8) % 2 or cur.ready else 4
            pygame.draw.rect(surf, cur.color, r.inflate(14 + off, 14 + off), w)
            tag = ui.text_outline(cur.label, 14, cur.color)
            tx = r.left - 4 if cur is self.c1 else r.right - tag.get_width() + 4
            surf.blit(tag, (tx, r.top - 26))
            if cur.flash:
                s = pygame.Surface(r.size, pygame.SRCALPHA); s.fill((255, 255, 255, cur.flash * 10))
                surf.blit(s, r.topleft)
        for p in self.particles:
            pygame.draw.rect(surf, p[5], (p[0], p[1], 5, 5))
        if self.done_t:
            k = min(1.0, self.done_t / 30)
            s = ui.text_gradient('¡A PELEAR!', 60, (255, 255, 255), C.RED, extrude=6)
            ui.blit_center(surf, s, C.WIDTH / 2, 560 - (1 - k) * 100)
        if self.mode == 'versus':
            help_bar(surf, 'J1: A D W S + F ELEGIR / G CANCELAR      J2: FLECHAS + 1 ELEGIR / 2 CANCELAR      ESC VOLVER')
        else:
            help_bar(surf, 'FLECHAS / WASD  MOVER      ENTER / F  ELEGIR      G  CANCELAR      ESC  VOLVER')

    def draw_unknown(self, surf):
        x = C.WIDTH - 230
        q = ui.text_gradient('?', 160, (90, 90, 120), (40, 40, 60), extrude=6)
        ui.blit_center(surf, q, x, 420 + math.sin(self.t * 0.05) * 8)

    def draw_arcade_preview(self, surf):
        x = C.WIDTH - 230
        ui.panel(surf, (x - 190, 220, 380, 330), (0, 0, 0, 160), C.YELLOW, 2)
        ui.blit_center(surf, ui.text_outline('MODO ARCADE', 18, C.YELLOW), x, 250)
        lines = ['Vencé a los luchadores', 'del IES 10 y enfrentá', 'al JEFE FINAL: NICO.', '',
                 'La dificultad sube', 'en cada combate.', '', '¡Convertite en el', 'CAMPEÓN DEL IES 10!']
        for i, l in enumerate(lines):
            ui.blit_center(surf, ui.text(l, 11, C.WHITE), x, 290 + i * 26)
