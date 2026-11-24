"""Entrada de jugadores: estado de teclas por acción, flancos y búfer."""
import pygame
import config as C


class InputState:
    """Estado lógico de un jugador en un tick (teclado o IA)."""

    def __init__(self):
        self.held = {a: False for a in C.ACTIONS}
        self.pressed = {a: False for a in C.ACTIONS}
        self.buffer = {a: 0 for a in C.ACTIONS}   # ticks restantes de búfer

    def set(self, new_held):
        for a in C.ACTIONS:
            p = new_held[a] and not self.held[a]
            self.pressed[a] = p
            if p:
                self.buffer[a] = 6
            elif self.buffer[a] > 0:
                self.buffer[a] -= 1
            self.held[a] = new_held[a]

    def take(self, a):
        """Consume una pulsación (con búfer de unos ticks)."""
        if self.buffer[a] > 0:
            self.buffer[a] = 0
            return True
        return False

    def clear(self):
        for a in C.ACTIONS:
            self.buffer[a] = 0
            self.pressed[a] = False


class KeyboardController:
    def __init__(self, settings, player):
        self.settings = settings
        self.player = player

    def read(self, keys):
        m = self.settings.controls(self.player)
        return {a: any(keys[k] for k in m[a] if 0 <= k < len(keys)) if True else False
                for a in C.ACTIONS}


def key_name(k):
    n = pygame.key.name(k).upper()
    return {'LEFT': '←', 'RIGHT': '→', 'UP': '↑', 'DOWN': '↓', '[1]': 'NUM1', '[2]': 'NUM2',
            '[3]': 'NUM3', '[4]': 'NUM4', '[5]': 'NUM5'}.get(n, n)


def _key_ok(keys, k):
    try:
        return bool(keys[k])
    except IndexError:
        return False


class KeyboardControllerSafe(KeyboardController):
    """Jugador humano: teclado, mando o ambos según OPCIONES → ENTRADA."""

    def read(self, keys):
        from game import gamepad
        mgr = gamepad.manager()
        mode = mgr.mode(self.player) if mgr else 'teclado'
        if mode != 'mando':
            m = self.settings.controls(self.player)
            out = {a: any(_key_ok(keys, k) for k in m[a]) for a in C.ACTIONS}
        else:
            out = {a: False for a in C.ACTIONS}
        if mgr is not None and mode != 'teclado':
            pad = mgr.read(self.player)
            for a in C.ACTIONS:
                out[a] = out[a] or pad[a]
        return out
