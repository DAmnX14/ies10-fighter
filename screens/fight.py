"""Escena de combate: entrada de jugadores/IA, pausa y fin de partida."""
import pygame
import config as C
from game import ui
from game.combat import Match
from game.controls import InputState, KeyboardControllerSafe
from game.ai import AIController
from game.characters_data import move_list, CHARACTERS
from screens.common import Scene, nav, Menu, help_bar
from screens.training import TrainingTools


class FightScene(Scene):
    def __init__(self, game, c1, c2, mode, on_finish, difficulty=1):
        super().__init__(game)
        self.mode = mode
        self.on_finish = on_finish
        self.audio = game.audio
        st = C.STAGES.get(getattr(game, 'stage_id', 'aula'), {})
        self.audio.music(st.get('music', 'musica_combate'))   # cada escenario tiene su tema
        self.ctrl = {1: KeyboardControllerSafe(game.settings, 1)}
        ai2 = None
        if mode == 'versus':
            self.ctrl[2] = KeyboardControllerSafe(game.settings, 2)
        else:
            ai2 = AIController(difficulty)
            if mode == 'training':
                ai2.mode = 'dummy'
            self.ctrl[2] = ai2
        self.match = Match(game, c1, c2, mode, None, ai2, difficulty)
        self.inputs = {1: InputState(), 2: InputState()}
        self.paused = False
        self.pause_menu = None
        self.show_moves = False
        self.end_t = 0
        self.training = TrainingTools(self) if mode == 'training' else None

    def open_pause(self):
        items = ['CONTINUAR', 'LISTA DE MOVIMIENTOS']
        if self.mode == 'training':
            items += ['CAMBIAR PERSONAJES']
        items += ['SALIR AL MENÚ']
        self.pause_menu = Menu(items, C.WIDTH / 2, 300, 56, 24)
        self.paused = True
        self.audio.play('menu_ok')
        pygame.mixer.music.pause()

    def handle_event(self, e):
        if e.type != pygame.KEYDOWN:
            return
        m = self.match
        if not self.paused and m.state == 'encounter' and m.encounter is not None and \
                (nav(e) == 'ok' or getattr(e, 'pad', None) in ('ok', 'start') or e.key == pygame.K_ESCAPE):
            m.encounter.skip()          # saltear la escena previa
            return
        if getattr(e, 'pad', None) == 'start':
            if not self.paused:
                self.open_pause()
            elif self.show_moves:
                self.show_moves = False
            else:
                self.paused = False
                pygame.mixer.music.unpause()
            return
        if self.paused:
            if self.show_moves:
                if nav(e) in ('ok', 'back'):
                    self.show_moves = False
                return
            a = nav(e)
            m = self.pause_menu
            if a == 'up':
                m.move(-1, self.audio)
            elif a == 'down':
                m.move(1, self.audio)
            elif a == 'back' or e.key == pygame.K_p:
                self.paused = False
                pygame.mixer.music.unpause()
            elif a == 'ok':
                it = m.items[m.sel]
                self.audio.play('menu_ok')
                if it == 'CONTINUAR':
                    self.paused = False
                    pygame.mixer.music.unpause()
                elif it == 'LISTA DE MOVIMIENTOS':
                    self.show_moves = True
                elif it == 'CAMBIAR PERSONAJES':
                    pygame.mixer.music.unpause()
                    from screens.character_select import CharacterSelect
                    self.game.change(lambda: CharacterSelect(self.game, 'training'))
                elif it == 'SALIR AL MENÚ':
                    pygame.mixer.music.unpause()
                    from screens.main_menu import TitleScene
                    self.game.change(lambda: TitleScene(self.game, True))
            return
        if getattr(e, 'player', None):
            return                # botones del mando durante la pelea: se leen por tick
        if e.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_PAUSE):
            self.open_pause()
            return
        if self.training:
            self.training.handle_key(e.key)

    def update(self):
        super().update()
        if self.paused:
            self.pause_menu.update()
            return
        keys = pygame.key.get_pressed()
        m = self.match
        for side in (1, 2):
            c = self.ctrl[side]
            if isinstance(c, AIController):
                me = m.p1 if side == 1 else m.p2
                held = c.read(me, me.opponent(), m)
            else:
                held = c.read(keys)
            self.inputs[side].set(held)
        m.update(self.inputs)
        if m.state == 'match_over':
            self.end_t += 1
            if self.end_t == 30:
                self.on_finish(self)

    def draw(self, surf):
        self.match.draw(surf)
        if self.paused:
            s = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 20, 190))
            surf.blit(s, (0, 0))
            if self.show_moves:
                self.draw_moves(surf)
            else:
                ui.blit_center(surf, ui.text_gradient('PAUSA', 60, extrude=6), C.WIDTH / 2, 190)
                self.pause_menu.draw(surf)
                help_bar(surf, '↑↓ ELEGIR      ENTER ACEPTAR      ESC CONTINUAR')

    def draw_moves(self, surf):
        m = self.match
        fighters = [m.p1] if self.mode != 'versus' else [m.p1, m.p2]
        w = 560
        for i, f in enumerate(fighters):
            x = C.WIDTH / 2 - (w + 20) * len(fighters) / 2 + i * (w + 40)
            ui.panel(surf, (x, 70, w, 560), (0, 0, 0, 220), f.color, 3)
            ui.blit_center(surf, ui.text_gradient(f.data['display'], 28, (255, 255, 255), f.color, extrude=3),
                           x + w / 2, 105)
            for j, (name, inp) in enumerate(move_list(f.name)):
                y = 146 + j * 36
                col = C.YELLOW if j >= 8 else C.WHITE
                surf.blit(ui.text(name, 11, col), (x + 20, y))
                surf.blit(ui.text(inp, 10, (170, 220, 255)), (x + 20, y + 16))
        help_bar(surf, '→ = HACIA EL RIVAL      ↓ = ABAJO      ENTER / ESC  VOLVER')
