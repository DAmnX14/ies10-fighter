"""Presentación VS antes del combate y lanzamiento de partidas Versus / VS CPU / Entrenamiento."""
import math
import random
import pygame
import config as C
from game import assets, ui
from game.characters_data import CHARACTERS
from screens.common import Scene, nav, AnimPlayer


class VersusScreen(Scene):
    def __init__(self, game, c1, c2, mode, on_done=None, subtitle=None, difficulty=None):
        super().__init__(game)
        self.c1, self.c2, self.mode = c1, c2, mode
        self.on_done = on_done
        self.subtitle = subtitle
        self.difficulty = difficulty
        self.a1 = AnimPlayer(c1, 'presentacion', False, 'idle')
        self.a2 = AnimPlayer(c2, 'presentacion', False, 'idle')
        self.audio = game.audio
        self.audio.stop_music(300)
        self.audio.play('ultimate_activar')
        self.started = False

    def handle_event(self, e):
        a = nav(e)
        if a in ('left', 'right') and self.on_done is None and not self.started:
            order = C.STAGE_ORDER
            cur = getattr(self.game, 'stage_id', 'aula')
            self.game.stage_id = order[(order.index(cur) + (1 if a == 'right' else -1)) % len(order)]
            self.audio.play('menu_mover')
            self.t = min(self.t, 120)          # da tiempo para elegir
        if a == 'ok' and self.t > 40:
            self.go()

    def go(self):
        if self.started:
            return
        self.started = True
        g = self.game
        if self.on_done:
            self.on_done()
            return
        start_fight(g, self.c1, self.c2, self.mode, self.difficulty)

    def update(self):
        super().update()
        self.a1.update(); self.a2.update()
        t = self.t
        if t == 20:
            self.audio.announce(f'loc_{self.c1}')
        if t == 60:
            self.audio.play('ko_impacto')
        if t == 95:
            self.audio.announce(f'loc_{self.c2}')
        if t >= 230:
            self.go()

    def draw(self, surf):
        t = self.t
        surf.fill((0, 0, 0))
        k = min(1.0, t / 18)
        d1, d2 = CHARACTERS[self.c1], CHARACTERS[self.c2]
        # mitades diagonales
        off = (1 - k) * 800
        pygame.draw.polygon(surf, tuple(c // 3 for c in d1['color']),
                            [(-off, 0), (C.WIDTH / 2 + 80 - off, 0), (C.WIDTH / 2 - 80 - off, C.HEIGHT), (-off, C.HEIGHT)])
        pygame.draw.polygon(surf, tuple(c // 3 for c in d2['color']),
                            [(C.WIDTH + off, 0), (C.WIDTH / 2 + 80 + off, 0), (C.WIDTH / 2 - 80 + off, C.HEIGHT),
                             (C.WIDTH + off, C.HEIGHT)])
        for i in range(30):
            y = (i * 47 + t * 9) % C.HEIGHT
            pygame.draw.line(surf, d1['color'], (0 - off, y), (C.WIDTH / 2 - 200 - off, y), 1)
            y2 = (i * 53 - t * 9) % C.HEIGHT
            pygame.draw.line(surf, d2['color'], (C.WIDTH / 2 + 200 + off, y2), (C.WIDTH + off, y2), 1)
        # retratos grandes
        # columnas laterales: retrato, nombre y frase (ancho 280) — los cuerpos van al centro
        COLW = 280
        p1 = assets.character(self.c1).portrait_at(COLW)
        p2 = assets.character(self.c2).portrait_at(COLW, flip=True)
        surf.blit(p1, (30 - off, 70))
        surf.blit(p2, (C.WIDTH - 30 - COLW + off, 70))
        # cuerpos, a escala 2, entre las columnas y debajo del «VS»
        self.a1.draw(surf, 450 - off, 650, 1, 2)
        self.a2.draw(surf, C.WIDTH - 450 + off, 650, -1, 2)
        # nombres y frases
        n1 = ui.text_gradient(d1['display'], 36, (255, 255, 255), d1['color'], extrude=5)
        n2 = ui.text_gradient(d2['display'], 36, (255, 255, 255), d2['color'], extrude=5)
        surf.blit(n1, (30 - off, 362))
        surf.blit(n2, (C.WIDTH - 30 - n2.get_width() + off, 362))
        from screens.character_select import wrap
        for side, d, base in ((1, d1, 30 - off), (2, d2, C.WIDTH - 30 + off)):
            for li, ln in enumerate(wrap('«' + d['quote'] + '»', 11, COLW)):
                q = ui.text_outline(ln, 11, C.WHITE)
                surf.blit(q, (base if side == 1 else base - q.get_width(), 420 + li * 18))
        # VS
        if t > 55:
            kk = min(1.0, (t - 55) / 8)
            vs = ui.text_gradient('VS', 130, (255, 255, 255), C.RED, extrude=10)
            sc = 0.5 + 0.5 * kk + 0.03 * math.sin(t * 0.3)
            vs = pygame.transform.scale(vs, (int(vs.get_width() * sc), int(vs.get_height() * sc)))
            ui.blit_center(surf, vs, C.WIDTH / 2, 230)
        if self.subtitle:
            ui.blit_center(surf, ui.text_outline(self.subtitle, 18, C.YELLOW), C.WIDTH / 2, 40)
        sname = C.STAGES[getattr(self.game, 'stage_id', 'aula')]['name']
        lab = f'← ESCENARIO: {sname} →' if self.on_done is None else f'ESCENARIO: {sname}'
        ui.blit_center(surf, ui.text_outline(lab, 14, C.CYAN), C.WIDTH / 2, C.HEIGHT - 44)
        if self.on_done is None:
            ui.blit_center(surf, ui.text('← → CAMBIAR ESCENARIO   ENTER PELEAR', 9, C.WHITE), C.WIDTH / 2, C.HEIGHT - 16)
        if t > 55 and t < 64:
            s = pygame.Surface((C.WIDTH, C.HEIGHT)); s.fill((255, 255, 255)); s.set_alpha(255 - (t - 55) * 28)
            surf.blit(s, (0, 0))


def start_fight(g, c1, c2, mode, difficulty=None, on_finish=None, subtitle=None):
    from screens.fight import FightScene
    from screens.results import ResultScreen

    if difficulty is None:
        difficulty = g.settings['difficulty']

    def finish(scene):
        m = scene.match
        win = m.winner
        if on_finish:
            on_finish(scene, win.side)
            return
        g.change(lambda: ResultScreen(g, c1, c2, win.side, mode, difficulty))

    g.change(lambda: FightScene(g, c1, c2, mode, finish, difficulty))
