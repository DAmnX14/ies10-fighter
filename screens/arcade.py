"""Modo Arcade: el jugador enfrenta a 5 rivales al azar y al jefe final, con dificultad creciente."""
import math
import random
import pygame
import config as C
from game import assets, ui
from game.characters_data import CHARACTERS
from screens.common import Scene, nav, menu_background, help_bar, AnimPlayer

ENDINGS = {
    'nico': ['Nico derrotó a toda la plantilla.', 'Nadie pidió aumento ese año.', '',
             'ArceTech abrió una sucursal', 'en el aula del IES 10.', 'El jefe siempre gana.'],
    'pantoja': ['Pantoja derrotó a todos en el aula.', 'Desde ese día, nadie volvió a reírse',
                'de su remera rosa.', '', 'El kiosco del IES 10 le regaló', 'alfajores de por vida.'],
    'parada': ['Parada fue tan rápido', 'que terminó el torneo antes', 'de que sonara el timbre.', '',
               'Su campera verde es ahora', 'una leyenda del recreo.'],
    'nehuen': ['Nehuen celebró con un solo', 'de guitarra que se escuchó', 'en todo Fraile Pintado.', '',
               'Su piluso ahora cuelga', 'en el salón de la fama del IES 10.'],
    'angel': ['Angel compiló el torneo entero', 'sin un solo warning.', '',
              'Ahora el sistema de notas del IES 10', 'corre con su código.', 'Nadie entiende cómo, pero anda.'],
    'facu': ['Facu y su gato naranja', 'ganaron el torneo.', '',
             'La IA escribió la crónica del combate', 'y el gato se durmió encima del teclado.', 'Final perfecto.'],
    'pedro': ['Pedro ganó sin levantar la voz.', 'Al final, todos se dieron la mano.', '',
              'Desde ese día, en el IES 10', 'los recreos son en paz.', 'Bueno... casi siempre.'],
    'emi': ['Emi aprobó el torneo con diez.', 'Los profes le pidieron los apuntes.', '',
            'Ahora da clases de apoyo', 'de "cómo no perder una pelea".', 'Cupo lleno.'],
    'denis': ['Denis levantó la copa', 'y la dio la vuelta olímpica por el aula.', '',
              'Nehuen no habló por una semana.', 'El aula quedó pintada', 'de rojo y blanco.'],
    'luciano': ['Luciano labró el acta final:', '"Todos los rivales: amonestados."', '', 'La preceptoría nunca',
                'volvió a ser la misma.', 'El orden fue restaurado.'],
}


class ArcadeRun:
    def __init__(self, game, char):
        self.game = game
        self.char = char
        others = [c for c in C.CHARACTERS if c != char and c != C.BOSS]
        random.shuffle(others)
        others = others[:5]          # con 10 luchadores: 5 rivales al azar + el jefe
        # NICO, el jefe de ArceTech, siempre es el último rival
        self.ladder = others + ([C.BOSS] if char != C.BOSS else [])
        self.stage = 0
        self.base = game.settings['difficulty']
        self.continues = 0
        self.score = 0

    def level(self):
        # combate 1: dificultad elegida; 2: +1; jefe final: +1 más (máximo EXTREMO)
        if self.stage == len(self.ladder) - 1:
            return min(3, self.base + 2)
        return min(3, self.base + min(self.stage, 1))

    def next_fight(self):
        g = self.game
        g.change(lambda: LadderScreen(g, self))

    def begin_fight(self):
        from screens.versus import VersusScreen, start_fight
        g = self.game
        opp = self.ladder[self.stage]
        sub = 'JEFE FINAL' if self.stage == len(self.ladder) - 1 else f'COMBATE {self.stage + 1} DE {len(self.ladder)}'
        lvl = self.level()
        last = self.stage == len(self.ladder) - 1
        g.stage_id = 'plaza' if (last or self.stage % 2 == 1) else 'aula'

        def launch():
            start_fight(g, self.char, opp, 'arcade', lvl, on_finish=self.fight_over)
        g.change(lambda: VersusScreen(g, self.char, opp, 'arcade', on_done=launch, subtitle=sub, difficulty=lvl))

    def fight_over(self, scene, winner_side):
        g = self.game
        from screens.results import ResultScreen
        opp = self.ladder[self.stage]
        m = scene.match
        if winner_side == 1:
            self.score += 10000 + m.p1.health * 10 + (m.timer * 100 if m.round_time else 0)
            self.stage += 1
            if self.stage >= len(self.ladder):
                g.change(lambda: ResultScreen(g, self.char, opp, 1, 'arcade', items=['CONTINUAR'],
                                              on_select=lambda it: g.change(lambda: EndingScreen(g, self))))
            else:
                g.change(lambda: ResultScreen(g, self.char, opp, 1, 'arcade', items=['SIGUIENTE RIVAL'],
                                              on_select=lambda it: self.next_fight()))
        else:
            g.change(lambda: ResultScreen(g, self.char, opp, 2, 'arcade', items=['CONTINUAR'],
                                          on_select=lambda it: g.change(lambda: ContinueScreen(g, self))))


class LadderScreen(Scene):
    def __init__(self, game, run):
        super().__init__(game)
        self.run = run
        game.audio.music('musica_seleccion')
        self.player = AnimPlayer(run.char, 'idle')

    def handle_event(self, e):
        if nav(e) == 'ok' and self.t > 30:
            self.go()

    def go(self):
        if getattr(self, '_gone', False):
            return
        self._gone = True
        self.game.audio.play('menu_ok')
        self.run.begin_fight()

    def update(self):
        super().update()
        self.player.update()
        if self.t > 240:
            self.go()

    def draw(self, surf):
        t = self.t
        menu_background(surf, t, (20, 60, 120))
        ui.blit_center(surf, ui.text_gradient('CAMINO AL CAMPEONATO', 36, extrude=5), C.WIDTH / 2, 70)
        n = len(self.run.ladder)
        for i, opp in enumerate(self.run.ladder):
            sp = 260 if n <= 3 else 215
            x = (380 if n <= 3 else 420) + i * sp
            y = 330
            d = CHARACTERS[opp]
            done = i < self.run.stage
            cur = i == self.run.stage
            r = pygame.Rect(x - 90, y - 90, 180, 180)
            pygame.draw.rect(surf, (0, 0, 0), r.inflate(12, 12))
            pygame.draw.rect(surf, C.YELLOW if cur and (t // 10) % 2 else d['color'], r.inflate(6, 6))
            por = pygame.transform.scale(assets.character(opp).portrait, (180, 180))
            if done:
                por = por.copy(); por.fill((80, 80, 80, 255), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(por, r.topleft)
            if done:
                ui.blit_center(surf, ui.text_gradient('K.O.', 40, (255, 255, 255), C.RED, extrude=4), x, y)
            label = 'JEFE FINAL' if i == n - 1 else f'RIVAL {i + 1}'
            ui.blit_center(surf, ui.text_outline(label, 14, C.YELLOW if cur else C.WHITE), x, y + 115)
            ui.blit_center(surf, ui.text_outline(d['display'], 16, d['color']), x, y + 140)
        # jugador
        pygame.draw.ellipse(surf, (0, 0, 0), (80, 640, 180, 24))
        self.player.draw(surf, 170, 655, 1, 3)
        diff = C.DIFFICULTIES[self.run.level()]
        ui.blit_center(surf, ui.text_outline(f'DIFICULTAD: {diff}', 16, C.CYAN), C.WIDTH / 2 + 120, 560)
        ui.blit_center(surf, ui.text_outline(f'PUNTOS: {int(self.run.score):08d}', 16, C.WHITE), C.WIDTH / 2 + 120, 600)
        help_bar(surf, 'ENTER  PELEAR')


class ContinueScreen(Scene):
    def __init__(self, game, run):
        super().__init__(game)
        self.run = run
        self.count = 10
        self.sub = 0
        game.audio.stop_music()
        game.audio.announce('loc_continuar')
        self.anim = AnimPlayer(run.char, 'derrota', False, None)

    def handle_event(self, e):
        a = nav(e)
        if a == 'ok':
            self.game.audio.play('moneda')
            self.run.continues += 1
            self.run.score = int(self.run.score * 0.5)
            self.run.next_fight()
        elif a == 'back':
            self.game_over()

    def game_over(self):
        from screens.main_menu import TitleScene
        if getattr(self, '_over', False):
            return
        self._over = True
        self.game.audio.announce('loc_fin')
        self.game.change(lambda: TitleScene(self.game, True))

    def update(self):
        super().update()
        self.anim.update()
        self.sub += 1
        if self.sub >= 60:
            self.sub = 0
            self.count -= 1
            self.game.audio.play('tic')
            if self.count < 0:
                self.game_over()

    def draw(self, surf):
        surf.fill((10, 0, 0))
        ui.blit_center(surf, ui.text_gradient('¿CONTINUAR?', 64, (255, 255, 255), C.RED, extrude=6), C.WIDTH / 2, 150)
        n = max(0, self.count)
        img = ui.text_gradient(str(n), 140, (255, 255, 220), C.YELLOW, extrude=8)
        sc = 1 + 0.3 * (1 - self.sub / 60)
        img = pygame.transform.scale(img, (int(img.get_width() * sc), int(img.get_height() * sc)))
        ui.blit_center(surf, img, C.WIDTH / 2, 360)
        self.anim.draw(surf, C.WIDTH / 2, 680, 1, 2)
        help_bar(surf, 'ENTER  CONTINUAR      ESC  RENDIRSE')


class EndingScreen(Scene):
    def __init__(self, game, run):
        super().__init__(game)
        self.run = run
        game.audio.music('musica_victoria')
        self.anim = AnimPlayer(run.char, 'victoria', True)
        self.lines = ENDINGS[run.char]
        self.credits = ['IES 10 FIGHTER', '', 'LUCHADORES', 'PANTOJA - PARADA - NEHUEN - LUCIANO - NICO', '', 'UNA PRODUCCIÓN DE', 'ARCE TECH', '',
                        'ESCENARIO', 'AULA DEL IES N.º 10', '', 'PROGRAMACIÓN', 'PYTHON + PYGAME', '',
                        'SPRITES', 'RIG 2D GENERADO A PARTIR DE LAS ILUSTRACIONES ORIGINALES', '',
                        'MÚSICA Y SONIDO', 'SÍNTESIS ORIGINAL (VER audio_credits.md)', '',
                        'FUENTE', 'PRESS START 2P (SIL OPEN FONT LICENSE)', '', '¡GRACIAS POR JUGAR!']

    def handle_event(self, e):
        if nav(e) in ('ok', 'back') and self.t > 120:
            from screens.main_menu import TitleScene
            self.game.change(lambda: TitleScene(self.game, True))

    def update(self):
        super().update()
        self.anim.update()
        if self.t == 30:
            self.game.audio.announce(f'loc_{self.run.char}_gana')

    def draw(self, surf):
        d = CHARACTERS[self.run.char]
        menu_background(surf, self.t, tuple(c // 2 for c in d['color']))
        ui.blit_center(surf, ui.text_gradient('¡CAMPEÓN DEL IES 10!', 44, (255, 255, 255), d['color'], extrude=6),
                       C.WIDTH / 2, 70)
        pygame.draw.ellipse(surf, (0, 0, 0), (190, 650, 220, 30))
        self.anim.draw(surf, 300, 668, 1, 4)
        for i, l in enumerate(self.lines):
            img = ui.text(l, 15, C.WHITE)
            a = max(0, min(255, (self.t - 40 - i * 25) * 8))
            img.set_alpha(a)
            surf.blit(img, (560, 150 + i * 34))
        # créditos
        y0 = C.HEIGHT + 200 - (self.t - 200) * 0.8 if self.t > 200 else C.HEIGHT + 200
        clip = pygame.Rect(560, 380, 700, 280)
        surf.set_clip(clip)
        for i, l in enumerate(self.credits):
            col = C.YELLOW if l.isupper() and len(l) < 20 else C.WHITE
            ui.blit_center(surf, ui.text(l, 12, col), 900, y0 - 200 + i * 30 + 0)
        surf.set_clip(None)
        ui.blit_center(surf, ui.text_outline(f'PUNTAJE FINAL: {int(self.run.score):08d}', 18, C.YELLOW), 900, 690 - 30)
        help_bar(surf, 'ENTER  VOLVER AL MENÚ')
