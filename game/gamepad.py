"""Soporte de joysticks / mandos (Xbox, PlayStation, genéricos USB).

Cada jugador elige en OPCIONES si juega con TECLADO, MANDO o ambos a la vez.

- En combate, el mando se lee cada tick (cruceta, stick izquierdo y botones).
- En los menús, los movimientos y botones del mando se traducen a eventos de
  teclado "sintéticos" para que todas las pantallas funcionen sin cambios.
  Esos eventos llevan atributos extra: ``pad`` ('up', 'down', 'left', 'right',
  'ok', 'back', 'start'), ``player`` (1 o 2) y ``action`` (acción de combate
  asociada al botón, si tiene).

Botones por defecto (numeración SDL de un mando estilo Xbox; los de PlayStation
equivalen a: A=X, B=O, X=□, Y=△):
    A (0) patada · B (1) bloquear · X (2) puñetazo · Y (3) especial
    LB (4) bloquear · RB (5) ultimate · RT ultimate · START pausa · BACK volver
Se pueden reasignar en OPCIONES → CONTROLES JUGADOR 1 / 2.
"""
import pygame
import config as C

DEADZONE = 0.5
TRIGGER_BASE = 100          # "botón" virtual: 100 + eje (gatillos analógicos)
MENU_OK_BUTTONS = (0,)      # A / ✕
MENU_BACK_BUTTONS = (1, 6)  # B / ○ y BACK / SELECT
START_BUTTONS = (7, 9)      # START (Xbox = 7; algunos genéricos = 9)

DEFAULT_PAD = {
    'golpe': [2], 'patada': [0], 'especial': [3], 'ultimate': [5, 105], 'bloquear': [1, 4],
}

INPUT_MODES = ['ambos', 'teclado', 'mando']
INPUT_NAMES = {'ambos': 'TECLADO + MANDO', 'teclado': 'SÓLO TECLADO', 'mando': 'SÓLO MANDO'}
PAD_SLOTS = ['auto', 0, 1]


def button_name(b):
    if b >= TRIGGER_BASE:
        return {104: 'LT', 105: 'RT', 102: 'LT', 103: 'RT'}.get(b, f'EJE {b - TRIGGER_BASE}')
    return {0: 'A', 1: 'B', 2: 'X', 3: 'Y', 4: 'LB', 5: 'RB', 6: 'BACK', 7: 'START',
            8: 'L3', 9: 'R3'}.get(b, f'BOTÓN {b}')


class PadManager:
    def __init__(self, settings):
        self.settings = settings
        self.pads = []            # Joystick abiertos, en orden de conexión
        self.dir_state = {}       # instance_id -> set de direcciones activas (para menús)
        self.trig_state = {}      # (instance_id, eje) -> pulsado
        try:
            pygame.joystick.init()
            for i in range(pygame.joystick.get_count()):
                self._open(i)
        except pygame.error:
            pass

    # ------------------------------------------------------------ dispositivos
    def _open(self, index):
        try:
            j = pygame.joystick.Joystick(index)
            j.init()
        except pygame.error:
            return
        iid = self._iid(j)
        if all(self._iid(p) != iid for p in self.pads):
            self.pads.append(j)

    @staticmethod
    def _iid(j):
        try:
            return j.get_instance_id()
        except AttributeError:          # pygame < 2
            return j.get_id()

    def _remove(self, iid):
        self.pads = [p for p in self.pads if self._iid(p) != iid]
        self.dir_state.pop(iid, None)

    def count(self):
        return len(self.pads)

    def name(self, idx):
        if 0 <= idx < len(self.pads):
            try:
                return self.pads[idx].get_name()
            except pygame.error:
                return 'MANDO'
        return None

    # ------------------------------------------------------------ asignación
    def mode(self, player):
        m = self.settings.data.get('input_mode', {}).get(str(player), 'ambos')
        return m if m in INPUT_MODES else 'ambos'

    def slot(self, player):
        s = self.settings.data.get('pad_slot', {}).get(str(player), 'auto')
        return s if s in PAD_SLOTS else 'auto'

    def pad_for(self, player):
        """Joystick asignado al jugador (o None)."""
        if self.mode(player) == 'teclado':
            return None
        s = self.slot(player)
        if s != 'auto':
            return self.pads[s] if s < len(self.pads) else None
        # automático: los mandos se reparten en orden entre los jugadores que los usan,
        # sin repetir los que ya están fijados a mano por el otro jugador
        taken = set()
        other = 2 if player == 1 else 1
        if self.mode(other) != 'teclado' and self.slot(other) != 'auto':
            taken.add(self.slot(other))
        free = [i for i in range(len(self.pads)) if i not in taken]
        order = [p for p in (1, 2) if self.mode(p) != 'teclado' and self.slot(p) == 'auto']
        k = order.index(player)
        return self.pads[free[k]] if k < len(free) else None

    def player_of(self, joy_iid):
        for p in (1, 2):
            j = self.pad_for(p)
            if j is not None and self._iid(j) == joy_iid:
                return p
        return None

    def buttons(self, player):
        pc = self.settings.data.setdefault('pad_controls', {})
        m = pc.setdefault(str(player), {})
        for a, v in DEFAULT_PAD.items():
            m.setdefault(a, list(v))
        return m

    # ------------------------------------------------------------ lectura en combate
    @staticmethod
    def _button_down(j, b):
        try:
            if b >= TRIGGER_BASE:
                ax = b - TRIGGER_BASE
                return ax < j.get_numaxes() and j.get_axis(ax) > 0.3
            return b < j.get_numbuttons() and j.get_button(b)
        except pygame.error:
            return False

    @staticmethod
    def _dirs(j):
        x = y = 0.0
        try:
            if j.get_numhats() > 0:
                hx, hy = j.get_hat(0)
                x, y = hx, -hy
            if j.get_numaxes() >= 2 and x == 0 and y == 0:
                ax, ay = j.get_axis(0), j.get_axis(1)
                x = -1 if ax < -DEADZONE else 1 if ax > DEADZONE else 0
                y = -1 if ay < -DEADZONE else 1 if ay > DEADZONE else 0
        except pygame.error:
            pass
        return x, y

    def read(self, player):
        """Acciones mantenidas por el mando del jugador (dict acción -> bool)."""
        out = {a: False for a in C.ACTIONS}
        j = self.pad_for(player)
        if j is None:
            return out
        x, y = self._dirs(j)
        out['izquierda'] = x < 0
        out['derecha'] = x > 0
        out['arriba'] = y < 0
        out['abajo'] = y > 0
        for a, bl in self.buttons(player).items():
            if a in out:
                out[a] = any(self._button_down(j, b) for b in bl)
        return out

    def start_pressed_raw(self, e):
        return e.type == pygame.JOYBUTTONDOWN and e.button in START_BUTTONS

    # ------------------------------------------------------------ eventos
    def handle_device_event(self, e):
        if e.type == getattr(pygame, 'JOYDEVICEADDED', -1):
            self._open(e.device_index)
            return True
        if e.type == getattr(pygame, 'JOYDEVICEREMOVED', -1):
            self._remove(e.instance_id)
            return True
        return False

    def _key_for(self, player, action):
        keys = self.settings.controls(player).get(action) or []
        return keys[0] if keys else 0

    def _synth(self, player, pad, action=None, key=None, button=None):
        if key is None:
            key = self._key_for(player, action) if action else 0
        return pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode='', scancode=0,
                                  pad=pad, player=player, action=action, button=button)

    def translate(self, e):
        """Convierte un evento de joystick en eventos de teclado para los menús."""
        out = []
        iid = getattr(e, 'instance_id', getattr(e, 'joy', None))
        if e.type not in (pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
            return out
        p = self.player_of(iid)
        if p is None:
            return out
        if e.type == pygame.JOYBUTTONDOWN:
            b = e.button
            act = next((a for a, bl in self.buttons(p).items() if b in bl), None)
            if b in START_BUTTONS:
                out.append(self._synth(p, 'start', key=pygame.K_ESCAPE, button=b))
            elif b in MENU_OK_BUTTONS:
                out.append(self._synth(p, 'ok', act or 'golpe', button=b))
            elif b in MENU_BACK_BUTTONS:
                out.append(self._synth(p, 'back', act or 'patada', button=b))
            elif act:
                out.append(self._synth(p, None, act, button=b))
            return out
        if e.type == pygame.JOYAXISMOTION and e.axis >= 2:
            # gatillos analógicos como botones virtuales
            k = (iid, e.axis)
            down = e.value > 0.3
            if down and not self.trig_state.get(k):
                b = TRIGGER_BASE + e.axis
                act = next((a for a, bl in self.buttons(p).items() if b in bl), None)
                if act:
                    out.append(self._synth(p, None, act, button=b))
            self.trig_state[k] = down
            return out
        # direcciones (cruceta o stick): sólo al entrar en una dirección nueva
        j = next((q for q in self.pads if self._iid(q) == iid), None)
        if j is None:
            return out
        x, y = self._dirs(j)
        now = set()
        if x < 0: now.add('left')
        if x > 0: now.add('right')
        if y < 0: now.add('up')
        if y > 0: now.add('down')
        prev = self.dir_state.get(iid, set())
        act_of = {'left': 'izquierda', 'right': 'derecha', 'up': 'arriba', 'down': 'abajo'}
        for d in ('up', 'down', 'left', 'right'):
            if d in now and d not in prev:
                out.append(self._synth(p, d, act_of[d]))
        self.dir_state[iid] = now
        return out


_mgr = None


def manager(settings=None):
    global _mgr
    if _mgr is None and settings is not None:
        _mgr = PadManager(settings)
    return _mgr
