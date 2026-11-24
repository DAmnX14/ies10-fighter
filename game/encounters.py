"""Escenas de encuentro antes de la primera ronda, según quiénes se enfrentan.

- PARADA y PANTOJA (pareja): se acercan enamorados, corazones.
- NICO y ANGEL: se dan un abrazo antes de pelear.
- PEDRO con EMI, NICO o LUCIANO: saludo de amistad, bien amigable.
- DENIS y NEHUEN (River - Boca): cara a cara, rayos de rivalidad, "SUPERCLÁSICO".
- Cualquiera de los nuevos (ANGEL, FACU, PEDRO, EMI, DENIS) contra PARADA: todos lo odian.

Cada escena es una línea de tiempo: los dos caminan hacia el centro, hacen su pose
con efectos y frases, y vuelven a su lugar. Se puede saltear con ACEPTAR / START.
"""
import math
import random
import pygame
import config as C
from game import assets
from game.particles import SpriteFX, Ring, FloatText

NEW_CHARS = ('angel', 'facu', 'pedro', 'emi', 'denis')


def pick(a, b):
    """Devuelve (tipo, protagonista) del encuentro entre a y b, o None."""
    pair = {a, b}
    if pair == {'parada', 'pantoja'}:
        return 'amor', None
    if pair == {'nico', 'angel'}:
        return 'abrazo', None
    if pair == {'denis', 'nehuen'}:
        return 'rival', None
    if 'pedro' in pair and pair & {'emi', 'nico', 'luciano'}:
        return 'saludo', 'pedro'
    if 'parada' in pair and pair & set(NEW_CHARS):
        return 'odio', (a if a != 'parada' else b)
    return None


class FloatSprite:
    """Efecto que sube flotando y se desvanece (corazones, bronca, brillos)."""

    def __init__(self, name, x, y, vy=-1.6, life=70, scale=1.0, wobble=1.5):
        fx = assets.effects()
        self.frames = fx.frames[name]
        self.dur = fx.meta[name]['dur']
        self.x, self.y, self.vy, self.life, self.max = x, y, vy, life, life
        self.scale = scale
        self.wobble = wobble
        self.t = random.random() * 6

    def update(self):
        self.t += 1
        self.life -= 1
        self.y += self.vy
        self.x += math.sin(self.t * 0.12) * self.wobble
        return self.life > 0

    def draw(self, surf, cam):
        img = self.frames[int(self.t // self.dur) % len(self.frames)]
        if self.scale != 1.0:
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
        if self.life < 20:
            img = img.copy(); img.set_alpha(int(255 * self.life / 20))
        x, y = cam.to_screen(self.x, self.y)
        surf.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))


# configuración por tipo: distancia final, pose, duración de la pose (ticks), cartel
SCENES = {
    'amor': dict(dist=170, pose=('enamorado', 'enamorado'), hold=150, banner=('¡LOS ENAMORADOS!', (255, 90, 160))),
    'abrazo': dict(dist=120, pose=('abrazo', 'abrazo'), hold=130, banner=('ABRAZO DE AMIGOS', (120, 220, 255))),
    'saludo': dict(dist=190, pose=('saludo', 'saludo'), hold=130, banner=('¡BUENA ONDA!', (255, 230, 90))),
    'rival': dict(dist=200, pose=('provocar', 'provocar'), hold=160, banner=('¡SUPERCLÁSICO!', (255, 255, 255))),
    'odio': dict(dist=230, pose=('enojado', 'confundido'), hold=160, banner=('¡TODOS CONTRA PARADA!', (255, 60, 60))),
}
WALK = 55          # ticks caminando hacia el centro
BACK = 40          # ticks volviendo


class Encounter:
    def __init__(self, match, kind, who):
        self.m = match
        self.kind = kind
        self.who = who
        self.cfg = SCENES[kind]
        self.t = 0
        p1, p2 = match.p1, match.p2
        self.start = (p1.x, p2.x)
        mid = (p1.x + p2.x) / 2
        d = self.cfg['dist']
        self.target = (mid - d / 2, mid + d / 2)
        self.done = False
        self.skipped = False
        for f in (p1, p2):
            f.state = 'encounter'          # lo anima la escena, no el luchador
            f.set_anim('caminar')

    # ---------------------------------------------------------------- utilidades
    def fighters(self):
        return self.m.p1, self.m.p2

    def pose_for(self, f):
        a, b = self.cfg['pose']
        if self.kind == 'odio':
            return a if f.name == self.who else b
        return a if f is self.m.p1 else b

    def speak(self, f, key):
        self.m.audio.voice(f.name, key)

    def head(self, f):
        return f.x + 10 * f.facing, f.y - 400

    def skip(self):
        if not self.done:
            self.skipped = True
            self.finish()

    def finish(self):
        p1, p2 = self.fighters()
        p1.x, p2.x = self.start
        for f in (p1, p2):
            f.state = 'intro'
            f.set_anim('idle')
            f.facing = 1 if f is p1 else -1
        self.done = True

    # ---------------------------------------------------------------- línea de tiempo
    def update(self):
        if self.done:
            return
        m = self.m
        p1, p2 = self.fighters()
        t = self.t = self.t + 1
        hold = self.cfg['hold']
        if t <= WALK:
            k = t / WALK
            e = 1 - (1 - k) ** 2
            p1.x = self.start[0] + (self.target[0] - self.start[0]) * e
            p2.x = self.start[1] + (self.target[1] - self.start[1]) * e
            for f in (p1, p2):
                f.step_anim()
            if t == WALK:
                for f in (p1, p2):
                    f.set_anim(self.pose_for(f))
                txt, col = self.cfg['banner']
                m.set_banner(txt, col, hold - 10, 46)
                self.on_pose()
        elif t <= WALK + hold:
            for f in (p1, p2):
                f.step_anim()
            self.during(t - WALK)
        elif t <= WALK + hold + BACK:
            if t == WALK + hold + 1:
                for f in (p1, p2):
                    f.set_anim('caminar_atras')
            k = (t - WALK - hold) / BACK
            e = k * k
            p1.x = self.target[0] + (self.start[0] - self.target[0]) * e
            p2.x = self.target[1] + (self.start[1] - self.target[1]) * e
            for f in (p1, p2):
                f.step_anim()
        else:
            self.finish()

    def on_pose(self):
        m = self.m
        p1, p2 = self.fighters()
        mid = (p1.x + p2.x) / 2
        k = self.kind
        if k == 'amor':
            m.audio.play('corazones')
            self.speak(self._by('pantoja'), 'amor')
        elif k == 'abrazo':
            m.audio.play('amistad')
            self.speak(self._by('nico'), 'abrazo')
            m.fx.add(Ring(mid, p1.y - 170, (150, 220, 255), 10, 220, 24, 6))
        elif k == 'saludo':
            m.audio.play('amistad')
            self.speak(self._by('pedro'), 'saludo')
        elif k == 'rival':
            m.audio.play('rival')
            m.camera.shake(6, 20)
            self.speak(self._by('denis'), 'rival')
            m.fx.add(SpriteFX('rayo', mid, m.stage.ground_y - 262, 1, loops=4))
        elif k == 'odio':
            m.audio.play('bronca')
            self.speak(self._by(self.who), 'odio')
            m.camera.shake(4, 14)

    def _by(self, name):
        p1, p2 = self.fighters()
        return p1 if p1.name == name else p2

    def during(self, u):
        m = self.m
        p1, p2 = self.fighters()
        mid = (p1.x + p2.x) / 2
        k = self.kind
        if k == 'amor' and u % 9 == 0:
            x = mid + random.uniform(-90, 90)
            m.fx.add(FloatSprite('corazon', x, p1.y - random.uniform(300, 420), -1.4, 80, random.choice((0.7, 0.9, 1.1))))
        if k == 'amor' and u == 70:
            self.speak(self._by('parada'), 'amor')
        if k == 'abrazo':
            if u % 12 == 0:
                m.fx.add(FloatSprite('brillo', mid + random.uniform(-60, 60), p1.y - random.uniform(330, 430),
                                     -1.0, 50, 0.8, 0.8))
            if u == 60:
                self.speak(self._by('angel'), 'abrazo') if 'angel' in (p1.name, p2.name) else None
        if k == 'saludo':
            if u % 14 == 0:
                m.fx.add(FloatSprite('brillo', mid + random.uniform(-50, 50), p1.y - random.uniform(330, 430),
                                     -1.0, 50, 0.8, 0.8))
            if u == 65:
                other = p2 if p1.name == 'pedro' else p1
                self.speak(other, 'saludo')
        if k == 'rival':
            if u % 10 == 0:
                for f in (p1, p2):
                    hx, hy = self.head(f)
                    m.fx.add(FloatSprite('enojo', hx + random.uniform(-30, 30), hy, -0.8, 34, 0.9, 0.5))
            if u in (30, 90):
                m.fx.add(SpriteFX('rayo', mid, m.stage.ground_y - 262, 1, loops=3))
                m.camera.shake(5, 10)
            if u == 80:
                self.speak(self._by('nehuen'), 'rival')
            if u == 40:
                m.fx.add(FloatText(p1.x, p1.y - 380, '¡BOSTERO!' if p1.name == 'denis' else '¡GALLINA!',
                                   p1.color, 22, 70))
            if u == 100:
                m.fx.add(FloatText(p2.x, p2.y - 380, '¡BOSTERO!' if p2.name == 'denis' else '¡GALLINA!',
                                   p2.color, 22, 70))
        if k == 'odio':
            hater = self._by(self.who)
            if u % 8 == 0:
                hx, hy = self.head(hater)
                m.fx.add(FloatSprite('enojo', hx + random.uniform(-40, 40), hy, -0.9, 34, 0.9, 0.5))
            if u == 85:
                self.speak(self._by('parada'), 'odio')
                pa = self._by('parada')
                m.fx.add(FloatText(pa.x, pa.y - 390, '¿Y AHORA QUÉ HICE?', pa.color, 16, 80))
