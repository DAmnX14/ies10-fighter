"""Sistema centralizado de render y geometría de los luchadores.

Todos los luchadores (los actuales y los que se agreguen) pasan por acá:

- ``FighterProfile``: ficha técnica configurable de cada personaje (escala, offsets,
  ancla, tamaño de referencia, cajas base y velocidad de animación). Los valores por
  defecto salen del ``<nombre>_meta.json`` que genera ``tools/build_sprites.py``; se
  pueden ajustar sin tocar código desde ``config.FIGHTER_PROFILES``.
- Ancla bottom-center: el punto ``anchor`` de cada cuadro es el suelo bajo la pelvis.
  Ese punto se dibuja exactamente en la posición (x, y) del luchador, así que los pies
  quedan sobre ``stage.ground_y`` en todas las animaciones.
- Corrección por cuadro (red de seguridad): si un cuadro apoyado en el piso tiene su
  punto más bajo unos píxeles arriba o abajo del suelo, se compensa al dibujarlo y al
  calcular las cajas. Con los sprites actuales vale 0 (los generadores ya los alinean),
  pero protege a cualquier personaje nuevo.
- Hurtbox por cuerpo real (cabeza, torso y piernas según las articulaciones del
  cuadro), no por el rectángulo del sprite que incluye brazos y piernas estiradas.
- Una sola transformación sprite -> mundo, usada para dibujar, para las hitboxes y
  para los efectos, así nunca se desalinean entre sí.
- Escalado sólo por enteros y vecino más cercano (pixel art nítido, sin deformar).
"""
import pygame
import config as C

FEET_JOINTS = ('f_an', 'b_an', 'f_toe', 'b_toe')
BODY_JOINTS = ('head', 'neck', 'pelvis', 'f_kn', 'b_kn', 'f_an', 'b_an', 'f_toe', 'b_toe')
GROUND_TOL = 16          # px nativos: un pie a esta altura o menos se considera apoyado
MAX_FIX = 6              # corrección automática máxima por cuadro (px nativos)


class FighterProfile:
    """Parámetros de render y colisión de un luchador."""

    def __init__(self, name, meta):
        o = getattr(C, 'FIGHTER_PROFILES', {}).get(name, {})
        self.name = name
        self.scale = int(o.get('scale', C.SCALE))                # siempre entero
        self.offset_x = o.get('offset_x', 0)                     # px nativos
        self.offset_y = o.get('offset_y', 0)
        self.anchor = tuple(o.get('anchor', meta['anchor']))
        self.anim_speed = o.get('anim_speed', 1.0)               # >1 = más rápido
        idle = meta['animations']['idle']['bbox'][0]
        self.ref_w = idle[2] - idle[0]                           # ancho/alto de referencia (reposo)
        self.ref_h = idle[3] - idle[1]
        self.height = meta.get('height', self.ref_h)
        # medio ancho de empuje (px de pantalla): los cuerpos no se superponen
        self.push_w = int(o.get('push_w', max(64, self.ref_w * 0.40 * self.scale)))
        # margen lateral de la hurtbox alrededor de las articulaciones del cuerpo
        self.hurt_margin = o.get('hurt_margin', max(8, round(self.height * 0.075)))
        self.head_top = o.get('head_top', round(self.height * 0.10))

    def describe(self):
        return dict(name=self.name, scale=self.scale, offset=(self.offset_x, self.offset_y), anchor=self.anchor,
                    ref=(self.ref_w, self.ref_h), push_w=self.push_w, anim_speed=self.anim_speed)


class FrameGeometry:
    """Datos precalculados de un cuadro (en px nativos del cuadro de 240x176)."""
    __slots__ = ('rect', 'feet_y', 'fix_y', 'hurt', 'grounded')

    def __init__(self, rect, feet_y, fix_y, hurt, grounded):
        self.rect, self.feet_y, self.fix_y, self.hurt, self.grounded = rect, feet_y, fix_y, hurt, grounded


def compute_geometry(profile, info):
    """Calcula rect, pies, corrección vertical y hurtbox de cada cuadro de una animación."""
    ax, ay = profile.anchor
    out = []
    for i in range(info['frames']):
        x0, y0, x1, y1 = info['bbox'][i]
        j = info['joints'][i]
        feet = max(j[k][1] for k in FEET_JOINTS)
        grounded = feet >= ay - GROUND_TOL
        fix = 0
        if grounded and y1 - 1 != ay and abs(ay - (y1 - 1)) <= MAX_FIX:
            fix = ay - (y1 - 1)                                  # baja/sube el cuadro hasta el suelo
        # hurtbox del cuerpo: articulaciones del torso y las piernas + margen
        xs = [j[k][0] for k in BODY_JOINTS]
        ys = [j[k][1] for k in BODY_JOINTS]
        m = profile.hurt_margin
        hx0, hx1 = min(xs) - m, max(xs) + m
        hy0 = min(ys) - profile.head_top
        hy1 = max(j[k][1] for k in FEET_JOINTS) + 4
        # ancho mínimo (perfil de costado) y siempre dentro del sprite real
        minw = profile.height * 0.30
        if hx1 - hx0 < minw:
            c = (hx0 + hx1) / 2
            hx0, hx1 = c - minw / 2, c + minw / 2
        hx0, hx1 = max(hx0, x0), min(hx1, x1)
        hy0, hy1 = max(hy0, y0), min(hy1, y1)
        out.append(FrameGeometry((x0, y0, x1, y1), y1 - 1, fix, (hx0, hy0, hx1, hy1), grounded))
    return out


class FighterRenderer:
    """Dibujo y transformaciones comunes a todos los luchadores."""

    def __init__(self, sprites):
        self.spr = sprites
        self.p = sprites.profile

    # ------------------------------------------------------------ transformaciones
    def geom(self, anim, frame):
        return self.spr.geometry(anim, frame)

    def to_world(self, x, y, facing, nx, ny, anim, frame, scale=None):
        """Punto nativo del cuadro -> coordenadas de mundo (o de pantalla si x,y lo son)."""
        p = self.p
        s = scale or p.scale
        g = self.geom(anim, frame)
        ax, ay = p.anchor
        return (x + (nx - ax + p.offset_x) * s * facing,
                y + (ny - ay + p.offset_y + g.fix_y) * s)

    def rect_world(self, x, y, facing, r, anim, frame):
        a = self.to_world(x, y, facing, r[0], r[1], anim, frame)
        b = self.to_world(x, y, facing, r[2], r[3], anim, frame)
        return pygame.Rect(int(min(a[0], b[0])), int(min(a[1], b[1])),
                           int(abs(b[0] - a[0])), int(abs(b[1] - a[1])))

    def hurtbox(self, x, y, facing, anim, frame):
        return self.rect_world(x, y, facing, self.geom(anim, frame).hurt, anim, frame)

    def sprite_rect(self, x, y, facing, anim, frame):
        return self.rect_world(x, y, facing, self.geom(anim, frame).rect, anim, frame)

    # ------------------------------------------------------------ dibujo
    def surface(self, anim, frame, facing, scale=None):
        """(surface escalada, dx, dy) relativos al ancla, ya con offsets y corrección."""
        p = self.p
        s = scale or p.scale
        img, dx, dy = self.spr.frame_surface(anim, frame, facing, s)
        g = self.geom(anim, frame)
        return img, dx + p.offset_x * s * facing, dy + (p.offset_y + g.fix_y) * s

    def draw(self, surf, sx, sy, anim, frame, facing=1, scale=None, flash=None, alpha=None, glow=None):
        """Dibuja el cuadro con el ancla (pies) en la posición de pantalla (sx, sy)."""
        img, dx, dy = self.surface(anim, frame, facing, scale)
        if flash is not None:
            img = img.copy()
            img.fill(flash + (0,), special_flags=pygame.BLEND_RGB_ADD)
        if alpha is not None:
            img = img.copy()
            img.set_alpha(alpha)
        if glow:
            g = img.copy()
            g.fill(glow + (0,), special_flags=pygame.BLEND_RGB_MULT)
            for ox, oy in ((-4, 0), (4, 0), (0, -4), (0, 4)):
                surf.blit(g, (round(sx + dx + ox), round(sy + dy + oy)))
        x, y = round(sx + dx), round(sy + dy)          # alineado a píxel entero
        surf.blit(img, (x, y))
        return img, x, y


def renderer(name):
    from game import assets
    return assets.character(name).renderer
