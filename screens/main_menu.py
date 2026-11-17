"""Pantalla de título y menú principal."""
import math
import pygame
import config as C
from game import ui
from screens.common import Scene, nav, logo, menu_background, Menu, help_bar, AnimPlayer

MAIN_ITEMS = ['JUGAR', 'MODO ARCADE', 'VERSUS', 'PERSONAJES', 'OPCIONES', 'SALIR']
PLAY_ITEMS = ['1 JUGADOR VS CPU', 'ENTRENAMIENTO', 'VOLVER']


class TitleScene(Scene):
    def __init__(self, game, start_in_menu=False):
        super().__init__(game)
        self.audio = game.audio
        self.audio.music('musica_menu')
        self.state = 'menu' if start_in_menu else 'title'
        self.menu = Menu(MAIN_ITEMS, C.WIDTH / 2, 380, 50, 26)
        self.sub = Menu(PLAY_ITEMS, C.WIDTH / 2, 420, 56, 24)
        self.chars = [AnimPlayer(n, 'idle') for n in C.CHARACTERS[:4]]
        self.logo_k = 1.0 if start_in_menu else 0.0

    def handle_event(self, e):
        a = nav(e)
        if a is None:
            return
        if self.state == 'title':
            if a in ('ok',):
                self.audio.play('moneda')
                self.state = 'menu'
                self.menu.flash = 12
            return
        m = self.menu if self.state == 'menu' else self.sub
        if a == 'up':
            m.move(-1, self.audio)
            self.react(m)
        elif a == 'down':
            m.move(1, self.audio)
            self.react(m)
        elif a == 'back':
            self.audio.play('menu_atras')
            if self.state == 'sub':
                self.state = 'menu'
            else:
                self.state = 'title'
        elif a == 'ok':
            self.audio.play('menu_ok')
            m.flash = 12
            self.choose(m.items[m.sel])

    def react(self, m):
        # el luchador de fondo reacciona al pasar por las opciones
        i = m.sel % 4
        self.chars[i].set('golpe' if m.sel % 2 == 0 else 'patada', False, 'idle')

    def choose(self, item):
        g = self.game
        if item == 'JUGAR':
            self.state = 'sub'; self.sub.sel = 0
        elif item == 'MODO ARCADE':
            from screens.character_select import CharacterSelect
            g.change(lambda: CharacterSelect(g, 'arcade'))
        elif item == 'VERSUS':
            from screens.character_select import CharacterSelect
            g.change(lambda: CharacterSelect(g, 'versus'))
        elif item == 'PERSONAJES':
            from screens.gallery import GalleryScene
            g.change(lambda: GalleryScene(g))
        elif item == 'OPCIONES':
            from screens.options import OptionsScene
            g.change(lambda: OptionsScene(g))
        elif item == 'SALIR':
            g.quit()
        elif item == '1 JUGADOR VS CPU':
            from screens.character_select import CharacterSelect
            g.change(lambda: CharacterSelect(g, 'cpu'))
        elif item == 'ENTRENAMIENTO':
            from screens.character_select import CharacterSelect
            g.change(lambda: CharacterSelect(g, 'training'))
        elif item == 'VOLVER':
            self.state = 'menu'

    def update(self):
        super().update()
        self.menu.update(); self.sub.update()
        for c in self.chars:
            c.update()
        self.logo_k = min(1.0, self.logo_k + 0.04)

    def draw(self, surf):
        t = self.t
        menu_background(surf, t, (40, 30, 110))
        # luchadores de fondo
        xs = [140, 330, C.WIDTH - 330, C.WIDTH - 140]
        for i, c in enumerate(self.chars):
            face = 1 if i < 2 else -1
            sel = self.state != 'title' and self.menu.sel % 4 == i
            c.draw(surf, xs[i], C.HEIGHT - 40 + (0 if sel else 10), face, 3,
                   glow=(255, 214, 10) if sel else None)
        # sombra inferior para legibilidad
        sh = pygame.Surface((C.WIDTH, 300), pygame.SRCALPHA)
        for i in range(300):
            pygame.draw.line(sh, (0, 0, 0, int(i * 0.5)), (0, i), (C.WIDTH, i))
        # logo
        lg = logo()
        bob = math.sin(t * 0.04) * 6
        ty = 175 if self.state == 'title' else 140
        sc = (0.95 if self.state == 'title' else 0.72) * (0.5 + 0.5 * self.logo_k)
        im = pygame.transform.smoothscale(lg, (int(lg.get_width() * sc), int(lg.get_height() * sc)))
        ui.blit_center(surf, im, C.WIDTH / 2, ty + bob)
        if self.state == 'title':
            if (t // 30) % 2 == 0:
                ui.blit_center(surf, ui.text_outline('PRESIONÁ ENTER', 28, C.YELLOW), C.WIDTH / 2, 470)
            ui.blit_center(surf, ui.text('CRÉDITOS: ∞   -   1 O 2 JUGADORES', 12, (200, 200, 230)), C.WIDTH / 2, 530)
            from screens.common import arcetech_logo
            lg2 = arcetech_logo()
            ui.blit_center(surf, lg2, C.WIDTH / 2, 610)
            ui.blit_center(surf, ui.text('© 2026 ARCE TECH - TODOS LOS DERECHOS RESERVADOS', 10, (190, 230, 200)),
                           C.WIDTH / 2, 660)
            help_bar(surf, 'ENTER  COMENZAR      F11  PANTALLA COMPLETA')
        elif self.state == 'menu':
            ui.panel(surf, (C.WIDTH / 2 - 260, 345, 520, 320), (5, 5, 25, 170), C.YELLOW, 2)
            self.menu.draw(surf)
            help_bar(surf, '↑↓ / W S  ELEGIR      ENTER / F  ACEPTAR      ESC  VOLVER')
        else:
            ui.panel(surf, (C.WIDTH / 2 - 300, 360, 600, 220), (5, 5, 25, 190), C.CYAN, 2)
            ui.blit_center(surf, ui.text_outline('JUGAR', 22, C.CYAN), C.WIDTH / 2, 380)
            self.sub.draw(surf)
            help_bar(surf, '↑↓  ELEGIR      ENTER  ACEPTAR      ESC  VOLVER')
