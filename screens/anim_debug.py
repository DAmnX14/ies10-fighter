"""Inspector de animaciones (debug). Se abre con F8 desde PERSONAJES.

Teclas:
  ← →  personaje        ↑ ↓  animación        ESPACIO  pausa / reproducir
  , .  cuadro anterior / siguiente (en pausa)  R  reiniciar
  - +  velocidad (x0.25 … x2)                   F  mirar a la izquierda / derecha
  ESC  volver
Muestra el cuadro a escala x3 con el ancla, la línea del suelo, el rectángulo del
sprite (azul), la hurtbox (verde), las articulaciones (amarillo), y abajo la tira
original completa con el recorte de cada cuadro. Los cuadros que tocan el borde del
lienzo (recorte incorrecto) se marcan en rojo.
"""
import pygame
import config as C
from game import assets, ui
from screens.common import Scene, help_bar

SPEEDS = [0.25, 0.5, 1.0, 1.5, 2.0]


class AnimDebugScene(Scene):
    def __init__(self, game, ci=0, ai=0):
        super().__init__(game)
        self.ci, self.ai = ci, ai
        self.paused = False
        self.si = 2
        self.facing = 1
        self.reset()

    # ------------------------------------------------------------ estado
    def spr(self):
        return assets.character(C.CHARACTERS[self.ci])

    def anims(self):
        return list(self.spr().meta['animations'].keys())

    def reset(self):
        self.ai %= len(self.anims())
        self.frame = 0
        self.acc = 0.0
        self._strip = None

    def anim(self):
        return self.anims()[self.ai]

    def info(self):
        return self.spr().info(self.anim())

    def clipped(self, i):
        x0, y0, x1, y1 = self.info()['bbox'][i]
        s = self.spr()
        return x0 <= 0 or y0 <= 0 or x1 >= s.fw or y1 >= s.fh

    # ------------------------------------------------------------ entrada
    def handle_event(self, e):
        if e.type != pygame.KEYDOWN:
            return
        k = e.key
        n = self.info()['frames']
        if k == pygame.K_ESCAPE:
            from screens.gallery import GalleryScene
            self.game.change(lambda: GalleryScene(self.game), instant=True)
        elif k == pygame.K_LEFT:
            self.ci = (self.ci - 1) % len(C.CHARACTERS); self.reset()
        elif k == pygame.K_RIGHT:
            self.ci = (self.ci + 1) % len(C.CHARACTERS); self.reset()
        elif k == pygame.K_UP:
            self.ai -= 1; self.reset()
        elif k == pygame.K_DOWN:
            self.ai += 1; self.reset()
        elif k == pygame.K_SPACE:
            self.paused = not self.paused
        elif k == pygame.K_PERIOD:
            self.paused = True; self.frame = (self.frame + 1) % n
        elif k == pygame.K_COMMA:
            self.paused = True; self.frame = (self.frame - 1) % n
        elif k == pygame.K_r:
            self.frame = 0; self.acc = 0.0
        elif k in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
            self.si = min(len(SPEEDS) - 1, self.si + 1)
        elif k in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.si = max(0, self.si - 1)
        elif k == pygame.K_f:
            self.facing = -self.facing

    def update(self):
        super().update()
        if self.paused:
            return
        info = self.info()
        dur = max(1, info['dur'] / self.spr().profile.anim_speed)
        self.acc += SPEEDS[self.si]
        while self.acc >= dur:
            self.acc -= dur
            self.frame += 1
            if self.frame >= info['frames']:
                self.frame = 0

    # ------------------------------------------------------------ dibujo
    def strip(self):
        if self._strip is None:
            path = assets.os.path.join(C.CHAR_DIR, C.CHARACTERS[self.ci], self.info()['file'])
            self._strip = assets.image(path)
        return self._strip

    def draw(self, surf):
        surf.fill((26, 24, 40))
        spr, info, an = self.spr(), self.info(), self.anim()
        rnd = spr.renderer
        prof = spr.profile
        # cuadro grande
        ax, ay = 330, 520
        pygame.draw.line(surf, (255, 0, 255), (60, ay), (600, ay), 1)
        rnd.draw(surf, ax, ay, an, self.frame, self.facing)
        r = rnd.sprite_rect(ax, ay, self.facing, an, self.frame)
        pygame.draw.rect(surf, (80, 140, 255), r, 1)
        pygame.draw.rect(surf, (0, 255, 0), rnd.hurtbox(ax, ay, self.facing, an, self.frame), 2)
        for j, (jx, jy) in info['joints'][self.frame].items():
            x, y = rnd.to_world(ax, ay, self.facing, jx, jy, an, self.frame)
            pygame.draw.circle(surf, (255, 220, 0), (int(x), int(y)), 3)
        pygame.draw.line(surf, (255, 255, 255), (ax - 10, ay), (ax + 10, ay), 2)
        pygame.draw.line(surf, (255, 255, 255), (ax, ay - 10), (ax, ay + 10), 2)
        # datos
        g = rnd.geom(an, self.frame)
        x0, y0, x1, y1 = info['bbox'][self.frame]
        lines = [
            f'{C.CHARACTERS[self.ci].upper()}  ·  {an}',
            f'CUADRO {self.frame + 1}/{info["frames"]}   {info["dur"]} ticks/cuadro ({60 / info["dur"]:.1f} fps)',
            f'BUCLE: {"SÍ" if info["loop"] else "NO"}   VELOCIDAD x{SPEEDS[self.si]}   {"PAUSA" if self.paused else "REPRODUCIENDO"}',
            f'ESCALA x{prof.scale}   ANCLA {prof.anchor}   OFFSET ({prof.offset_x},{prof.offset_y})',
            f'RECORTE ({x0},{y0})-({x1},{y1})  {x1 - x0}x{y1 - y0} px',
            f'PIES: {"SUELO" if g.grounded else "AIRE"}   CORRECCIÓN {g.fix_y:+d} px',
        ]
        for i, ln in enumerate(lines):
            surf.blit(ui.text(ln, 11, C.WHITE if i else C.YELLOW), (640, 60 + i * 24))
        if self.clipped(self.frame):
            surf.blit(ui.text_outline('¡CUADRO CORTADO EN EL BORDE!', 14, C.RED), (640, 220))
        # tira original con el recorte de cada cuadro
        st = self.strip()
        n = info['frames']
        k = min(1.0, (C.WIDTH - 40) / st.get_width(), 90 / st.get_height())
        th = int(st.get_height() * k)
        small = pygame.transform.scale(st, (int(st.get_width() * k), th))
        y = C.HEIGHT - 44 - th
        pygame.draw.rect(surf, (60, 60, 80), (20, y, small.get_width(), th))
        surf.blit(small, (20, y))
        fw = spr.fw * k
        for i in range(n):
            bx0, by0, bx1, by1 = info['bbox'][i]
            col = C.RED if self.clipped(i) else ((255, 255, 0) if i == self.frame else (90, 90, 120))
            pygame.draw.rect(surf, col, (20 + i * fw, y, fw, th), 2 if i == self.frame else 1)
            pygame.draw.rect(surf, (80, 140, 255), (20 + i * fw + bx0 * k, y + by0 * k, (bx1 - bx0) * k, (by1 - by0) * k), 1)
        help_bar(surf, '←→ PERSONAJE  ↑↓ ANIMACIÓN  ESPACIO PAUSA  , . CUADRO  -/+ VELOCIDAD  F GIRAR  R REINICIO  ESC')
