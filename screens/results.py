"""Pantalla de victoria / derrota: «PANTOJA WINS», «PARADA WINS», etc."""
import math
import random
import pygame
import config as C
from game import assets, ui
from game.characters_data import CHARACTERS
from screens.common import Scene, nav, Menu, help_bar, AnimPlayer, menu_background


class ResultScreen(Scene):
    def __init__(self, game, c1, c2, winner_side, mode, difficulty=1, items=None, on_select=None,
                 cpu_won=None):
        super().__init__(game)
        self.c1, self.c2, self.mode, self.difficulty = c1, c2, mode, difficulty
        self.winner = c1 if winner_side == 1 else c2
        self.loser = c2 if winner_side == 1 else c1
        self.winner_side = winner_side
        self.audio = game.audio
        if cpu_won is None:
            cpu_won = mode in ('cpu', 'arcade') and winner_side == 2
        self.cpu_won = cpu_won
        self.audio.music('musica_derrota' if cpu_won else 'musica_victoria')
        self.wa = AnimPlayer(self.winner, 'victoria', True)
        self.la = AnimPlayer(self.loser, 'derrota', False, None)
        self.quote = random.choice(CHARACTERS[self.winner]['win_quotes'])
        self.items = items or ['REVANCHA', 'ELEGIR PERSONAJES', 'MENÚ PRINCIPAL']
        self.menu = Menu(self.items, C.WIDTH / 2, 560, 46, 20)
        self.on_select = on_select
        self.confetti = [[random.uniform(0, C.WIDTH), random.uniform(-C.HEIGHT, 0), random.uniform(-1, 1),
                          random.uniform(2, 5), random.choice([C.YELLOW, CHARACTERS[self.winner]['color'], C.WHITE,
                                                               C.CYAN])] for _ in range(120)]

    def handle_event(self, e):
        if self.t < 60:
            return
        a = nav(e)
        if a == 'up':
            self.menu.move(-1, self.audio)
        elif a == 'down':
            self.menu.move(1, self.audio)
        elif a == 'ok':
            self.audio.play('menu_ok')
            it = self.menu.items[self.menu.sel]
            if self.on_select:
                self.on_select(it)
                return
            g = self.game
            if it == 'REVANCHA':
                from screens.versus import start_fight
                start_fight(g, self.c1, self.c2, self.mode, self.difficulty)
            elif it == 'ELEGIR PERSONAJES':
                from screens.character_select import CharacterSelect
                g.change(lambda: CharacterSelect(g, self.mode))
            else:
                from screens.main_menu import TitleScene
                g.change(lambda: TitleScene(g, True))

    def update(self):
        super().update()
        self.wa.update(); self.la.update(); self.menu.update()
        if self.t == 25:
            self.audio.announce(f'loc_{self.winner}_gana')
        if self.t == 70:
            self.audio.voice(self.winner, 'victoria')
        for c in self.confetti:
            c[0] += c[2] + math.sin((self.t + c[1]) * 0.05); c[1] += c[3]
            if c[1] > C.HEIGHT:
                c[1] = -10

    def draw(self, surf):
        t = self.t
        d = CHARACTERS[self.winner]
        menu_background(surf, t, tuple(c // 2 for c in d['color']))
        # rayos detrás del ganador
        cx, cy = 360, 420
        s = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
        for i in range(14):
            a = i * math.tau / 14 + t * 0.01
            pygame.draw.polygon(s, d['color'] + (40,), [(cx, cy), (cx + math.cos(a) * 900, cy + math.sin(a) * 900),
                                                        (cx + math.cos(a + 0.15) * 900, cy + math.sin(a + 0.15) * 900)])
        surf.blit(s, (0, 0))
        if not self.cpu_won:
            for c in self.confetti:
                pygame.draw.rect(surf, c[4], (c[0], c[1], 6, 4))
        pygame.draw.ellipse(surf, (0, 0, 0), (cx - 130, 650, 260, 34))
        self.wa.draw(surf, cx, 668, 1, 4)
        # perdedor pequeño y oscurecido
        img, dx, dy = assets.character(self.loser).frame_surface('derrota', self.la.frame, -1, 2)
        dark = img.copy(); dark.fill((90, 90, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(dark, (1080 + dx, 610 + dy))
        # título
        k = min(1.0, t / 14)
        title = ui.text_gradient(f'{d["display"]} WINS', 64, (255, 255, 255), d['color'], extrude=8)
        sc = 2 - k
        im = pygame.transform.scale(title, (int(title.get_width() * sc), int(title.get_height() * sc)))
        ui.blit_center(surf, im, C.WIDTH / 2 + 160, 120)
        if self.cpu_won:
            ui.blit_center(surf, ui.text_outline('PERDISTE...', 22, C.RED), C.WIDTH / 2 + 160, 190)
        # frase
        if t > 30:
            ui.panel(surf, (620, 240, 600, 120), (0, 0, 0, 190), d['color'], 3)
            words = ('«' + self.quote + '»').split()
            lines, cur = [], ''
            for w in words:
                if len(cur + ' ' + w) > 30:
                    lines.append(cur); cur = w
                else:
                    cur = (cur + ' ' + w).strip()
            lines.append(cur)
            for i, l in enumerate(lines):
                surf.blit(ui.text(l, 15, C.WHITE), (645, 262 + i * 28))
            lq = CHARACTERS[self.loser]['lose_quote']
            surf.blit(ui.text(f'{CHARACTERS[self.loser]["display"]}: «{lq}»'[:62], 9, (180, 180, 200)), (630, 380))
        if t > 60:
            ui.panel(surf, (C.WIDTH / 2 - 230 + 160, 525, 460, 50 + 46 * len(self.items) - 20), (0, 0, 20, 200), C.YELLOW, 2)
            self.menu.x = C.WIDTH / 2 + 160
            self.menu.draw(surf)
        help_bar(surf, '↑↓  ELEGIR      ENTER  ACEPTAR')
