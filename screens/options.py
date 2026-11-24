"""Opciones: volúmenes, tiempo, dificultad, rondas, pantalla y configuración de controles."""
import pygame
import config as C
from game import ui
from game.controls import key_name
from game import gamepad
from screens.common import Scene, nav, menu_background, help_bar


class OptionsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.audio = game.audio
        self.audio.music('musica_menu')
        self.sel = 0
        self.items = ['music_volume', 'sfx_volume', 'voice_volume', 'round_time', 'rounds_to_win', 'difficulty',
                      'fullscreen', 'crt', 'show_intro', 'in1', 'in2', 'ctl1', 'ctl2', 'reset', 'back']

    def label(self, k):
        s = self.game.settings
        if k == 'music_volume':
            return 'VOLUMEN MÚSICA', self.bar(s[k])
        if k == 'sfx_volume':
            return 'VOLUMEN EFECTOS', self.bar(s[k])
        if k == 'voice_volume':
            return 'VOLUMEN VOCES', self.bar(s[k])
        if k == 'round_time':
            return 'TIEMPO POR RONDA', ('∞ INFINITO' if s[k] == 0 else f'{s[k]} SEG')
        if k == 'rounds_to_win':
            return 'RONDAS', {1: 'A 1 RONDA', 2: 'MEJOR DE 3', 3: 'MEJOR DE 5'}[s[k]]
        if k == 'difficulty':
            return 'DIFICULTAD CPU', C.DIFFICULTIES[s[k]]
        if k == 'fullscreen':
            return 'PANTALLA COMPLETA', 'SÍ' if s[k] else 'NO'
        if k == 'crt':
            return 'FILTRO CRT RETRO', 'SÍ' if s[k] else 'NO'
        if k == 'show_intro':
            return 'VER INTRO AL INICIAR', 'SÍ' if s[k] else 'NO'
        if k in ('in1', 'in2'):
            p = k[-1]
            mode = s.data.get('input_mode', {}).get(p, 'ambos')
            mgr = gamepad.manager()
            n = mgr.count() if mgr else 0
            extra = ''
            if mode != 'teclado':
                j = mgr.pad_for(int(p)) if mgr else None
                extra = '  (MANDO OK)' if j is not None else '  (SIN MANDO)'
            return f'ENTRADA JUGADOR {p}', gamepad.INPUT_NAMES.get(mode, mode) + extra
        if k == 'ctl1':
            return 'CONTROLES JUGADOR 1', '>'
        if k == 'ctl2':
            return 'CONTROLES JUGADOR 2', '>'
        if k == 'reset':
            return 'RESTAURAR VALORES', ''
        return 'VOLVER', ''

    @staticmethod
    def bar(v):
        return ('BAR', v)

    def change(self, d):
        s = self.game.settings
        k = self.items[self.sel]
        if k in ('music_volume', 'sfx_volume', 'voice_volume'):
            s[k] = round(max(0.0, min(1.0, s[k] + 0.1 * d)), 2)
            self.audio.refresh_volume()
            if k == 'voice_volume':
                self.audio.announce('loc_pelea')
            else:
                self.audio.play('golpe_debil')
        elif k == 'round_time':
            i = C.TIMER_OPTIONS.index(s[k]) if s[k] in C.TIMER_OPTIONS else 2
            s[k] = C.TIMER_OPTIONS[(i + d) % len(C.TIMER_OPTIONS)]
        elif k == 'rounds_to_win':
            s[k] = (s[k] - 1 + d) % 3 + 1
        elif k == 'difficulty':
            s[k] = (s[k] + d) % 4
        elif k == 'fullscreen':
            self.game.toggle_fullscreen()
        elif k in ('crt', 'show_intro'):
            s[k] = not s[k]
        elif k in ('in1', 'in2'):
            im = s.data.setdefault('input_mode', {'1': 'ambos', '2': 'ambos'})
            cur = im.get(k[-1], 'ambos')
            modes = gamepad.INPUT_MODES
            im[k[-1]] = modes[(modes.index(cur) + d) % len(modes) if cur in modes else 0]
        self.audio.play('menu_mover')
        s.save()

    def handle_event(self, e):
        a = nav(e)
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s):
            pass
        if a == 'up':
            self.sel = (self.sel - 1) % len(self.items); self.audio.play('menu_mover')
        elif a == 'down':
            self.sel = (self.sel + 1) % len(self.items); self.audio.play('menu_mover')
        elif a == 'left':
            self.change(-1)
        elif a == 'right':
            self.change(1)
        elif a == 'ok':
            k = self.items[self.sel]
            self.audio.play('menu_ok')
            if k == 'ctl1':
                self.game.change(lambda: ControlsScene(self.game, 1))
            elif k == 'ctl2':
                self.game.change(lambda: ControlsScene(self.game, 2))
            elif k == 'reset':
                s = self.game.settings
                keep = {k_: s.data.get(k_) for k_ in ('controls', 'pad_controls')}
                s.data = __import__('json').loads(__import__('json').dumps(C.DEFAULT_SETTINGS))
                s.data.update({k_: v for k_, v in keep.items() if v is not None})
                s.save(); self.audio.refresh_volume()
            elif k == 'back':
                self.back()
            else:
                self.change(1)
        elif a == 'back':
            self.back()

    def back(self):
        self.game.settings.save()
        self.audio.play('menu_atras')
        from screens.main_menu import TitleScene
        self.game.change(lambda: TitleScene(self.game, True))

    def draw(self, surf):
        menu_background(surf, self.t, (20, 70, 90))
        ui.blit_center(surf, ui.text_gradient('OPCIONES', 50, extrude=6), C.WIDTH / 2, 64)
        ui.panel(surf, (170, 104, 940, 572), (0, 0, 20, 200), C.CYAN, 2)
        for i, k in enumerate(self.items):
            name, val = self.label(k)
            y = 118 + i * 37
            sel = i == self.sel
            col = C.YELLOW if sel else C.WHITE
            if sel:
                pygame.draw.rect(surf, (60, 40, 0), (180, y - 6, 920, 34))
                pygame.draw.polygon(surf, C.YELLOW, [(190, y + 2), (204, y + 11), (190, y + 20)])
            surf.blit(ui.text(name, 15, col), (220, y + 2))
            if isinstance(val, tuple):
                n = int(round(val[1] * 10))
                for j in range(10):
                    r = pygame.Rect(1080 - (10 - j) * 22, y + 2, 18, 18)
                    pygame.draw.rect(surf, (C.CYAN if sel else (120, 180, 230)) if j < n else (40, 40, 70), r)
                surf.blit(ui.text(f'{n * 10}%', 12, C.WHITE), (1080 - 10 * 22 - 70, y + 5))
                if sel:
                    ax = 1080 - 10 * 22 - 92
                    pygame.draw.polygon(surf, C.YELLOW, [(ax, y + 11), (ax + 12, y + 3), (ax + 12, y + 19)])
            elif val:
                v = ui.text(val, 15, C.CYAN if sel else (180, 220, 255))
                surf.blit(v, (1080 - v.get_width(), y + 2))
                if sel and k not in ('ctl1', 'ctl2'):
                    ax = 1080 - v.get_width() - 30
                    pygame.draw.polygon(surf, C.YELLOW, [(ax, y + 11), (ax + 12, y + 3), (ax + 12, y + 19)])
        help_bar(surf, '↑↓ ELEGIR      ←→ CAMBIAR      ENTER ACEPTAR      ESC VOLVER')


class ControlsScene(Scene):
    def __init__(self, game, player):
        super().__init__(game)
        self.player = player
        self.audio = game.audio
        self.sel = 0
        self.waiting = False
        self.items = C.ACTIONS + ['restaurar', 'volver']
        self.capture_pad = False

    def handle_event(self, e):
        s = self.game.settings
        act = self.items[self.sel]
        if self.waiting and act in gamepad.DEFAULT_PAD and e.type in (pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION):
            # asignar un botón (o gatillo) del mando a la acción
            if e.type == pygame.JOYAXISMOTION:
                if e.axis < 2 or e.value < 0.6:
                    return
                b = gamepad.TRIGGER_BASE + e.axis
            else:
                b = e.button
                if b in gamepad.START_BUTTONS:
                    return
            pc = gamepad.manager().buttons(self.player)
            for a in pc:
                pc[a] = [x for x in pc[a] if x != b]
            pc[act] = [b]
            self.audio.play('menu_ok')
            s.save()
            self.waiting = False
            self.capture_pad = False
            return
        if e.type != pygame.KEYDOWN:
            return
        if self.waiting:
            if getattr(e, 'player', None):
                return
            self.capture_pad = False
            if e.key != pygame.K_ESCAPE:
                act = self.items[self.sel]
                ctl = s.controls(self.player)
                # quitar la tecla de cualquier otra acción de ambos jugadores
                for p in (1, 2):
                    for a in C.ACTIONS:
                        if e.key in s.controls(p)[a]:
                            s.controls(p)[a] = [k for k in s.controls(p)[a] if k != e.key]
                ctl[act] = [e.key]
                self.audio.play('menu_ok')
                s.save()
            self.waiting = False
            return
        a = nav(e)
        if e.key in (pygame.K_UP,) and not getattr(e, 'pad', None):
            a = 'up'
        if getattr(e, 'pad', None) in ('ok', 'start'):
            e = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        elif getattr(e, 'pad', None) == 'back':
            e = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        if a == 'up':
            self.sel = (self.sel - 1) % len(self.items); self.audio.play('menu_mover')
        elif a == 'down':
            self.sel = (self.sel + 1) % len(self.items); self.audio.play('menu_mover')
        elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            it = self.items[self.sel]
            if it == 'volver':
                self.back()
            elif it == 'restaurar':
                s.controls(self.player).update({k: list(v) for k, v in C.DEFAULT_CONTROLS[self.player].items()})
                s.data.setdefault('pad_controls', {})[str(self.player)] = {k: list(v) for k, v in gamepad.DEFAULT_PAD.items()}
                s.save(); self.audio.play('menu_ok')
            else:
                self.waiting = True
                self.capture_pad = True
                self.audio.play('menu_ok')
        elif e.key == pygame.K_ESCAPE:
            self.back()

    def back(self):
        self.audio.play('menu_atras')
        self.game.change(lambda: OptionsScene(self.game))

    def draw(self, surf):
        menu_background(surf, self.t, (60, 30, 90))
        ui.blit_center(surf, ui.text_gradient(f'CONTROLES JUGADOR {self.player}', 36, extrude=5), C.WIDTH / 2, 64)
        ui.panel(surf, (240, 112, 800, 556), (0, 0, 20, 200), C.YELLOW, 2)
        ctl = self.game.settings.controls(self.player)
        mgr = gamepad.manager()
        pc = mgr.buttons(self.player) if mgr else gamepad.DEFAULT_PAD
        surf.blit(ui.text('TECLADO', 12, (180, 180, 220)), (700, 124))
        surf.blit(ui.text('MANDO', 12, (180, 180, 220)), (900, 124))
        for i, it in enumerate(self.items):
            y = 150 + i * 42
            sel = i == self.sel
            col = C.YELLOW if sel else C.WHITE
            if sel:
                pygame.draw.rect(surf, (60, 40, 0), (250, y - 8, 780, 38))
            if it in C.ACTIONS:
                surf.blit(ui.text(C.ACTION_NAMES[it], 16, col), (290, y + 2))
                if sel and self.waiting:
                    v = ui.text('TECLA O BOTÓN...' if (self.t // 15) % 2 else '', 14, C.CYAN)
                    surf.blit(v, (1010 - v.get_width(), y + 2))
                else:
                    v = ui.text(' / '.join(key_name(k) for k in ctl[it]) or '---', 16, C.CYAN)
                    surf.blit(v, (840 - v.get_width(), y + 2))
                    if it in pc:
                        pv = ', '.join(gamepad.button_name(b) for b in pc[it]) or '---'
                    else:
                        pv = {'izquierda': 'CRUCETA/STICK', 'derecha': 'CRUCETA/STICK', 'arriba': 'CRUCETA/STICK',
                              'abajo': 'CRUCETA/STICK'}.get(it, '---')
                    w = ui.text(pv, 12, (120, 230, 160))
                    surf.blit(w, (1010 - w.get_width(), y + 4))
            else:
                surf.blit(ui.text('RESTAURAR PREDETERMINADOS' if it == 'restaurar' else 'VOLVER', 16, col), (290, y + 2))
        help_bar(surf, '↑↓ ELEGIR    ENTER: PRESIONÁ UNA TECLA O UN BOTÓN DEL MANDO    ESC VOLVER')
