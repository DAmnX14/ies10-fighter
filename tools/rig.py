"""
Rig 2D por huesos construido a partir de los sprites originales.

Cada sprite fuente se segmenta (se elimina el fondo cuadriculado), se divide
en partes (cabeza, torso, brazo, antebrazo, muslo, pierna, pie) asignando cada
píxel al hueso más cercano, y luego cada parte se re-posa con rotaciones
(cinemática directa + inversa) para producir fotogramas reales de animación.

El render interno se hace a 4x la resolución nativa y luego se reduce y se
cuantiza a la paleta del personaje, para mantener la estética pixel-art.
"""
import math
import numpy as np
import cv2
from PIL import Image

# ---------------------------------------------------------------- constantes
CANVAS_W, CANVAS_H = 240, 176      # tamaño de cada fotograma (px nativos)
ANCHOR_X, ANCHOR_Y = 112, 170       # punto del suelo bajo la pelvis
SS = 4                             # supersampling interno

# Esqueletos en coordenadas de la imagen fuente.
#  b_ = brazo/pierna trasera   f_ = brazo/pierna delantera (lado del rival)
SKELETONS = {
    'luciano': dict(
        src='luciano.jpg', height=126,
        pelvis=(600, 1470), neck=(690, 815), head=(690, 400),
        b_sh=(370, 880), b_el=(185, 1170), b_ha=(545, 880),
        f_sh=(870, 900), f_el=(1065, 1205), f_ha=(1060, 815),
        b_hip=(500, 1500), b_kn=(340, 1960), b_an=(195, 2390), b_toe=(100, 2490),
        f_hip=(725, 1500), f_kn=(1000, 1900), f_an=(990, 2380), f_toe=(1290, 2475),
    ),
    'nehuen': dict(
        src='nehuen.jpg', height=128,
        pelvis=(560, 1470), neck=(640, 760), head=(640, 300),
        b_sh=(300, 800), b_el=(110, 1060), b_ha=(555, 830),
        f_sh=(820, 790), f_el=(935, 1140), f_ha=(1000, 790),
        b_hip=(470, 1500), b_kn=(330, 1950), b_an=(210, 2390), b_toe=(120, 2500),
        f_hip=(680, 1500), f_kn=(880, 1850), f_an=(880, 2380), f_toe=(1130, 2480),
    ),
    'pantoja': dict(
        src='pantoja.jpg', height=114,
        pelvis=(520, 1400), neck=(585, 950), head=(610, 640),
        b_sh=(360, 1040), b_el=(420, 1215), b_ha=(790, 985),
        f_sh=(600, 1030), f_el=(650, 1230), f_ha=(840, 1370),
        b_hip=(420, 1450), b_kn=(300, 1710), b_an=(195, 1985), b_toe=(100, 2065),
        f_hip=(630, 1450), f_kn=(830, 1650), f_an=(850, 1960), f_toe=(980, 2040),
        front_f=True,
        torso_poly=[(300, 930), (470, 915), (560, 960), (680, 990), (730, 1100), (745, 1250),
                    (720, 1340), (640, 1395), (420, 1405), (250, 1370), (225, 1250), (230, 1050)],
    ),
    'nico': dict(
        src='nico.png', height=126,
        pelvis=(235, 520), neck=(240, 300), head=(236, 215),
        b_sh=(140, 345), b_el=(115, 440), b_ha=(235, 385),
        f_sh=(320, 340), f_el=(340, 445), f_ha=(385, 345),
        b_hip=(195, 535), b_kn=(150, 680), b_an=(110, 815), b_toe=(80, 855),
        f_hip=(275, 535), f_kn=(315, 660), f_an=(325, 810), f_toe=(395, 850),
    ),
    'parada': dict(
        src='parada.jpg', height=126,
        pelvis=(620, 1480), neck=(700, 830), head=(720, 410),
        b_sh=(370, 860), b_el=(195, 1180), b_ha=(560, 905),
        f_sh=(900, 900), f_el=(1090, 1230), f_ha=(1110, 830),
        b_hip=(520, 1520), b_kn=(380, 1950), b_an=(230, 2390), b_toe=(130, 2500),
        f_hip=(760, 1520), f_kn=(1040, 1900), f_an=(1030, 2380), f_toe=(1300, 2480),
    ),
}

# hueso: (articulación proximal, distal, radio relativo a la altura)
BONES = {
    'torso':  ('pelvis', 'neck', 0.13),
    'head':   ('neck', 'head', 0.085),
    'b_up':   ('b_sh', 'b_el', 0.05),
    'b_lo':   ('b_el', 'b_ha', 0.06),
    'f_up':   ('f_sh', 'f_el', 0.05),
    'f_lo':   ('f_el', 'f_ha', 0.06),
    'b_th':   ('b_hip', 'b_kn', 0.055),
    'b_shin': ('b_kn', 'b_an', 0.045),
    'b_foot': ('b_an', 'b_toe', 0.04),
    'f_th':   ('f_hip', 'f_kn', 0.055),
    'f_shin': ('f_kn', 'f_an', 0.045),
    'f_foot': ('f_an', 'f_toe', 0.04),
}
DRAW_ORDER = ['f_up', 'f_lo', 'b_th', 'b_shin', 'b_foot', 'f_th', 'f_shin',
              'f_foot', 'torso', 'head', 'b_up', 'b_lo']


# --------------------------------------------------------------- segmentado
def segment(path, name):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.int16)
    mx, mn = a.max(2), a.min(2)
    cand = ((mx - mn) < 28) & (mn > 105)
    if name == 'pantoja':
        cand[2340:, :] = True            # franja negra inferior del original
    cand = cand.astype(np.uint8)
    n, lab = cv2.connectedComponents(cand, connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    border.discard(0)
    bg = np.isin(lab, list(border))
    fg = (~bg).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    fg = (lab == big)
    # quitar restos grises del fondo pegados al contorno
    halo = ((mx - mn) < 22) & (mn > 150) & fg
    kk = max(3, int(15 * a.shape[0] / 2500)) | 1
    er = cv2.erode(fg.astype(np.uint8), np.ones((kk, kk), np.uint8)).astype(bool)
    fg &= ~(halo & ~er)
    return a.astype(np.uint8), fg


def seg_dist(px, py, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((px - ax) * dx + (py - ay) * dy) / L2, 0, 1)
    qx, qy = ax + t * dx, ay + t * dy
    return np.hypot(px - qx, py - qy)


def ang(v):
    return math.degrees(math.atan2(v[1], v[0]))


def rot(v, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def length(v): return math.hypot(v[0], v[1])


def ik2(A, T, L1, L2, sign):
    d = sub(T, A); dist = length(d)
    dist = max(abs(L1 - L2) + 1e-3, min(L1 + L2 - 1e-3, dist))
    a = math.atan2(d[1], d[0])
    c = (L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist)
    al = math.acos(max(-1, min(1, c)))
    E = (A[0] + L1 * math.cos(a + sign * al), A[1] + L1 * math.sin(a + sign * al))
    Tn = (A[0] + dist * math.cos(a), A[1] + dist * math.sin(a))
    return E, Tn


# ---------------------------------------------------------------- personaje
class RigCharacter:
    def __init__(self, name, src_dir):
        self.name = name
        sk = SKELETONS[name]
        img, fg = segment(f'{src_dir}/{sk["src"]}', name)
        ys, xs = np.where(fg)
        H_src = ys.max() - ys.min()
        self.ground_src = ys.max()
        ns = sk['height'] / H_src                  # escala nativa
        self.ws = ws = ns * SS                     # escala de trabajo
        self.H = sk['height'] * SS                 # altura en px de trabajo
        self.u = self.H / 100.0

        # ---- asignación de píxeles a huesos (en resolución fuente reducida)
        small = cv2.resize(img, None, fx=ws, fy=ws, interpolation=cv2.INTER_AREA)
        fgs = cv2.resize(fg.astype(np.uint8) * 255, (small.shape[1], small.shape[0]),
                         interpolation=cv2.INTER_AREA) > 127
        self.J = {k: (v[0] * ws, v[1] * ws) for k, v in sk.items()
                  if isinstance(v, tuple)}
        self.ground_y = self.ground_src * ws
        h, w = fgs.shape
        py, px = np.mgrid[0:h, 0:w].astype(np.float32)
        names = list(BONES)
        D = np.stack([seg_dist(px, py, self.J[BONES[b][0]], self.J[BONES[b][1]])
                      / (BONES[b][2] * self.H) for b in names])
        limb = [i for i, b in enumerate(names) if b not in ('torso', 'head')]
        Dl = D[limb]
        li = np.argmin(Dl, 0)
        lmin = np.take_along_axis(Dl, li[None], 0)[0]
        th = np.where(D[0] < D[1], 0, 1)      # torso / cabeza
        tmin = np.minimum(D[0], D[1])
        if 'torso_poly' in sk:
            tp = np.zeros((h, w), np.uint8)
            cv2.fillPoly(tp, [np.array([(x * ws, y * ws) for x, y in sk['torso_poly']], np.int32)], 1)
            self.torso_poly = tp > 0
            tmin = np.where(self.torso_poly, 0.0, tmin)
            lmin = np.where(self.torso_poly, lmin * 1.2, lmin)
        else:
            self.torso_poly = None
        lab = np.where((lmin < 1.0) | (tmin > 1.0), np.array(limb)[li], th)
        lab = np.where(fgs, lab, -1)
        # limpiar fragmentos sueltos: se reasignan a la parte vecina dominante
        for _ in range(3):
            for i in range(len(names)):
                m = (lab == i).astype(np.uint8)
                n_, cc, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
                if n_ <= 2:
                    continue
                keep = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
                for c_ in range(1, n_):
                    if c_ == keep:
                        continue
                    comp = (cc == c_).astype(np.uint8)
                    ring = (cv2.dilate(comp, np.ones((3, 3), np.uint8)) > 0) & (comp == 0)
                    nb = lab[ring]; nb = nb[(nb >= 0) & (nb != i)]
                    if len(nb):
                        lab[comp > 0] = np.bincount(nb).argmax()
        # todo lo que está por encima de la línea de cadera pertenece al torso
        hip_y = min(self.J['b_hip'][1], self.J['f_hip'][1]) + 0.01 * self.H
        for ob in ('b_th', 'f_th'):
            k = names.index(ob)
            lab[(lab == k) & (py < hip_y)] = 0
        self.label = lab

        rgba = np.dstack([small, (fgs * 255).astype(np.uint8)])
        self.parts = {}
        for i, b in enumerate(names):
            m = (self.label == i)
            if b not in ('torso', 'head'):
                # solape en articulaciones: cada parte incluye un disco de su cadena
                # alrededor de sus articulaciones, para que no se abran huecos al rotar
                chain = [n_ for n_ in names if n_[0] == b[0] and
                         (n_.endswith(('_up', '_lo')) == b.endswith(('_up', '_lo'))) and n_ not in ('torso', 'head')]
                cm = np.isin(self.label, [names.index(c_) for c_ in chain])
                rad = BONES[b][2] * self.H * (1.3 if b[2:] in ('th', 'shin') else 1.05)
                for jn in BONES[b][:2]:
                    if jn.endswith('_toe') or jn.endswith('_ha'):
                        continue
                    jd = np.hypot(px - self.J[jn][0], py - self.J[jn][1])
                    m = m | (cm & (jd < rad))
            layer = np.zeros_like(rgba)
            layer[m] = rgba[m]
            if b == 'torso':
                # rellenar donde el brazo trasero tapaba el torso
                hole = np.zeros((h, w), np.uint8)
                tm = m.astype(np.uint8)
                if self.torso_poly is not None:
                    hullm = self.torso_poly.astype(np.uint8)
                else:
                    hull = cv2.convexHull(cv2.findNonZero(tm))
                    hullm = np.zeros((h, w), np.uint8); cv2.fillConvexPoly(hullm, hull, 1)
                for ob in (('b_up', 'b_lo', 'f_up', 'f_lo') if sk.get('front_f') else ('b_up', 'b_lo')):
                    hole |= ((self.label == names.index(ob)) & (hullm > 0)).astype(np.uint8)
                # piel de brazos/manos que quedó dentro del torso: se repinta con la ropa
                L_ = layer[..., :3].astype(np.int16)
                r_, g_, b_ = L_[..., 0], L_[..., 1], L_[..., 2]
                op = layer[..., 3] > 0
                skin = op & (r_ > 110) & (g_ > b_ + 10) & (r_ > g_ + 15) & (r_ - g_ < 110)
                if self.torso_poly is not None:
                    inner = cv2.erode(self.torso_poly.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
                    skin = op & ((g_ >= b_ - 2) & (r_ > 60) | inner & ~((b_ > g_ + 15) & (r_ > 120)))
                nd = np.hypot(px - self.J['neck'][0], py - self.J['neck'][1])
                skin &= nd > 0.10 * self.H
                if not sk.get('front_f'):
                    hd = np.hypot(px - self.J['b_ha'][0], py - self.J['b_ha'][1])
                    skin |= op & (hd < 0.075 * self.H)
                if skin.sum() > 20:
                    skin = (cv2.dilate(skin.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & op
                    layer[skin] = 0
                    hole |= skin.astype(np.uint8)
                if hole.any():
                    hole = cv2.dilate(hole, np.ones((3, 3), np.uint8))
                    known = layer[..., 3] > 0
                    src_rgb = small.copy()
                    src_rgb[~known] = 0
                    fill = cv2.inpaint(src_rgb, (~known).astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA)
                    sel = (hole > 0) & ~known
                    layer[sel, :3] = fill[sel]
                    layer[sel, 3] = 255
                # parche de cadera: duplica la parte alta de los muslos en el torso
                hipd = seg_dist(px, py, self.J['b_hip'], self.J['f_hip'])
                for ob in ('b_th', 'f_th'):
                    sel = (self.label == names.index(ob)) & (hipd < 0.10 * self.H)
                    layer[sel] = rgba[sel]
                # hombreras: la parte alta de cada brazo se duplica en el torso
                for sd in ('b' if sk.get('front_f') else 'bf'):
                    shd = np.hypot(px - self.J[sd + '_sh'][0], py - self.J[sd + '_sh'][1])
                    sel = (self.label == names.index(sd + '_up')) & (shd < 0.045 * self.H)
                    layer[sel] = rgba[sel]
            ys_, xs_ = np.where(layer[..., 3] > 0)
            if len(xs_) == 0:
                continue
            x0, y0, x1, y1 = xs_.min(), ys_.min(), xs_.max() + 1, ys_.max() + 1
            crop = layer[y0:y1, x0:x1].copy()
            # escalar a resolución de trabajo (SS) ya está aplicado
            self.parts[b] = (crop, (x0, y0))

        # ---- datos de reposo
        J = self.J
        self.L = {b: length(sub(J[BONES[b][1]], J[BONES[b][0]])) for b in names}
        self.rest_ang = {b: ang(sub(J[BONES[b][1]], J[BONES[b][0]])) for b in names}
        self.anchor = (J['pelvis'][0], self.ground_y)
        self.armlen = {s: self.L[s + '_up'] + self.L[s + '_lo'] for s in 'bf'}
        self.leglen = {s: self.L[s + '_th'] + self.L[s + '_shin'] for s in 'bf'}

        def bend(A, E, T):
            d1 = sub(E, A); d2 = sub(T, A)
            return 1 if d1[0] * d2[1] - d1[1] * d2[0] < 0 else -1
        self.arm_sign = {s: bend(J[s + '_sh'], J[s + '_el'], J[s + '_ha']) for s in 'bf'}
        self.leg_sign = {s: bend(J[s + '_hip'], J[s + '_kn'], J[s + '_an']) for s in 'bf'}
        # posición de reposo de la mano relativa al hombro en unidades de brazo
        self.rest_hand = {s: mul(sub(J[s + '_ha'], J[s + '_sh']), 1 / self.armlen[s])
                          for s in 'bf'}
        self.rest_ankle_u = {s: mul(sub(J[s + '_an'], self.anchor), 1 / self.u) for s in 'bf'}
        self.palette = None
        self.weak_back = not sk.get('front_f')
        self.order = list(DRAW_ORDER)
        if sk.get('front_f'):
            for b in ('f_up', 'f_lo'):
                self.order.remove(b)
            self.order += ['f_up', 'f_lo']

    # ------------------------------------------------------------ pose
    def default_params(self):
        p = dict(rx=0.0, ry=0.0, lean=0.0, head=0.0, rot=0.0, lrel=0.0, sx=1.0, sy=1.0)
        for s in 'bf':
            p[s + 'hx'], p[s + 'hy'] = self.rest_hand[s]
            p[s + 'fx'] = p[s + 'fy'] = 0.0
            p[s + 'fa'] = 0.0
        return p

    def resolve(self, kf):
        """Convierte un keyframe genérico a parámetros numéricos completos."""
        p = self.default_params()
        for k, v in kf.items():
            if k in ('bh', 'fh'):            # mano: (ang, ext) polar torso-local
                a, e = v
                p[k[0] + 'hx'] = math.cos(math.radians(a)) * e
                p[k[0] + 'hy'] = math.sin(math.radians(a)) * e
            elif k in ('bh_off', 'fh_off'):  # desplazamiento desde reposo
                p[k[0] + 'hx'] += v[0]; p[k[0] + 'hy'] += v[1]
            elif k in ('bf_abs', 'ff_abs'):  # tobillo absoluto (u) desde ancla
                s = k[0]
                p[s + 'fx'] = v[0] - self.rest_ankle_u[s][0]
                p[s + 'fy'] = v[1] - self.rest_ankle_u[s][1]
            elif k in ('bf', 'ff'):          # tobillo desplazado (u)
                p[k[0] + 'fx'], p[k[0] + 'fy'] = v
            else:
                p[k] = v
        if self.weak_back:
            # El brazo trasero está dibujado plegado sobre el pecho y se deforma al
            # extenderlo: los golpes/gestos amplios los hace el brazo delantero.
            br, fr = self.rest_hand['b'], self.rest_hand['f']
            dbx, dby = p['bhx'] - br[0], p['bhy'] - br[1]
            db = math.hypot(dbx, dby)
            df = math.hypot(p['fhx'] - fr[0], p['fhy'] - fr[1])
            if db > 0.45 and db >= df:
                p['fhx'], p['fhy'] = p['bhx'], p['bhy']
                p['_swap'] = True
                p['tw'] = 0.0
            if db > 0.26:
                p['bhx'], p['bhy'] = br[0] + dbx / db * 0.26, br[1] + dby / db * 0.26
        return p

    def solve(self, p):
        """Devuelve posiciones de articulaciones y ángulos de cada hueso."""
        J = self.J; u = self.u
        self._scale = {}
        R = p['rot']
        pel0 = J['pelvis']
        ry = p['ry']
        if p['lrel'] < 0.5 and ry > 0:
            # no doblar las piernas más de lo que el dibujo soporta
            for _ in range(40):
                pel_t = add(pel0, (p['rx'] * u, ry * u))
                ok = True
                for s in 'bf':
                    hip = add(pel_t, rot(sub(J[s + '_hip'], pel0), R))
                    tg = add(J[s + '_an'], (p[s + 'fx'] * u, p[s + 'fy'] * u))
                    if length(sub(tg, hip)) < 0.70 * self.leglen[s] and p[s + 'fy'] > -8:
                        ok = False
                if ok or ry <= 0:
                    break
                ry -= 0.75
        pel = add(pel0, (p['rx'] * u, ry * u))

        def body(pt, extra=0.0):   # transforma punto de reposo rígido con pelvis
            return add(pel, rot(sub(pt, pel0), R + extra))
        lean = p['lean']
        # torso + hombros rotan con lean+rot alrededor de la pelvis
        P = {'pelvis': pel}
        P['neck'] = body(J['neck'], lean)
        tw = p.get('tw', 0.0)
        P['b_sh'] = body((J['b_sh'][0] + (J['f_sh'][0] - J['b_sh'][0]) * tw * 0.6,
                          J['b_sh'][1] + (J['f_sh'][1] - J['b_sh'][1]) * tw * 0.3), lean)
        P['f_sh'] = body(J['f_sh'], lean)
        P['b_hip'] = body(J['b_hip'])
        P['f_hip'] = body(J['f_hip'])
        A = {'torso': self.rest_ang['torso'] + R + lean}
        A['head'] = self.rest_ang['head'] + R + lean + p['head']
        P['head'] = add(P['neck'], rot((self.L['head'], 0), A['head']))
        # brazos (IK en marco del torso)
        for s in 'bf':
            sh = P[s + '_sh']
            tgt_local = mul((p[s + 'hx'], p[s + 'hy']), self.armlen[s])
            T = add(sh, rot(tgt_local, R + lean))
            L1, L2 = self.L[s + '_up'], self.L[s + '_lo']
            k = min(1.4, max(1.0, length(sub(T, sh)) / ((L1 + L2) * 0.985)))
            E, Tn = ik2(sh, T, L1 * k, L2 * k, self.arm_sign[s])
            P[s + '_el'], P[s + '_ha'] = E, Tn
            self._scale[s + '_up'] = self._scale[s + '_lo'] = k
            A[s + '_up'] = ang(sub(E, sh)); A[s + '_lo'] = ang(sub(Tn, E))
        # piernas
        anc = self.anchor
        for s in 'bf':
            hip = P[s + '_hip']
            off = (p[s + 'fx'] * u, p[s + 'fy'] * u)
            ground_t = add(J[s + '_an'], off)
            body_t = add(pel, rot(add(sub(J[s + '_an'], pel0), off), R))
            w = p['lrel']
            T = (ground_t[0] * (1 - w) + body_t[0] * w, ground_t[1] * (1 - w) + body_t[1] * w)
            K, Tn = ik2(hip, T, self.L[s + '_th'], self.L[s + '_shin'], self.leg_sign[s])
            P[s + '_kn'], P[s + '_an'] = K, Tn
            A[s + '_th'] = ang(sub(K, hip)); A[s + '_shin'] = ang(sub(Tn, K))
            A[s + '_foot'] = self.rest_ang[s + '_foot'] + p[s + 'fa'] + R * w
            P[s + '_toe'] = add(Tn, rot((self.L[s + '_foot'], 0), A[s + '_foot']))
        return P, A

    # ------------------------------------------------------------ render
    def render(self, p, quantize=True):
        P, A = self.solve(p)
        W, Hh = CANVAS_W * SS, CANVAS_H * SS
        # traslación: ancla de reposo -> ancla de lienzo
        ox = ANCHOR_X * SS - self.anchor[0]
        oy = ANCHOR_Y * SS - self.anchor[1]
        canvas = np.zeros((Hh, W, 4), np.float32)
        for b in self.order:
            if b == 'b_up' and p.get('prop') == 'guitar':
                self._draw_guitar(canvas, P, ox, oy)
            if b not in self.parts:
                continue
            crop, (cx, cy) = self.parts[b]
            j0 = BONES[b][0]
            src_p = self.J[j0]
            dst_p = P[j0]
            k = self._scale.get(b, 1.0)
            rs, rd = math.radians(self.rest_ang[b]), math.radians(A[b])
            Rs_inv = np.array([[math.cos(rs), math.sin(rs)], [-math.sin(rs), math.cos(rs)]])
            Rd = np.array([[math.cos(rd), -math.sin(rd)], [math.sin(rd), math.cos(rd)]])
            M = np.zeros((2, 3))
            M[:, :2] = Rd @ np.diag([k, 1.0]) @ Rs_inv
            t = np.array([cx - src_p[0], cy - src_p[1]])
            M[:, 2] = M[:, :2] @ t + np.array([dst_p[0] + ox, dst_p[1] + oy])
            warped = cv2.warpAffine(crop, M, (W, Hh), flags=cv2.INTER_NEAREST,
                                    borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            a = warped[..., 3:4].astype(np.float32) / 255
            canvas[..., :3] = canvas[..., :3] * (1 - a) + warped[..., :3] * a
            canvas[..., 3:4] = canvas[..., 3:4] * (1 - a) + a
        if p.get('sx', 1) != 1 or p.get('sy', 1) != 1:
            ax, ay = ANCHOR_X * SS, ANCHOR_Y * SS
            M = np.array([[p['sx'], 0, ax - ax * p['sx']], [0, p['sy'], ay - ay * p['sy']]])
            canvas = cv2.warpAffine(canvas, M, (W, Hh), flags=cv2.INTER_NEAREST)
        # reducción a nativo
        prem = canvas.copy()
        prem[..., :3] *= prem[..., 3:4]
        small = cv2.resize(prem, (CANVAS_W, CANVAS_H), interpolation=cv2.INTER_AREA)
        al = small[..., 3]
        rgb = np.where(al[..., None] > 1e-4, small[..., :3] / np.maximum(al[..., None], 1e-4), 0)
        out = np.zeros((CANVAS_H, CANVAS_W, 4), np.uint8)
        mask = al > 0.45
        rgb = np.clip(rgb, 0, 255)
        if quantize and self.palette is not None:
            px = rgb[mask].astype(np.float32)
            d = ((px[:, None, :] - self.palette[None, :, :]) ** 2).sum(2)
            rgb_q = self.palette[np.argmin(d, 1)]
            out[mask, :3] = rgb_q.astype(np.uint8)
        else:
            out[mask, :3] = rgb[mask].astype(np.uint8)
        out[mask, 3] = 255
        if quantize and self.palette is not None:
            out = self._finish(out)
        return out, P

    def _finish(self, out):
        """Cierra huecos pequeños entre partes y repasa el contorno oscuro."""
        mask = (out[..., 3] > 0).astype(np.uint8)
        closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        # sólo huecos realmente encerrados o rendijas finas
        new = (closed > 0) & (mask == 0)
        if new.any():
            fill = cv2.inpaint(out[..., :3].copy(), new.astype(np.uint8) * 255, 2, cv2.INPAINT_TELEA)
            d = ((fill[new].astype(np.float32)[:, None, :] - self.palette[None]) ** 2).sum(2)
            out[new, :3] = self.palette[np.argmin(d, 1)].astype(np.uint8)
            out[new, 3] = 255
            mask = closed
        edge = (mask > 0) & (cv2.erode(mask, np.ones((3, 3), np.uint8)) == 0)
        lum = out[..., :3].astype(np.float32).sum(2)
        dark = self.palette[np.argmin(self.palette.sum(1))].astype(np.uint8)
        out[edge & (lum > 150)] = np.append(dark, 255)
        return out

    def _draw_guitar(self, canvas, P, ox, oy):
        g = guitar_sprite()
        g = cv2.resize(g, None, fx=SS, fy=SS, interpolation=cv2.INTER_NEAREST)
        a0 = P['b_ha']; a1 = P['f_ha']
        th = math.atan2(a1[1] - a0[1] + 6 * SS, a1[0] - a0[0])
        c, s_ = math.cos(th), math.sin(th)
        bx, by = 10 * SS, 8 * SS              # centro del cuerpo de la guitarra
        cx, cy = a0[0] - 2 * SS + ox, a0[1] + 3 * SS + oy
        M = np.array([[c, -s_, 0], [s_, c, 0]], np.float64)
        M[:, 2] = np.array([cx, cy]) - M[:, :2] @ np.array([bx, by])
        H_, W_ = canvas.shape[:2]
        w = cv2.warpAffine(g, M, (W_, H_), flags=cv2.INTER_NEAREST)
        a = w[..., 3:4].astype(np.float32) / 255
        canvas[..., :3] = canvas[..., :3] * (1 - a) + w[..., :3] * a
        canvas[..., 3:4] = canvas[..., 3:4] * (1 - a) + a

    def build_palette(self, k=40):
        img, _ = self.render(self.default_params(), quantize=False)
        px = img[img[..., 3] > 0, :3].astype(np.float32)
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.5)
        _, _, centers = cv2.kmeans(px, k, None, crit, 4, cv2.KMEANS_PP_CENTERS)
        self.palette = centers.astype(np.float32)

    def to_native(self, pt):
        """Convierte un punto del espacio de trabajo a coordenadas del fotograma nativo."""
        return ((pt[0] - self.anchor[0]) / SS + ANCHOR_X, (pt[1] - self.anchor[1]) / SS + ANCHOR_Y)


_GUITAR = None


def guitar_sprite():
    """Guitarra pixel-art original (54x17 px nativos)."""
    global _GUITAR
    if _GUITAR is not None:
        return _GUITAR
    W, H = 56, 17
    im = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    body = (((xx - 7) / 7.0) ** 2 + ((yy - 8) / 7.6) ** 2 <= 1) | \
           (((xx - 15) / 5.5) ** 2 + ((yy - 8) / 6.0) ** 2 <= 1)
    neck = (xx >= 18) & (xx <= 49) & (yy >= 7) & (yy <= 9)
    headst = (xx >= 49) & (xx <= 55) & (yy >= 6) & (yy <= 10)
    shape = body | neck | headst
    out = cv2.dilate(shape.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    im[out] = (25, 15, 20, 255)
    # cuerpo sunburst
    d = np.hypot(xx - 9, yy - 8)
    col = np.where(d[..., None] < 4.5, np.array([250, 170, 40]),
                   np.where(d[..., None] < 7, np.array([220, 90, 30]), np.array([140, 40, 25])))
    im[body, :3] = col[body]; im[body, 3] = 255
    im[neck] = (120, 70, 35, 255)
    im[neck & (yy == 8)] = (90, 50, 25, 255)
    im[headst] = (60, 30, 20, 255)
    for fx in range(22, 49, 4):
        im[(xx == fx) & neck] = (220, 220, 200, 255)
    im[(yy == 8) & (xx >= 4) & (xx <= 49)] = (235, 235, 225, 255)   # cuerdas
    im[(np.hypot(xx - 13, yy - 8) < 1.6)] = (20, 10, 10, 255)       # boca
    im[(xx >= 4) & (xx <= 5) & (yy >= 6) & (yy <= 10)] = (40, 25, 20, 255)  # puente
    for py_ in (6, 10):
        im[py_, 51] = im[py_, 53] = (230, 230, 230, 255)
    _GUITAR = im
    return im
