"""
Definición de todas las animaciones como keyframes de pose.

Parámetros de pose (todos opcionales, el resto queda en reposo):
  rx, ry   desplazamiento de pelvis (u = 1% de la altura del personaje; y+ abajo)
  lean     inclinación del torso (+ hacia adelante)      head  giro de cabeza
  rot      rotación de todo el cuerpo (volteretas, caídas)
  lrel     0 = pies anclados al suelo, 1 = piernas siguen al cuerpo (aire)
  fh / bh  mano delantera / trasera en polar (ángulo, extensión 0..1) local al torso
  ff / bf  desplazamiento del tobillo (u)   ff_abs / bf_abs  posición absoluta (u)
  ffa/bfa  ángulo del pie       sx, sy  escala (squash & stretch)
  prop     objeto dibujado (p. ej. 'guitar')

Cada animación: dict(keys=[(keyframe, cuadros_hasta_aquí), ...], dur=ticks por cuadro,
loop=bool). El primer elemento usa 1 cuadro.
"""
import math

GUARD_F = (-62, 0.55)   # guardia genérica (mano adelantada)
GUARD_B = (-40, 0.42)


def K(n, **kw):
    return (kw, n)


def cyc(n, fn):
    return [(fn(i / n), 1) for i in range(n)]


# ------------------------------------------------------------ básicos
def idle(t):
    s = math.sin(t * 2 * math.pi)
    return dict(ry=1.2 + 1.2 * s, lean=0.8 * s, head=-0.8 * s,
                fh_off=(0.0, 0.025 * s), bh_off=(0.0, 0.03 * s))


def walk(direction):
    def f(t):
        a = t * 2 * math.pi
        s, c = math.sin(a), math.cos(a)
        st = 7 * direction
        return dict(ff=(st * s, -5 * max(0, c)), bf=(st * s * -1 + 0, -5 * max(0, -c)),
                    ry=1.5 + 1.5 * abs(s), lean=2 * direction + 1.5 * s,
                    fh_off=(0.02 * s, 0.02 * c), bh_off=(-0.02 * s, 0.02 * c), head=-1)
    return f


ANIMS = {
    'idle': dict(func=(8, idle), dur=7, loop=True),
    'caminar': dict(func=(8, walk(1)), dur=5, loop=True),
    'caminar_atras': dict(func=(8, walk(-1)), dur=6, loop=True),
    'saltar': dict(keys=[
        K(1, ry=8, lean=6, sy=0.97),
        K(1, ry=-2, sy=1.03, fh=(-58, 0.6), lean=-2),
        K(1, lrel=1, ry=-6, bf=(4, -16), ff=(-2, -20), fh=(-55, 0.55), lean=2),
        K(2, lrel=1, ry=-8, bf=(6, -22), ff=(-4, -26), fh=(-50, 0.5), lean=4),
        K(1, lrel=1, ry=-4, bf=(2, -10), ff=(0, -12)),
        K(1, lrel=1, ry=0),
        K(1, ry=8, lean=4, sy=0.97),
    ], dur=6),
    'saltar_adelante': dict(keys=[
        K(1, ry=8, lean=8, sy=0.97),
        K(1, ry=-4, lrel=1, rot=20, bf=(6, -18), ff=(-6, -22)),
        K(1, ry=-14, lrel=1, rot=90, bf=(8, -26), ff=(-8, -30), fh=(40, 0.5), bh=(50, 0.5)),
        K(1, ry=-16, lrel=1, rot=180, bf=(8, -26), ff=(-8, -30), fh=(40, 0.5), bh=(50, 0.5)),
        K(1, ry=-14, lrel=1, rot=270, bf=(8, -26), ff=(-8, -30), fh=(40, 0.5), bh=(50, 0.5)),
        K(1, ry=-6, lrel=1, rot=345, bf=(4, -14), ff=(-2, -16)),
        K(1, ry=-2, lrel=1, rot=360),
        K(1, ry=6, rot=360, lean=4),
    ], dur=6),
    'agacharse': dict(keys=[
        K(1, ry=12, bf=(-3, 0), ff=(3, 0), lean=5),
        K(1, ry=24, bf=(-6, 0), ff=(6, 0), lean=9, fh_off=(0, 0.05)),
        K(1, ry=28, bf=(-7, 0), ff=(7, 0), lean=10, fh_off=(0, 0.06), bh_off=(0, 0.04)),
    ], dur=3),
    'bloquear': dict(keys=[
        K(1, fh=(-70, 0.5), bh=(-45, 0.45), lean=-2),
        K(1, fh=(-85, 0.42), bh=(-62, 0.38), lean=-5, ry=3, head=6, rx=-1),
        K(1, fh=(-88, 0.40), bh=(-66, 0.36), lean=-6, ry=4, head=8, rx=-2),
    ], dur=3),
    'bloquear_agachado': dict(keys=[
        K(1, ry=18, bf=(-4, 0), ff=(4, 0), lean=4, fh=(-75, 0.45), bh=(-55, 0.42)),
        K(1, ry=20, bf=(-5, 0), ff=(5, 0), lean=2, fh=(-85, 0.4), bh=(-65, 0.36), head=8, rx=-1),
    ], dur=3),
    'presentacion': dict(keys=[
        K(1, ry=2),
        K(1, ry=4, lean=6, head=8, fh=(60, 0.5), bh=(70, 0.5)),
        K(1, ry=6, lean=10, head=12, fh=(80, 0.6), bh=(85, 0.6)),
        K(1, ry=2, lean=-2, head=-6, fh=(-60, 0.5), bh=(-40, 0.45)),
        K(1, ry=0, lean=6, fh=(-4, 1.1), rx=2),
        K(1, ry=0, lean=2, fh=(-50, 0.5), rx=1),
        K(1, ry=0, lean=10, bh=(-4, 1.25), tw=1, rx=4),
        K(1, ry=0, lean=3, rx=1),
        K(1, ry=-1, lean=-6, bh=(-95, 1.0), head=-12),
        K(1, ry=-2, lean=-7, bh=(-97, 1.0), head=-14),
        K(1, ry=0, lean=-2, bh=(-50, 0.6)),
        K(1),
    ], dur=6),
    'golpe': dict(keys=[
        K(1, fh=(-30, 0.45), lean=3),
        K(1, fh=(-8, 0.85), lean=7, rx=2, head=2),
        K(1, fh=(-4, 1.15), lean=9, rx=3, head=3),
        K(1, fh=(-6, 0.9), lean=8, rx=3),
        K(1, fh=(-40, 0.55), lean=3, rx=1),
    ], dur=3),
    'patada': dict(keys=[
        K(1, ff=(4, -10), lean=-4, fh=(-60, 0.5)),
        K(1, ff_abs=(28, -36), ffa=-20, lean=-10, rx=-1),
        K(1, ff_abs=(46, -40), ffa=-35, lean=-14, rx=-2, fh=(-60, 0.5)),
        K(1, ff_abs=(48, -40), ffa=-35, lean=-14, rx=-2, fh=(-60, 0.5)),
        K(1, ff_abs=(30, -26), ffa=-15, lean=-8),
        K(1, ff=(2, -4), lean=-2),
    ], dur=3),
    'golpe_fuerte': dict(keys=[
        K(1, lean=-6, fh=(-70, 0.4), rx=-2, head=-2, ry=2),
        K(1, lean=-9, fh=(-80, 0.32), rx=-3, ry=3, bf=(-2, 0)),
        K(1, lean=10, bh=(-12, 0.9), rx=5, bf=(4, 0), fh=(-70, 0.45), head=4, tw=0.6),
        K(1, lean=14, bh=(-4, 1.3), rx=9, bf=(7, 0), fh=(-80, 0.4), head=6, tw=1),
        K(1, lean=14, bh=(-4, 1.3), rx=9, bf=(7, 0), fh=(-80, 0.4), head=6, tw=1),
        K(1, lean=10, bh=(-20, 0.8), rx=6, bf=(4, 0), tw=0.5),
        K(1, lean=3, rx=2),
    ], dur=4),
    'patada_fuerte': dict(keys=[
        K(1, lean=-6, ff=(2, -8), rx=-2),
        K(1, lean=-14, ff_abs=(20, -48), ffa=-30, rx=-3, fh=(-90, 0.5)),
        K(1, lean=-24, ff_abs=(38, -72), ffa=-60, rx=-4, fh=(-80, 0.5), bh=(-60, 0.45), head=10),
        K(1, lean=-26, ff_abs=(44, -76), ffa=-65, rx=-4, fh=(-80, 0.5), bh=(-60, 0.45), head=12),
        K(1, lean=-26, ff_abs=(44, -76), ffa=-65, rx=-4, fh=(-80, 0.5), bh=(-60, 0.45), head=12),
        K(1, lean=-18, ff_abs=(34, -52), ffa=-40, rx=-3),
        K(1, lean=-8, ff_abs=(24, -20), ffa=-10, rx=-1),
        K(1, lean=-2, ff=(2, -2)),
    ], dur=4),
    'golpe_agachado': dict(keys=[
        K(1, ry=20, bf=(-5, 0), ff=(5, 0), lean=7, fh=(-10, 0.5)),
        K(1, ry=20, bf=(-5, 0), ff=(5, 0), lean=12, fh=(10, 1.0), rx=3),
        K(1, ry=20, bf=(-5, 0), ff=(5, 0), lean=12, fh=(10, 1.0), rx=3),
        K(1, ry=20, bf=(-5, 0), ff=(5, 0), lean=8, fh=(-20, 0.6)),
    ], dur=3),
    'patada_agachado': dict(keys=[
        K(1, ry=22, bf=(-6, 0), ff=(5, 0), lean=6),
        K(1, ry=26, bf=(-8, 0), ff_abs=(40, -3), ffa=-5, lean=8, rx=-2),
        K(1, ry=28, bf=(-10, 0), ff_abs=(56, -3), ffa=-10, lean=10, rx=-4),
        K(1, ry=28, bf=(-10, 0), ff_abs=(56, -3), ffa=-10, lean=10, rx=-4),
        K(1, ry=26, bf=(-8, 0), ff=(14, 0), lean=8),        # recoge la pierna sin pararse
        K(1, ry=24, bf=(-6, 0), ff=(7, 0), lean=7),
    ], dur=4),
    'patada_aerea': dict(keys=[
        K(1, lrel=1, ry=-8, bf=(6, -22), ff=(-4, -26)),
        K(1, lrel=1, ry=-8, bf=(6, -24), ff=(14, -16), ffa=-20, lean=-8),
        K(1, lrel=1, ry=-8, bf=(4, -24), ff=(26, -6), ffa=-40, lean=-14, fh=(-100, 0.5)),
        K(1, lrel=1, ry=-8, bf=(4, -24), ff=(26, -6), ffa=-40, lean=-14, fh=(-100, 0.5)),
    ], dur=4, loop=False),
    'recibir_golpe': dict(keys=[
        K(1, lean=-14, head=-16, rx=-4, ry=2, fh=(15, 0.6), sx=0.98),
        K(1, lean=-20, head=-22, rx=-6, ry=4, fh=(35, 0.55), bf=(-3, 0)),
        K(1, lean=-12, head=-10, rx=-4, ry=3, fh=(-10, 0.55), bf=(-2, 0)),
        K(1, lean=-4, head=-3, rx=-1, ry=1, fh=(-45, 0.55)),
    ], dur=4),
    'caida': dict(keys=[
        K(1, lean=-18, head=-20, rx=-4, fh=(-80, 0.5), bh=(-110, 0.55)),
        K(1, lrel=1, rot=-25, ry=-4, rx=-8, fh=(-85, 0.5), bh=(-130, 0.6), ff=(6, -6)),
        K(1, lrel=1, rot=-50, ry=4, rx=-12, fh=(-150, 0.7), bh=(-140, 0.6), ff=(8, -10)),
        K(1, lrel=1, rot=-72, ry=22, rx=-16, fh=(-160, 0.6), bh=(-150, 0.6), ff=(6, -8)),
        K(1, lrel=1, rot=-88, ry=38, rx=-18, fh=(180, 0.6), bh=(170, 0.6), head=-6),
        K(1, lrel=1, rot=-84, ry=33, rx=-19, fh=(175, 0.6), bh=(165, 0.6), ff=(4, -6)),
        K(1, lrel=1, rot=-90, ry=39, rx=-20, fh=(180, 0.6), bh=(170, 0.6), head=-8),
        K(1, lrel=1, rot=-90, ry=40, rx=-20, fh=(178, 0.6), bh=(172, 0.6), head=-8),
    ], dur=5),
    'levantarse': dict(keys=[
        K(1, lrel=1, rot=-90, ry=40, rx=-20, fh=(178, 0.6), bh=(172, 0.6), head=-8),
        K(1, lrel=1, rot=-60, ry=32, rx=-16, bh=(120, 0.8), fh=(150, 0.6), ff=(-6, -10)),
        K(1, lrel=0.6, rot=-30, ry=26, rx=-10, bh=(100, 0.9), ff=(-4, 0), bf=(-2, 0)),
        K(1, rot=-8, ry=20, rx=-4, lean=10, bf=(-5, 0), ff=(5, 0)),
        K(1, ry=8, lean=4),
        K(1, ry=2),
    ], dur=5),
    'victoria': dict(keys=[
        K(1, ry=4, lean=4),
        K(1, bh=(-60, 0.6), lean=-2, head=-4),
        K(1, bh=(-95, 1.0), lean=-6, head=-12, ry=-2),
        K(1, bh=(-92, 1.0), lean=-7, head=-14, ry=-3),
        K(1, bh=(-96, 1.0), lean=-5, head=-10, ry=-1),
        K(1, bh=(-92, 1.0), lean=-7, head=-14, ry=-3),
        K(1, bh=(-96, 1.0), lean=-5, head=-10, ry=-1),
        K(1, bh=(-92, 1.0), lean=-7, head=-14, ry=-3),
        K(1, bh=(-96, 1.0), lean=-5, head=-10, ry=-1),
        K(1, bh=(-94, 1.0), lean=-6, head=-12, ry=-2),
    ], dur=7),
    'derrota': dict(keys=[
        K(1, lean=-8, head=-10, rx=-3),
        K(1, lean=6, head=12, ry=8, fh=(60, 0.6), bh=(70, 0.6)),
        K(1, lean=14, head=20, ry=18, fh=(80, 0.8), bh=(85, 0.8), bf=(-4, 0), ff=(4, 0)),
        K(1, lean=20, head=26, ry=28, fh=(85, 0.9), bh=(88, 0.9), bf=(-8, 0), ff=(6, 0)),
        K(1, lean=24, head=30, ry=32, fh=(88, 0.95), bh=(90, 0.95), bf=(-10, 0), ff=(7, 0)),
        K(1, lean=22, head=28, ry=31, fh=(88, 0.95), bh=(90, 0.95), bf=(-10, 0), ff=(7, 0)),
        K(1, lean=24, head=32, ry=32, fh=(88, 0.95), bh=(90, 0.95), bf=(-10, 0), ff=(7, 0)),
        K(1, lean=24, head=32, ry=32, fh=(88, 0.95), bh=(90, 0.95), bf=(-10, 0), ff=(7, 0)),
    ], dur=8),
}


# ------------------------------------------------------------ especiales
def alt_punches(n, base_lean=10, height=-6):
    out = []
    for i in range(n):
        h = height + (i % 3 - 1) * 10
        if i % 2 == 0:
            out.append(K(1, fh=(h, 1.15), lean=base_lean, rx=5, head=3))
        else:
            out.append(K(1, fh=(h - 20, 0.5), bh_off=(0.2, 0.0), lean=base_lean + 5, rx=7, head=4))
    return out


SPECIALS = {
    # ------------------------------------------------ PANTOJA
    'pantoja': {
        # PANZAZO: embestida con la panza
        'especial_1': dict(keys=[
            K(1, lean=-6, ry=6, bh=(150, 0.6), fh=(160, 0.6)),
            K(1, lean=-14, ry=8, bh=(165, 0.7), fh=(170, 0.7), rx=-4),
            K(1, lean=-22, ry=2, bh=(175, 0.8), fh=(178, 0.8), rx=6, bf=(6, 0), sx=1.06),
            K(1, lean=-26, ry=0, bh=(175, 0.85), fh=(178, 0.85), rx=12, bf=(10, 0), ff=(6, -3), sx=1.1),
            K(1, lean=-26, ry=0, bh=(175, 0.85), fh=(178, 0.85), rx=12, bf=(10, 0), ff=(6, -3), sx=1.1),
            K(1, lean=-26, ry=0, bh=(175, 0.85), fh=(178, 0.85), rx=12, bf=(10, 0), ff=(6, -3), sx=1.1),
            K(1, lean=-16, ry=2, bh=(150, 0.6), rx=8, bf=(6, 0)),
            K(1, lean=-6, ry=2, rx=3),
            K(1),
        ], dur=4),
        # GRITO METALERO: cuernos al cielo + onda sonora
        'especial_2': dict(keys=[
            K(1, lean=4, ry=4, head=6),
            K(1, lean=-4, ry=2, bh=(-80, 0.7), head=-6),
            K(1, lean=-12, ry=0, bh=(-95, 1.0), fh=(20, 0.7), head=-18, sx=1.02),
            K(1, lean=-14, ry=-1, bh=(-97, 1.0), fh=(10, 0.95), head=-20),
            K(1, lean=-14, ry=-1, bh=(-93, 1.0), fh=(8, 1.0), head=-22),
            K(1, lean=-14, ry=-1, bh=(-97, 1.0), fh=(8, 1.0), head=-20),
            K(1, lean=-14, ry=-1, bh=(-93, 1.0), fh=(8, 1.0), head=-22),
            K(1, lean=-8, ry=1, bh=(-70, 0.7), fh=(-20, 0.7), head=-8),
            K(1, lean=-2, ry=1),
        ], dur=5),
        # TERREMOTO PANTOJA: salto gigante + golpe al suelo
        'ultimate_1': dict(keys=[
            K(1, ry=6, lean=4, bh=(-60, 0.6)),
            K(1, ry=18, lean=12, bh=(-100, 1.0), fh=(-80, 1.0), head=-14, bf=(-4, 0), ff=(4, 0)),
            K(1, ry=20, lean=14, bh=(-102, 1.0), fh=(-78, 1.0), head=-16, bf=(-4, 0), ff=(4, 0), sx=1.04, sy=0.94),
            K(1, ry=-6, lrel=1, sy=1.08, bh=(-100, 1.0), fh=(-85, 1.0), bf=(2, -8), ff=(0, -10)),
            K(1, ry=-10, lrel=1, bh=(-110, 1.0), fh=(-95, 1.0), bf=(6, -22), ff=(-4, -26), lean=-6),
            K(1, ry=-10, lrel=1, bh=(-120, 1.0), fh=(-100, 1.0), bf=(6, -24), ff=(-4, -28), lean=-10),
            K(1, ry=-10, lrel=1, bh=(-120, 1.0), fh=(-100, 1.0), bf=(6, -24), ff=(-4, -28), lean=-10),
            K(1, ry=-8, lrel=1, bh=(60, 1.0), fh=(70, 1.0), bf=(6, -22), ff=(-4, -26), lean=20, head=10),
            K(1, ry=-6, lrel=1, bh=(75, 1.0), fh=(80, 1.0), bf=(4, -18), ff=(-2, -20), lean=28, head=14),
            K(1, ry=22, bh=(80, 1.0), fh=(85, 1.0), lean=34, head=16, bf=(-8, 0), ff=(8, 0), sx=1.1, sy=0.9),
            K(1, ry=24, bh=(82, 1.0), fh=(86, 1.0), lean=36, head=18, bf=(-8, 0), ff=(8, 0), sx=1.08, sy=0.92),
            K(1, ry=24, bh=(82, 1.0), fh=(86, 1.0), lean=36, head=18, bf=(-8, 0), ff=(8, 0)),
            K(1, ry=16, bh=(40, 0.7), fh=(50, 0.7), lean=20, bf=(-6, 0), ff=(6, 0)),
            K(1, ry=6, lean=6, bh=(-90, 1.0), head=-10),
            K(1, ry=2, lean=-4, bh=(-95, 1.0), head=-14),
            K(1, ry=2),
        ], dur=5),
        # LLUVIA DE CACHETADAS: ráfaga de cachetadas + gancho final
        'ultimate_2': dict(keys=[
            K(1, ry=4, lean=-6, bh=(170, 0.5), fh=(160, 0.5)),
            K(1, ry=6, lean=-8, bh=(175, 0.5), fh=(165, 0.5), head=-6),
        ] + [K(1, **({'fh': (-30 + 25 * (i % 3), 1.0), 'bh': (150, 0.5)} if i % 2 == 0
                     else {'bh': (-20 + 25 * (i % 3), 1.0), 'fh': (150, 0.5)}),
               lean=10 + 3 * (i % 2), rx=6, head=4) for i in range(10)]
          + [
            K(1, ry=16, lean=10, bh=(100, 0.6), bf=(-4, 0), ff=(4, 0)),
            K(1, ry=-4, lean=-6, bh=(-80, 1.0), rx=8, head=-12, sy=1.05),
            K(1, ry=-6, lean=-10, bh=(-88, 1.0), rx=9, head=-16, sy=1.06),
            K(1, ry=-4, lean=-8, bh=(-88, 1.0), rx=8, head=-14),
            K(1, ry=0, lean=-2, bh=(-60, 0.7), rx=4),
            K(1),
        ], dur=4),
    },
    # ------------------------------------------------ PARADA
    'parada': {
        # RÁFAGA ESMERALDA: embestida veloz con puño
        'especial_1': dict(keys=[
            K(1, ry=8, lean=10, fh=(-20, 0.5), bf=(-4, 0)),
            K(1, ry=10, lean=16, fh=(-10, 0.4), bh=(160, 0.5), bf=(-8, 0)),
            K(1, ry=6, lean=26, fh=(0, 1.0), bh=(170, 0.7), bf=(-14, 0), ff=(10, -4), rx=10, sx=1.08),
            K(1, ry=6, lean=26, fh=(0, 1.0), bh=(170, 0.7), bf=(-14, 0), ff=(10, -4), rx=10, sx=1.08),
            K(1, ry=6, lean=26, fh=(0, 1.0), bh=(170, 0.7), bf=(-14, 0), ff=(10, -4), rx=10, sx=1.08),
            K(1, ry=6, lean=18, fh=(-10, 0.8), rx=8, bf=(-8, 0)),
            K(1, ry=3, lean=8, rx=3),
            K(1),
        ], dur=4),
        # PATADA HURACÁN: doble patada ascendente
        'especial_2': dict(keys=[
            K(1, ry=12, lean=8, bf=(-4, 0), ff=(4, 0)),
            K(1, ry=0, lrel=1, ff=(20, -26), ffa=-40, lean=-12, fh=(-80, 0.5), bh=(-140, 0.5)),
            K(1, ry=-4, lrel=1, ff=(28, -42), ffa=-70, lean=-24, fh=(-80, 0.5), bh=(-60, 0.45)),
            K(1, ry=-6, lrel=1, ff=(26, -46), ffa=-75, lean=-26, bf=(0, -14)),
            K(1, ry=-6, lrel=1, ff=(-2, -20), bf=(28, -40), bfa=-70, lean=-24, rot=-10),
            K(1, ry=-6, lrel=1, ff=(-2, -20), bf=(30, -46), bfa=-75, lean=-26, rot=-12),
            K(1, ry=-4, lrel=1, ff=(0, -14), bf=(14, -20), lean=-10),
            K(1, ry=-2, lrel=1, ff=(0, -6), bf=(0, -6)),
            K(1, ry=8, lean=6),
            K(1),
        ], dur=4),
        # MIL PIÑAS: ráfaga de puñetazos supersónica
        'ultimate_1': dict(keys=[
            K(1, ry=6, lean=-4, fh=(-70, 0.45), bh=(-50, 0.4), head=-4),
            K(1, ry=10, lean=-8, fh=(-80, 0.4), bh=(-60, 0.35), head=-8, sy=0.97),
        ] + alt_punches(14, 12) + [
            K(1, ry=8, lean=4, fh=(170, 0.4), bh=(170, 0.4)),
            K(1, ry=4, lean=22, fh=(-2, 1.0), bh=(4, 1.3), tw=1, rx=10, sx=1.06),
            K(1, ry=4, lean=22, fh=(-2, 1.0), bh=(4, 1.3), tw=1, rx=10, sx=1.06),
            K(1, ry=2, lean=10, fh=(-40, 0.6), rx=5),
            K(1),
        ], dur=3),
        # TORNADO VERDE: cruces relámpago + patada final
        'ultimate_2': dict(keys=[
            K(1, ry=14, lean=14, bf=(-6, 0), ff=(4, 0), fh=(170, 0.4), bh=(170, 0.4)),
            K(1, ry=16, lean=18, bf=(-8, 0), ff=(4, 0), fh=(175, 0.45), bh=(175, 0.45), sy=0.95),
            K(1, ry=8, lean=34, fh=(170, 0.8), bh=(175, 0.8), bf=(-16, 0), ff=(12, -4), rx=12, sx=1.12),
            K(1, ry=8, lean=30, fh=(10, 1.0), bh=(170, 0.7), bf=(-14, 0), ff=(10, -4), rx=12),
            K(1, ry=8, lean=34, fh=(170, 0.8), bh=(175, 0.8), bf=(-16, 0), ff=(12, -4), rx=12, sx=1.12),
            K(1, ry=8, lean=30, bh=(5, 1.3), tw=1, fh=(170, 0.7), bf=(-14, 0), ff=(10, -4), rx=12),
            K(1, ry=8, lean=34, fh=(170, 0.8), bh=(175, 0.8), bf=(-16, 0), ff=(12, -4), rx=12, sx=1.12),
            K(1, ry=8, lean=30, fh=(-10, 1.0), bh=(170, 0.7), bf=(-14, 0), ff=(10, -4), rx=12),
            K(1, ry=12, lean=10, bf=(-6, 0), ff=(4, 0)),
            K(1, ry=-2, lrel=1, ff=(20, -30), ffa=-50, lean=-16, fh=(-80, 0.5)),
            K(1, ry=-6, lrel=1, ff=(30, -50), ffa=-80, lean=-28, fh=(-85, 0.5), bh=(-60, 0.45), rot=-8),
            K(1, ry=-6, lrel=1, ff=(30, -52), ffa=-80, lean=-28, fh=(-85, 0.5), bh=(-60, 0.45), rot=-10),
            K(1, ry=-4, lrel=1, ff=(16, -24), lean=-14),
            K(1, ry=-2, lrel=1, ff=(2, -8)),
            K(1, ry=8, lean=6, bh=(-95, 1.0), head=-10),
            K(1),
        ], dur=4),
    },
    # ------------------------------------------------ NEHUEN
    'nehuen': {
        # ACORDE SÓNICO: rasguido de guitarra -> onda de notas
        'especial_1': dict(keys=[
            K(1, prop='guitar', fh=(-20, 0.85), bh=(40, 0.35), lean=-2),
            K(1, prop='guitar', fh=(-22, 0.88), bh=(-10, 0.42), lean=-4, head=-4),
            K(1, prop='guitar', fh=(-22, 0.88), bh=(60, 0.38), lean=4, head=6),
            K(1, prop='guitar', fh=(-22, 0.88), bh=(-12, 0.42), lean=-4, head=-4),
            K(1, prop='guitar', fh=(-24, 0.9), bh=(70, 0.4), lean=6, head=10, rx=2),
            K(1, prop='guitar', fh=(-24, 0.9), bh=(70, 0.4), lean=6, head=10, rx=2),
            K(1, prop='guitar', fh=(-20, 0.85), bh=(30, 0.38), lean=0),
            K(1),
        ], dur=5),
        # PATADA DEL PILUSO: patada voladora ascendente (anti-aérea)
        'especial_2': dict(keys=[
            K(1, ry=14, lean=10, bf=(-5, 0), ff=(5, 0)),
            K(1, ry=2, lrel=1, ff=(16, -30), ffa=-50, lean=-14, fh=(-130, 0.7)),
            K(1, ry=-6, lrel=1, ff=(14, -56), ffa=-90, lean=-24, fh=(-85, 0.5), bh=(150, 0.6), rot=-12, bf=(2, -8)),
            K(1, ry=-8, lrel=1, ff=(12, -60), ffa=-95, lean=-26, fh=(-85, 0.5), bh=(150, 0.6), rot=-18, bf=(2, -8)),
            K(1, ry=-8, lrel=1, ff=(12, -60), ffa=-95, lean=-26, fh=(-85, 0.5), bh=(150, 0.6), rot=-18, bf=(2, -8)),
            K(1, ry=-6, lrel=1, ff=(6, -26), lean=-10, rot=-6, bf=(4, -14)),
            K(1, ry=-2, lrel=1, ff=(0, -10), bf=(2, -10)),
            K(1, ry=8, lean=6),
            K(1),
        ], dur=4),
        # SOLO INFINITO: solo de guitarra devastador
        'ultimate_1': dict(keys=[
            K(1, ry=4, lean=-4, bh=(-90, 0.8), head=-10),
            K(1, ry=2, lean=-8, bh=(-100, 1.0), fh=(-60, 0.6), head=-16),
            K(1, prop='guitar', fh=(-30, 0.9), bh=(-60, 0.6), lean=-12, head=-18, ry=2),
            K(1, prop='guitar', fh=(-30, 0.9), bh=(50, 0.4), lean=6, head=14, ry=6),
        ] + [K(1, prop='guitar', fh=(-26 + (i % 2) * 6, 0.9), bh=((60 if i % 2 else -10), 0.42),
               lean=(8 if i % 2 else -6), head=(16 if i % 2 else -8), ry=(6 if i % 2 else 2),
               bf=(-6, 0), ff=(6, 0)) for i in range(8)] + [
            K(1, prop='guitar', fh=(-40, 0.95), bh=(-120, 0.9), lean=-14, head=-20, ry=-2, sy=1.04),
            K(1, prop='guitar', fh=(-40, 0.95), bh=(-120, 0.9), lean=-14, head=-20, ry=-2, sy=1.04),
            K(1, prop='guitar', fh=(-20, 0.85), bh=(30, 0.38)),
            K(1),
        ], dur=4),
        # METEORO PILUSO: salto altísimo + caída en picada
        'ultimate_2': dict(keys=[
            K(1, ry=8, lean=6, head=-6),
            K(1, ry=18, lean=12, bf=(-5, 0), ff=(5, 0), fh=(170, 0.6), bh=(170, 0.6), sy=0.94),
            K(1, ry=-2, lrel=1, sy=1.04, fh=(-105, 0.85), bh=(-100, 0.85), bf=(0, -6), ff=(0, -8)),
            K(1, ry=-10, lrel=1, rot=60, bf=(8, -26), ff=(-8, -30), fh=(40, 0.5), bh=(50, 0.5)),
            K(1, ry=-10, lrel=1, rot=150, bf=(8, -26), ff=(-8, -30), fh=(40, 0.5), bh=(50, 0.5)),
            K(1, ry=-10, lrel=1, rot=240, bf=(8, -26), ff=(-8, -30), fh=(40, 0.5), bh=(50, 0.5)),
            K(1, ry=-10, lrel=1, rot=330, bf=(8, -26), ff=(-8, -30), fh=(40, 0.5), bh=(50, 0.5)),
            K(1, ry=-8, lrel=1, rot=390, bf=(6, -24), ff=(24, 0), ffa=-30, lean=-10, fh=(-80, 0.5)),
            K(1, ry=-8, lrel=1, rot=395, bf=(6, -24), ff=(26, 2), ffa=-30, lean=-12, fh=(-80, 0.5)),
            K(1, ry=-8, lrel=1, rot=395, bf=(6, -24), ff=(26, 2), ffa=-30, lean=-12, fh=(-80, 0.5)),
            K(1, ry=-8, lrel=1, rot=395, bf=(6, -24), ff=(26, 2), ffa=-30, lean=-12, fh=(-80, 0.5)),
            K(1, ry=20, rot=360, lean=16, bf=(-8, 0), ff=(8, 0), bh=(90, 0.8), sx=1.06, sy=0.92),
            K(1, ry=20, rot=360, lean=16, bf=(-8, 0), ff=(8, 0), bh=(90, 0.8)),
            K(1, ry=8, rot=360, lean=4, bh=(-95, 1.0), head=-10),
            K(1, rot=360),
        ], dur=5),
    },
    # ------------------------------------------------ LUCIANO
    'luciano': {
        # CREDENCIAL VOLADORA: lanza la credencial como boomerang
        'especial_1': dict(keys=[
            K(1, lean=-4, bh=(120, 0.6)),
            K(1, lean=-10, bh=(165, 0.85), rx=-3, head=-4),
            K(1, lean=-12, bh=(175, 0.9), rx=-4, head=-4),
            K(1, lean=6, bh=(60, 0.8), rx=2),
            K(1, lean=14, bh=(-2, 1.3), tw=1, rx=6, bf=(4, 0), head=4),
            K(1, lean=14, bh=(0, 1.3), tw=1, rx=6, bf=(4, 0), head=4),
            K(1, lean=8, bh=(-20, 0.7), rx=4),
            K(1, lean=2, rx=1),
        ], dur=4),
        # GANCHO PRECEPTOR: uppercut ascendente
        'especial_2': dict(keys=[
            K(1, ry=12, lean=10, bh=(100, 0.6), bf=(-4, 0), ff=(4, 0)),
            K(1, ry=18, lean=14, bh=(110, 0.7), bf=(-5, 0), ff=(5, 0), sy=0.95),
            K(1, ry=0, lean=2, bh=(-25, 1.2), tw=1, rx=8, head=-6, sy=1.04),
            K(1, ry=-6, lrel=1, lean=-6, bh=(-55, 1.25), tw=1, rx=10, head=-14, bf=(4, -12), ff=(2, -6), sy=1.06),
            K(1, ry=-8, lrel=1, lean=-10, bh=(-70, 1.2), tw=1, rx=10, head=-16, bf=(6, -16), ff=(2, -8)),
            K(1, ry=-6, lrel=1, lean=-10, bh=(-80, 1.0), rx=5, head=-10, bf=(4, -10), ff=(0, -4)),
            K(1, ry=-2, lrel=1, lean=-4, bh=(-40, 0.6), rx=2),
            K(1, ry=8, lean=6),
            K(1),
        ], dur=4),
        # COMBO DISCIPLINARIO: combo de 6 golpes
        'ultimate_1': dict(keys=[
            K(1, ry=4, lean=-6, head=-6, bh=(-30, 0.4), fh=(-70, 0.4)),
            K(1, ry=8, lean=-8, head=-8, sy=0.96),
            K(1, fh=(-4, 1.0), lean=9, rx=4),
            K(1, fh=(-30, 0.5), lean=6, rx=4),
            K(1, bh=(-4, 1.3), tw=1, lean=16, rx=9, bf=(6, 0)),
            K(1, bh=(-30, 0.6), lean=10, rx=7),
            K(1, fh=(-40, 0.9), lean=12, rx=8, rot=4, head=6),
            K(1, fh=(10, 0.9), lean=18, rx=9, head=8),
            K(1, ry=20, bf=(-6, 0), ff_abs=(50, -3), ffa=-10, lean=10, rx=4),
            K(1, ry=16, bf=(-5, 0), ff=(5, 0), lean=8, rx=4),
            K(1, lean=-20, ff_abs=(42, -72), ffa=-60, rx=2, fh=(-80, 0.5), bh=(-60, 0.45)),
            K(1, lean=-22, ff_abs=(44, -76), ffa=-65, rx=2, fh=(-80, 0.5), bh=(-60, 0.45)),
            K(1, ry=14, lean=12, bh=(100, 0.6), bf=(-4, 0), ff=(4, 0), rx=4),
            K(1, ry=-6, lrel=1, lean=-4, bh=(-45, 1.25), tw=1, rx=12, head=-14, bf=(4, -12), ff=(2, -6), sy=1.06),
            K(1, ry=-8, lrel=1, lean=-10, bh=(-65, 1.2), tw=1, rx=12, head=-16, bf=(6, -16), ff=(2, -8)),
            K(1, ry=-2, lrel=1, lean=-4, bh=(-50, 0.7), rx=4),
            K(1, ry=6, lean=4),
            K(1),
        ], dur=4),
        # AMONESTACIÓN FINAL: carga de poder + puñetazo devastador
        'ultimate_2': dict(keys=[
            K(1, ry=6, lean=4, fh=(80, 0.7), bh=(85, 0.7)),
            K(1, ry=12, lean=8, fh=(95, 0.8), bh=(100, 0.8), head=8, bf=(-5, 0), ff=(5, 0)),
            K(1, ry=14, lean=-6, fh=(110, 0.75), bh=(120, 0.8), head=-16, bf=(-6, 0), ff=(6, 0), sy=1.02),
            K(1, ry=14, lean=-8, fh=(112, 0.75), bh=(122, 0.8), head=-18, bf=(-6, 0), ff=(6, 0), sy=1.03),
            K(1, ry=14, lean=-6, fh=(110, 0.75), bh=(120, 0.8), head=-16, bf=(-6, 0), ff=(6, 0), sy=1.02),
            K(1, ry=14, lean=-8, fh=(112, 0.75), bh=(122, 0.8), head=-18, bf=(-6, 0), ff=(6, 0), sy=1.03),
            K(1, ry=8, lean=-10, bh=(175, 0.6), fh=(-60, 0.6), rx=-3),
            K(1, ry=6, lean=-12, bh=(178, 0.5), fh=(-70, 0.6), rx=-4),
            K(1, ry=4, lean=24, bh=(-6, 1.3), tw=1, fh=(-80, 0.4), rx=14, bf=(-12, 0), ff=(8, 0), head=8, sx=1.08),
            K(1, ry=4, lean=26, bh=(-4, 1.3), tw=1, fh=(-80, 0.4), rx=15, bf=(-12, 0), ff=(8, 0), head=8, sx=1.1),
            K(1, ry=4, lean=26, bh=(-4, 1.3), tw=1, fh=(-80, 0.4), rx=15, bf=(-12, 0), ff=(8, 0), head=8),
            K(1, ry=4, lean=26, bh=(-4, 1.3), tw=1, fh=(-80, 0.4), rx=15, bf=(-12, 0), ff=(8, 0), head=8),
            K(1, ry=4, lean=16, bh=(-20, 0.8), rx=10, bf=(-8, 0), ff=(6, 0)),
            K(1, ry=2, lean=4, bh=(-95, 1.0), head=-10, rx=4),
            K(1, ry=2, lean=-2, bh=(-96, 1.0), head=-12, rx=3),
            K(1),
        ], dur=5),
    },
}


# ------------------------------------------------ terceras ultimates
SPECIALS['pantoja']['ultimate_3'] = dict(keys=[      # COLECTIVAZO
    K(1, ry=6, lean=6, head=6),
    K(1, ry=10, lean=14, bf=(-6, 0), sy=0.96),
] + [K(1, ry=4 + (i % 2) * 2, lean=-20, rx=12, bh=(160, 0.6), fh=(170, 0.6), bf=(8 + (i % 2) * 4, 0),
       ff=(6, -3 if i % 2 else 0), sx=1.08) for i in range(8)] + [
    K(1, ry=2, lean=-28, rx=14, bh=(170, 0.7), fh=(175, 0.7), bf=(12, 0), sx=1.12),
    K(1, ry=2, lean=-28, rx=14, bh=(170, 0.7), fh=(175, 0.7), bf=(12, 0), sx=1.12),
    K(1, ry=2, lean=-10, rx=6),
    K(1),
], dur=4)
SPECIALS['parada']['ultimate_3'] = dict(keys=[       # CIEN PATADAS
    K(1, ry=6, lean=-6),
    K(1, ff=(4, -10), lean=-8),
] + [(K(1, ff_abs=(46, -30 - 12 * (i % 3)), ffa=-30, lean=-14, rx=2) if i % 2 == 0 else
      K(1, ff_abs=(22, -34), ffa=-10, lean=-10, rx=2)) for i in range(12)] + [
    K(1, lean=-24, ff_abs=(40, -74), ffa=-62, head=10, rx=2),
    K(1, lean=-25, ff_abs=(42, -76), ffa=-64, head=10, rx=2),
    K(1, lean=-8, ff=(2, -4)),
    K(1),
], dur=3)
_st = []
for _k in range(3):
    _st += [K(1, ry=-5, ff=(0, -10), fh=(-95, 1.0), head=-10),
            K(1, ry=16, lean=10, bf=(-6, 0), ff=(6, 0), sx=1.05, sy=0.94, fh=(-60, 0.6)),
            K(1, ry=12, lean=6, bf=(-6, 0), ff=(6, 0), fh=(-70, 0.7))]
SPECIALS['nehuen']['ultimate_3'] = dict(keys=[       # LA BOMBONERA LATE
    K(1, ry=4, lean=-6, fh=(-93, 1.0), head=-12),
    K(1, ry=2, lean=-8, fh=(-97, 1.0), head=-14),
] + _st + [
    K(1, lean=-8, fh=(-95, 1.0), head=-12),
    K(1),
], dur=5)
SPECIALS['luciano']['ultimate_3'] = dict(keys=[      # ALTO VOLTAJE
    K(1, ry=4, lean=-4, fh=(-60, 0.6)),
    K(1, ry=6, lean=-8, fh=(-95, 1.05), head=-14),
] + [K(1, ry=6, lean=-8 - (i % 2), fh=(-93 - 4 * (i % 2), 1.05), head=-14 - 2 * (i % 2)) for i in range(6)] + [
    K(1, lean=10, fh=(-10, 1.1), rx=4, head=4),
    K(1, lean=11, fh=(-8, 1.12), rx=4, head=4),
    K(1, lean=10, fh=(-10, 1.1), rx=4, head=4),
    K(1, lean=2),
    K(1),
], dur=5)

# ------------------------------------------------ NICO
SPECIALS['nico'] = {
    'especial_1': dict(keys=[                         # HOJA DE ARCE
        K(1, lean=-6, fh=(-120, 0.6), rx=-2),
        K(1, lean=-10, fh=(-150, 0.8), rx=-3),
        K(1, lean=8, fh=(-30, 1.0), rx=4),
        K(1, lean=12, fh=(0, 1.15), rx=6, head=4),
        K(1, lean=12, fh=(2, 1.15), rx=6, head=4),
        K(1, lean=6, fh=(-30, 0.7)),
        K(1),
    ], dur=4),
    'especial_2': dict(keys=[                         # REINICIO FORZADO (rodillazo volador)
        K(1, ry=12, lean=10, bf=(-4, 0), ff=(4, 0)),
        K(1, ry=2, lrel=1, lean=6, ff=(14, -26), ffa=30, rx=4),
        K(1, ry=-4, lrel=1, lean=2, ff=(16, -34), ffa=40, bf=(-6, -4), rx=6),
        K(1, ry=-4, lrel=1, lean=2, ff=(16, -35), ffa=40, bf=(-6, -4), rx=6),
        K(1, ry=-4, lrel=1, lean=2, ff=(16, -34), ffa=40, bf=(-6, -4), rx=6),
        K(1, ry=-2, lrel=1, ff=(4, -10)),
        K(1, ry=8, lean=6),
        K(1),
    ], dur=4),
    'ultimate_1': dict(keys=[                         # PANTALLAZO AZUL
        K(1, ry=6, lean=6, fh=(-70, 0.45), head=8),
        K(1, ry=10, lean=10, fh=(-75, 0.4), head=12, sy=0.97),
        K(1, ry=11, lean=11, fh=(-78, 0.4), head=13, sy=0.96),
        K(1, ry=10, lean=10, fh=(-75, 0.4), head=12, sy=0.97),
        K(1, ry=0, lean=-10, fh=(-100, 1.05), head=-14, sy=1.04),
        K(1, ry=0, lean=-11, fh=(-97, 1.05), head=-15, sy=1.04),
        K(1, ry=0, lean=-10, fh=(-100, 1.05), head=-14, sy=1.03),
        K(1, ry=0, lean=-11, fh=(-97, 1.05), head=-15),
        K(1, lean=-4, fh=(-60, 0.6)),
        K(1),
    ], dur=5),
    'ultimate_2': dict(keys=[                         # DESPIDO INMEDIATO
        K(1, ry=6, lean=8),
        K(1, ry=8, lean=18, rx=8, bf=(-10, 0), sx=1.06),
        K(1, fh=(-4, 1.15), lean=10, rx=5),
        K(1, fh=(-40, 0.5), lean=6, rx=5),
        K(1, lean=4, ff=(12, -28), ffa=30, rx=4),
        K(1, lean=2, ff=(2, -6), rx=3),
        K(1, fh=(20, 1.1), lean=16, rx=7),
        K(1, fh=(-40, 0.5), lean=8, rx=4),
        K(1, lean=-6, ff=(2, -8), rx=-2),
        K(1, lean=-22, ff_abs=(46, -62), ffa=-50, head=8, rx=2),
        K(1, lean=-23, ff_abs=(47, -63), ffa=-50, head=8, rx=2),
        K(1, lean=-8, ff_abs=(24, -20)),
        K(1, lean=-4, fh=(-95, 1.0), head=-10),
        K(1),
    ], dur=5),
}

# ------------------------------------------------------------ animaciones sobre poses de referencia
# (tools/ref_poses.py: imágenes provistas por el autor, usadas como modelo para todos)
G = {'ref': 'guardia'}
GA = {'ref': 'guardia-alta'}
PM = {'ref': 'patada-media'}
PA = {'ref': 'patada-alta'}
BAR = {'ref': 'barrida'}
RG = {'ref': 'recibiendo-golpe'}
CEL = {'ref': 'celebrando'}
TR = {'ref': 'triste'}
PROV = {'ref': 'provocando'}
GL = {'ref': 'guardia', 'lrel': 1}
SL = {'ref': 'salto', 'lrel': 1}
C0 = dict(ry=26, bf=(-7, 0), ff=(7, 0), lean=8)       # agachado base


def BL(a, b, t, **kw):
    return K(1, blend=(a, b, t), **kw)


def idle_ref(t):
    s = math.sin(t * 2 * math.pi)
    return dict(ref='guardia', ry=1.2 + 1.2 * s, lean=0.8 * s, head=-0.8 * s,
                fh_off=(0.0, 0.025 * s), bh_off=(0.0, 0.03 * s))


def walk_ref(direction):
    base = walk(direction)

    def f(t):
        d = base(t)
        d['ref'] = 'guardia'
        d['lean'] = d.get('lean', 0) - 2 * direction       # la guardia ya trae su inclinación
        return d
    return f


ANIMS['idle'] = dict(func=(8, idle_ref), dur=7, loop=True)
ANIMS['caminar'] = dict(func=(8, walk_ref(1)), dur=5, loop=True)
ANIMS['caminar_atras'] = dict(func=(8, walk_ref(-1)), dur=6, loop=True)
ANIMS['bloquear'] = dict(keys=[BL(G, GA, 0.45), BL(G, GA, 0.85), K(1, ref='guardia-alta', ry=2, rx=-1)], dur=3)
ANIMS['patada'] = dict(keys=[BL(G, PM, t) for t in (0.25, 0.7, 1.0, 1.0, 0.6, 0.2)], dur=3)
ANIMS['patada_fuerte'] = dict(keys=[BL(G, PA, t) for t in (0.15, 0.45, 0.85, 1.0, 1.0, 0.7, 0.4, 0.15)], dur=4)
ANIMS['patada_agachado'] = dict(keys=[K(1, **C0), BL(C0, BAR, 0.6), K(1, **BAR), K(1, **BAR),
                                      BL(C0, BAR, 0.5), K(1, **C0)], dur=4)
ANIMS['recibir_golpe'] = dict(keys=[BL(G, RG, 0.75), K(1, **RG), BL(G, RG, 0.6), BL(G, RG, 0.25)], dur=4)
ANIMS['saltar'] = dict(keys=[
    K(1, ry=8, lean=6, sy=0.97),
    BL(GL, SL, 0.6, ry=-2), BL(GL, SL, 1.0, ry=-6), BL(GL, SL, 1.0, ry=-8), BL(GL, SL, 0.85, ry=-4),
    BL(GL, SL, 0.5),
    K(1, ry=8, lean=4, sy=0.97),
], dur=6)
ANIMS['patada_aerea']['keys'][0] = K(1, ref='salto', lrel=1, ry=-8)
ANIMS['victoria'] = dict(keys=[BL(G, CEL, 0.3), BL(G, CEL, 0.7)] +
                     [K(1, ref='celebrando', ry=(-2 if i % 2 else 0), head=(-3 if i % 2 else 0)) for i in range(8)],
                     dur=7)
ANIMS['derrota'] = dict(keys=[BL(G, TR, t) for t in (0.2, 0.45, 0.7, 0.9)] +
                    [K(1, ref='triste', ry=(1 if i % 2 else 0)) for i in range(4)], dur=8)
ANIMS['presentacion'] = dict(keys=[K(1, **G), BL(G, PROV, 0.5)] +
                         [K(1, ref='provocando', fh_off=(0, (-0.04 if i % 2 else 0.0)), head=(-2 if i % 2 else 0))
                          for i in range(7)] + [BL(G, PROV, 0.5), BL(G, PROV, 0.2), K(1, **G)], dur=6)


# ------------------------------------------------------------ encuentros antes de pelear
def _sway(n, fn):
    return [(fn(i / n), 1) for i in range(n)]


ANIMS['enamorado'] = dict(keys=[                     # manos juntas en el pecho, cabeza ladeada, suspiro
    K(1, fh=(-70, 0.32), lean=-2, head=10),
    K(1, fh=(-72, 0.30), lean=-4, head=14, ry=1),
    K(1, fh=(-74, 0.30), lean=-5, head=16, ry=2, sy=1.01),
    K(1, fh=(-72, 0.30), lean=-4, head=14, ry=1),
], dur=10, loop=True)
ANIMS['abrazo'] = dict(keys=[                        # brazos hacia adelante rodeando al otro
    K(1, fh=(-30, 0.7), lean=6, head=4),
    K(1, fh=(-18, 0.82), lean=12, head=8, rx=3),
    K(1, fh=(-14, 0.86), lean=14, head=10, rx=4),
    K(1, fh=(-16, 0.84), lean=13, head=9, rx=4, ry=1),
], dur=8, loop=False)
ANIMS['saludo'] = dict(keys=[                        # mano tendida + saludo con la mano
    K(1, fh=(-20, 0.75), lean=4, head=-4),
    K(1, fh=(-6, 0.95), lean=6, head=-6, rx=2),
    K(1, fh=(-8, 0.95), lean=6, head=-6, rx=2, ry=1),
    K(1, fh=(-90, 1.0), lean=-2, head=-8),
    K(1, fh=(-84, 1.0), lean=-2, head=-8),
    K(1, fh=(-92, 1.0), lean=-2, head=-8),
    K(1, fh=(-84, 1.0), lean=-2, head=-8),
], dur=7, loop=False)
ANIMS['provocar'] = dict(keys=[K(1, ref='provocando', fh_off=(0, (-0.04 if i % 2 else 0.0)), rx=2 + i % 2)
                               for i in range(4)], dur=6, loop=True)
ANIMS['enojado'] = dict(keys=[                       # puños abajo, temblando de bronca
    K(1, fh=(70, 0.55), lean=6, head=8, ry=3, sx=1.02),
    K(1, fh=(72, 0.56), lean=7, head=9, ry=3, rx=1, sx=1.02),
    K(1, fh=(70, 0.55), lean=6, head=8, ry=3, rx=-1, sx=1.02),
    K(1, fh=(72, 0.56), lean=7, head=9, ry=4, sx=1.03),
], dur=3, loop=True)
ANIMS['confundido'] = dict(keys=[                    # "¿y ahora qué hice?": hombros arriba, brazos abiertos
    K(1, fh=(20, 0.7), lean=-4, head=-8, ry=-1),
    K(1, fh=(-10, 0.85), lean=-6, head=-14, ry=-2),
    K(1, fh=(-12, 0.86), lean=-6, head=-16, ry=-2),
    K(1, fh=(-10, 0.85), lean=-5, head=-12, ry=-1),
], dur=9, loop=False)


ANIM_ORDER = ['idle', 'caminar', 'caminar_atras', 'saltar', 'saltar_adelante', 'agacharse',
              'bloquear', 'bloquear_agachado', 'presentacion', 'golpe', 'patada', 'golpe_fuerte', 'patada_fuerte', 'golpe_agachado',
              'patada_agachado', 'patada_aerea', 'recibir_golpe', 'caida', 'levantarse',
              'victoria', 'derrota', 'especial_1', 'especial_2', 'ultimate_1', 'ultimate_2', 'ultimate_3',
              'enamorado', 'abrazo', 'saludo', 'provocar', 'enojado', 'confundido']


# Ajustes de postura agachada por personaje: Parada tiene la pierna trasera muy
# estirada en el dibujo original y al agacharse hondo el pie se salía del cuadro.
CROUCH_ANIMS = ('agacharse', 'bloquear_agachado', 'golpe_agachado', 'patada_agachado')
CROUCH_FIX = {'parada': dict(max_ry=20, bf=(-12, 0), ff=(10, 0), lean_add=3)}


CROUCH_RY = 26          # altura única del agachado: todas las acciones agachadas a la misma altura
CROUCH_FEET = ((-7, 0), (7, 0))


def _fix_crouch(char, name, a):
    """Misma altura de agachado en todas las acciones agachadas (también dentro de blend)."""
    if name not in CROUCH_ANIMS or 'keys' not in a:
        return a
    fx = CROUCH_FIX.get(char)

    def fix(kf):
        kf = dict(kf)
        if 'blend' in kf:
            A, B, t = kf['blend']
            kf['blend'] = (fix(A), fix(B), t)
            return kf
        if 'ref' in kf or kf.get('ry', 0) < 16:
            return kf
        if fx:                                   # Parada: agachado sobre una rodilla
            kf['ry'] = min(kf['ry'], fx['max_ry'])
            kf['bf'] = fx['bf']
            if 'ff_abs' not in kf:
                kf['ff'] = fx['ff']
            kf['lean'] = kf.get('lean', 0) + fx['lean_add']
        else:
            kf['ry'] = max(kf['ry'], CROUCH_RY)
            if kf.get('bf') in (None, (-5, 0), (-4, 0), (-6, 0)):
                kf['bf'] = CROUCH_FEET[0]
            if 'ff_abs' not in kf and kf.get('ff') in (None, (5, 0), (4, 0)):
                kf['ff'] = CROUCH_FEET[1]
        return kf
    return dict(a, keys=[(fix(kf), n) for kf, n in a['keys']])


def get_anim(char, name):
    if name in SPECIALS.get(char, {}):
        return SPECIALS[char][name]
    return _fix_crouch(char, name, ANIMS[name])


def has_anim(char, name):
    return name in SPECIALS.get(char, {}) or name in ANIMS


# ================================================================== PERSONAJES NUEVOS
def _throw_up():                      # lanzar algo hacia arriba/adelante con las dos manos (paloma)
    return dict(keys=[
        K(1, ry=6, lean=6, fh=(60, 0.5), head=8),
        K(1, ry=8, lean=10, fh=(80, 0.45), bh_off=(0.1, 0.1), head=10),
        K(1, ry=2, lean=-4, fh=(-40, 0.9), head=-8),
        K(1, ry=0, lean=-8, fh=(-60, 1.05), head=-12),
        K(1, ry=0, lean=-8, fh=(-62, 1.05), head=-12),
        K(1, ry=2, lean=-2, fh=(-40, 0.7)),
        K(1),
    ], dur=4)


def _beam():                          # carga y rayo sostenido con el brazo adelante (prompt)
    return dict(keys=[
        K(1, ry=4, lean=-4, fh=(-60, 0.6), head=-6),
        K(1, ry=8, lean=-10, fh=(-100, 1.0), head=-14, sy=0.98),
        K(1, ry=8, lean=-11, fh=(-104, 1.0), head=-15),
        K(1, ry=6, lean=6, fh=(-30, 0.8), rx=2),
    ] + [K(1, ry=6, lean=10 + (i % 2), fh=(-6 + (i % 2) * 2, 1.06), rx=4, head=4, bf=(-6, 0)) for i in range(9)] + [
        K(1, ry=4, lean=4, fh=(-40, 0.7), rx=2),
        K(1),
    ], dur=5)


def _meditate(n_hold=4, burst=True):  # meditación: manos juntas, se eleva la energía
    keys = [
        K(1, ry=8, lean=2, fh=(-80, 0.42), head=10),
        K(1, ry=14, lean=0, fh=(-88, 0.38), head=14, bf=(-5, 0), ff=(5, 0)),
    ] + [K(1, ry=14 + (i % 2), lean=0, fh=(-88, 0.38), head=14, bf=(-5, 0), ff=(5, 0)) for i in range(n_hold)]
    if burst:
        keys += [
            K(1, ry=-2, lean=-8, fh=(-60, 1.05), bh=(-120, 0.8), head=-14, sy=1.04),
            K(1, ry=-2, lean=-9, fh=(-62, 1.05), bh=(-122, 0.8), head=-15, sy=1.04),
            K(1, ry=2, lean=-2, fh=(-40, 0.6)),
            K(1),
        ]
    return dict(keys=keys, dur=5)


def _surrender_punch():               # "bandera blanca": se rinde... y pega con todo
    return dict(keys=[
        K(1, ry=2, lean=-4, fh=(-92, 1.0), head=6),
        K(1, ry=2, lean=-6, fh=(-95, 1.02), head=10, sx=0.99),
        K(1, ry=4, lean=-4, fh=(-90, 1.0), head=8),
        K(1, ry=2, lean=-6, fh=(-95, 1.02), head=12),
        K(1, ry=4, lean=-4, fh=(-90, 1.0), head=8),
        K(1, ry=6, lean=4, fh=(-60, 0.6), head=-6),
        K(1, ry=8, lean=-10, fh=(-80, 0.32), rx=-3, bf=(-4, 0)),
        K(1, ry=6, lean=-12, fh=(-82, 0.3), rx=-4, bf=(-4, 0)),
        K(1, ry=4, lean=24, fh=(-4, 1.08), rx=14, bf=(-12, 0), ff=(8, 0), head=8, sx=1.06),
        K(1, ry=4, lean=26, fh=(-2, 1.08), rx=15, bf=(-12, 0), ff=(8, 0), head=8, sx=1.08),
        K(1, ry=4, lean=26, fh=(-2, 1.08), rx=15, bf=(-12, 0), ff=(8, 0), head=8),
        K(1, ry=4, lean=26, fh=(-2, 1.08), rx=15, bf=(-12, 0), ff=(8, 0), head=8),
        K(1, ry=4, lean=16, fh=(-20, 0.8), rx=10, bf=(-8, 0), ff=(6, 0)),
        K(1, ry=2, lean=4, fh=(-60, 0.6), rx=4),
        K(1, ry=2, lean=-2, fh=(-90, 1.0), head=-10, rx=3),
        K(1),
    ], dur=5)


def _ball_kick():                     # patear una pelota (proyectil desde el pie)
    return dict(keys=[
        K(1, ry=4, lean=4, ff=(-6, -4), fh=(-60, 0.55)),
        K(1, ry=6, lean=8, ff=(-12, -10), ffa=20, fh=(-40, 0.6)),
        K(1, ry=2, lean=-6, ff_abs=(30, -18), ffa=-20, fh=(-70, 0.5)),
        K(1, ry=2, lean=-12, ff_abs=(44, -30), ffa=-40, fh=(-80, 0.5), rx=2),
        K(1, ry=2, lean=-12, ff_abs=(46, -32), ffa=-42, fh=(-80, 0.5), rx=2),
        K(1, ry=2, lean=-6, ff_abs=(28, -14), fh=(-60, 0.55)),
        K(1, ry=2, lean=-2, ff=(2, -2)),
        K(1),
    ], dur=4)


def _mega_kick():                     # golazo: carga larga, carrera y patada enorme
    return dict(keys=[
        K(1, ry=6, lean=6, head=-6, fh=(-60, 0.55)),
        K(1, ry=12, lean=10, head=8, bf=(-6, 0), ff=(6, 0), fh=(-40, 0.5)),
        K(1, ry=12, lean=10, head=8, bf=(-6, 0), ff=(6, 0), fh=(-42, 0.5)),
        K(1, ry=4, lean=14, rx=6, ff=(10, -6), bf=(-8, 0), fh=(-30, 0.6)),
        K(1, ry=4, lean=16, rx=10, ff=(-10, -6), bf=(6, 0), fh=(-20, 0.6)),
        K(1, ry=6, lean=10, rx=10, ff=(-16, -14), ffa=25, fh=(-40, 0.6)),
        K(1, ry=2, lean=-14, rx=12, ff_abs=(46, -36), ffa=-45, fh=(-85, 0.55), head=6),
        K(1, ry=2, lean=-18, rx=12, ff_abs=(50, -44), ffa=-55, fh=(-88, 0.55), head=8),
        K(1, ry=2, lean=-18, rx=12, ff_abs=(50, -44), ffa=-55, fh=(-88, 0.55), head=8),
        K(1, ry=2, lean=-10, rx=8, ff_abs=(30, -16)),
        K(1, ry=2, lean=-6, fh=(-95, 1.0), head=-10, rx=4),
        K(1, ry=2, lean=-7, fh=(-97, 1.0), head=-12, rx=4),
        K(1, ry=2, lean=-2, rx=2),
        K(1),
    ], dur=4)


for _c in ('angel', 'facu', 'pedro', 'emi', 'denis'):
    SPECIALS[_c] = {}
# ANGEL — programador
SPECIALS['angel']['especial_1'] = SPECIALS['nico']['especial_1']          # BUG EN PRODUCCIÓN
SPECIALS['angel']['especial_2'] = SPECIALS['luciano']['especial_2']       # DEPLOY FORZADO
SPECIALS['angel']['ultimate_1'] = SPECIALS['luciano']['ultimate_1']       # BUCLE INFINITO
SPECIALS['angel']['ultimate_2'] = SPECIALS['luciano']['ultimate_3']       # STACK OVERFLOW
# FACU — fanático de la IA con gato naranja
SPECIALS['facu']['especial_1'] = SPECIALS['nico']['especial_1']           # MICHI NARANJA
SPECIALS['facu']['especial_2'] = SPECIALS['parada']['especial_1']         # ZARPAZO GATUNO
SPECIALS['facu']['ultimate_1'] = _beam()                                  # PROMPT DEFINITIVO
SPECIALS['facu']['ultimate_2'] = SPECIALS['luciano']['ultimate_3']        # LLUVIA DE MICHIS
# PEDRO — el pacifista
SPECIALS['pedro']['especial_1'] = _throw_up()                             # PALOMA DE LA PAZ
SPECIALS['pedro']['especial_2'] = _meditate(2)                            # ONDA ZEN
SPECIALS['pedro']['ultimate_1'] = _meditate(6)                            # PAZ INTERIOR
SPECIALS['pedro']['ultimate_2'] = _surrender_punch()                      # BANDERA BLANCA
# EMI — el estudiante
SPECIALS['emi']['especial_1'] = SPECIALS['nico']['especial_1']            # AVIÓN DE PAPEL
SPECIALS['emi']['especial_2'] = SPECIALS['luciano']['especial_2']         # MOCHILAZO
SPECIALS['emi']['ultimate_1'] = SPECIALS['luciano']['ultimate_1']         # PRUEBA SORPRESA
SPECIALS['emi']['ultimate_2'] = SPECIALS['luciano']['ultimate_3']         # TABLA DEL NUEVE
# DENIS — hincha de River
SPECIALS['denis']['especial_1'] = _ball_kick()                            # PELOTAZO
SPECIALS['denis']['especial_2'] = SPECIALS['parada']['especial_1']        # BANDA ROJA
SPECIALS['denis']['ultimate_1'] = SPECIALS['nehuen']['ultimate_3']        # EL MONUMENTAL RUGE
SPECIALS['denis']['ultimate_2'] = _mega_kick()                            # GOLAZO DE MEDIA CANCHA


# ------------------------------------------------ NEHUEN bostero: sin guitarra
SPECIALS['nehuen']['especial_1'] = SPECIALS['nico']['especial_1']        # BUFANDAZO (revolea y tira la bufanda)
SPECIALS['nehuen']['ultimate_1'] = _beam()                               # AZUL Y ORO (rayo)
