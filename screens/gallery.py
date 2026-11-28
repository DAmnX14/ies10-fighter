"""PERSONAJES: galería con todas las animaciones, estadísticas y movimientos."""
import math
import pygame
import config as C
from game import assets, ui
from game.characters_data import CHARACTERS, move_list
from screens.common import Scene, nav, menu_background, help_bar, AnimPlayer
from screens.character_select import STAT_LABELS

ANIM_NAMES = {
    'idle': 'EN GUARDIA', 'caminar': 'CAMINAR', 'caminar_atras': 'RETROCEDER', 'saltar': 'SALTO',
    'saltar_adelante': 'SALTO ADELANTE', 'agacharse': 'AGACHARSE', 'bloquear': 'BLOQUEO',
    'bloquear_agachado': 'BLOQUEO BAJO', 'presentacion': 'PRESENTACIÓN', 'golpe': 'PUÑETAZO',
    'patada': 'PATADA', 'golpe_fuerte': 'GOLPE FUERTE', 'patada_fuerte': 'PATADA FUERTE',
    'golpe_agachado': 'GOLPE AGACHADO', 'patada_agachado': 'BARRIDA', 'patada_aerea': 'PATADA AÉREA',
    'recibir_golpe': 'RECIBIR GOLPE', 'caida': 'CAÍDA', 'levantarse': 'LEVANTARSE', 'victoria': 'VICTORIA',
    'derrota': 'DERROTA', 'especial_1': 'ESPECIAL 1', 'especial_2': 'ESPECIAL 2', 'ultimate_1': 'ULTIMATE 1',
    'ultimate_2': 'ULTIMATE 2', 'ultimate_3': 'ULTIMATE 3',
}


class GalleryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.audio = game.audio
        self.audio.music('musica_seleccion')
        self.ci = 0
        self.ai = 0
        self.anims = list(assets.character(C.CHARACTERS[0]).meta['animations'].keys())
        self.player = AnimPlayer(C.CHARACTERS[0], self.anims[0])

    def name(self):
        return C.CHARACTERS[self.ci]

    def reset_player(self):
        self.anims = list(assets.character(self.name()).meta['animations'].keys())
        self.ai %= len(self.anims)
        self.player = AnimPlayer(self.name(), self.anims[self.ai], True)
        an = self.anims[self.ai]
        if an.startswith('especial') or an.startswith('ultimate'):
            self.audio.voice(self.name(), an)

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_F8:
            # inspector de animaciones (debug)
            from screens.anim_debug import AnimDebugScene
            self.game.change(lambda: AnimDebugScene(self.game, self.ci, self.ai), instant=True)
            return
        a = nav(e)
        if a == 'left':
            self.ci = (self.ci - 1) % len(C.CHARACTERS); self.audio.play('menu_mover'); self.reset_player()
            self.audio.announce(f'loc_{self.name()}')
        elif a == 'right':
            self.ci = (self.ci + 1) % len(C.CHARACTERS); self.audio.play('menu_mover'); self.reset_player()
            self.audio.announce(f'loc_{self.name()}')
        elif a == 'up':
            self.ai = (self.ai - 1) % len(self.anims); self.audio.play('menu_mover'); self.reset_player()
        elif a == 'down':
            self.ai = (self.ai + 1) % len(self.anims); self.audio.play('menu_mover'); self.reset_player()
        elif a == 'ok':
            self.audio.voice(self.name(), 'grito_1')
        elif a == 'back':
            from screens.main_menu import TitleScene
            self.audio.play('menu_atras')
            self.game.change(lambda: TitleScene(self.game, True))

    def update(self):
        super().update()
        self.player.update()

    def draw(self, surf):
        n = self.name()
        d = CHARACTERS[n]
        menu_background(surf, self.t, tuple(c // 2 for c in d['color']))
        ui.blit_center(surf, ui.text_gradient('PERSONAJES', 40, extrude=5), C.WIDTH / 2, 46)
        # luchador
        x = 300
        glow = pygame.Surface((440, 560), pygame.SRCALPHA)
        for i in range(20):
            pygame.draw.ellipse(glow, d['color'] + (7,), (i * 11, i * 14, 440 - i * 22, 560 - i * 28))
        surf.blit(glow, (x - 220, 110))
        pygame.draw.ellipse(surf, (0, 0, 0), (x - 120, 636, 240, 30))
        self.player.draw(surf, x, 652, 1, 3)          # escala 3: no llega a la fila de retratos
        an = self.anims[self.ai]
        info = assets.character(n).info(an)
        ui.panel(surf, (60, 92, 480, 44), (0, 0, 0, 180), d['color'], 2)
        surf.blit(ui.text(f'▲▼ {ANIM_NAMES.get(an, an.upper())}', 13, C.YELLOW), (76, 106))
        fr = ui.text(f'{self.player.frame + 1}/{info["frames"]}', 12, C.WHITE)
        surf.blit(fr, (526 - fr.get_width(), 107))
        # ficha
        px = 640
        ui.panel(surf, (px, 92, 590, 560), (0, 0, 20, 200), d['color'], 3)
        nm = ui.text_gradient(d['display'], 36, (255, 255, 255), d['color'], extrude=4)
        surf.blit(nm, (px + 20, 108))
        surf.blit(ui.text_outline(d['title'], 13, C.YELLOW), (px + 24, 160))
        surf.blit(ui.text('«' + d['quote'] + '»', 10, C.WHITE), (px + 24, 190))
        for i, (k, lab) in enumerate(STAT_LABELS):
            y = 220 + i * 24
            surf.blit(ui.text(lab, 11, C.WHITE), (px + 24, y + 2))
            ui.stat_bar(surf, px + 190, y, 200, 14, d['stats'][k], 10, d['color'])
        surf.blit(ui.text(f'VIDA: {d["health"]}', 11, C.CYAN), (px + 420, 222))
        surf.blit(ui.text('MOVIMIENTOS', 13, C.YELLOW), (px + 24, 352))
        for j, (mname, inp) in enumerate(move_list(n)):
            y = 376 + j * 20
            col = C.YELLOW if j >= 8 else C.WHITE
            surf.blit(ui.text(mname, 10, col), (px + 24, y))
            t = ui.text(inp, 9, (170, 220, 255))
            surf.blit(t, (px + 570 - t.get_width(), y + 1))
        # selector inferior
        for i, c in enumerate(C.CHARACTERS):
            # 10 retratos dentro del ancho del panel izquierdo (no se meten debajo de la ficha)
            r = pygame.Rect(64 + i * 48, 148, 42, 42)
            pygame.draw.rect(surf, C.YELLOW if i == self.ci else (40, 40, 60), r.inflate(6, 6))
            surf.blit(assets.character(c).portrait_at(42), r.topleft)
        help_bar(surf, '← → PERSONAJE    ▲▼ ANIMACIÓN    ENTER GRITO    F8 INSPECTOR    ESC VOLVER')
