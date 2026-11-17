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
        K(1, ry=-2, sy=1.03, fh=(-80, 0.7), bh=(-70, 0.6)),
        K(1, lrel=1, ry=-6, bf=(4, -16), ff=(-2, -20), fh=(-70, 0.6)),
        K(2, lrel=1, ry=-8, bf=(6, -22), ff=(-4, -26), fh=(-60, 0.55), bh=(-40, 0.45)),
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
        K(1, ry=8, bf=(-2, 0), ff=(2, 0), lean=3),
        K(1, ry=17, bf=(-4, 0), ff=(4, 0), lean=6, fh_off=(0, 0.05)),
        K(1, ry=20, bf=(-5, 0), ff=(5, 0), lean=7, fh_off=(0, 0.06), bh_off=(0, 0.04)),
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
        K(1, ff_abs=(46, -40), ffa=-35, lean=-14, rx=-2, bh=(-20, 0.5)),
        K(1, ff_abs=(48, -40), ffa=-35, lean=-14, rx=-2, bh=(-20, 0.5)),
        K(1, ff_abs=(30, -26), ffa=-15, lean=-8),
        K(1, ff=(2, -4), lean=-2),
    ], dur=3),
    'golpe_fuerte': dict(keys=[
        K(1, lean=-6, bh=(170, 0.35), rx=-2, head=-2),
        K(1, lean=-8, bh=(175, 0.3), rx=-3, fh=(-60, 0.55)),
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
        K(1, ry=24, bf=(-6, 0), ff_abs=(30, -3), lean=7),
        K(1, ry=20, bf=(-5, 0), ff=(5, 0), lean=7),
    ], dur=4),
    'patada_aerea': dict(keys=[
        K(1, lrel=1, ry=-8, bf=(6, -22), ff=(-4, -26)),
        K(1, lrel=1, ry=-8, bf=(6, -24), ff=(14, -16), ffa=-20, lean=-8),
        K(1, lrel=1, ry=-8, bf=(4, -24), ff=(26, -6), ffa=-40, lean=-14, fh=(-100, 0.5)),
        K(1, lrel=1, ry=-8, bf=(4, -24), ff=(26, -6), ffa=-40, lean=-14, fh=(-100, 0.5)),
    ], dur=4, loop=False),
    'recibir_golpe': dict(keys=[
        K(1, lean=-12, head=-14, rx=-3, fh=(-100, 0.5), bh=(-90, 0.5)),
        K(1, lean=-18, head=-20, rx=-5, fh=(-80, 0.5), bh=(-110, 0.5), ry=2),
        K(1, lean=-10, head=-8, rx=-3, ry=1),
        K(1, lean=-3, head=-2),
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
            K(1, ry=-6, lrel=1, sy=1.1, fh=(-110, 1.0), bh=(-100, 1.0), bf=(0, -6), ff=(0, -8)),
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

ANIM_ORDER = ['idle', 'caminar', 'caminar_atras', 'saltar', 'saltar_adelante', 'agacharse',
              'bloquear', 'bloquear_agachado', 'presentacion', 'golpe', 'patada', 'golpe_fuerte', 'patada_fuerte', 'golpe_agachado',
              'patada_agachado', 'patada_aerea', 'recibir_golpe', 'caida', 'levantarse',
              'victoria', 'derrota', 'especial_1', 'especial_2', 'ultimate_1', 'ultimate_2', 'ultimate_3']


def get_anim(char, name):
    if name in SPECIALS.get(char, {}):
        return SPECIALS[char][name]
    return ANIMS[name]


def has_anim(char, name):
    return name in SPECIALS.get(char, {}) or name in ANIMS
