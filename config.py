"""Configuración global de IES 10 FIGHTER."""
import os
import json
import pygame

GAME_TITLE = 'IES 10 FIGHTER'
WIDTH, HEIGHT = 1280, 720
FPS = 60
SCALE = 3                      # escala de los sprites pixel-art

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE_DIR, 'assets')
CHAR_DIR = os.path.join(ASSETS, 'characters')
FX_DIR = os.path.join(ASSETS, 'effects')
SND_DIR = os.path.join(ASSETS, 'sounds')
MUS_DIR = os.path.join(ASSETS, 'music')
UI_DIR = os.path.join(ASSETS, 'interface')
FONT_PATH = os.path.join(ASSETS, 'fonts', 'PressStart2P-Regular.ttf')
BG_PATH = os.path.join(ASSETS, 'backgrounds', 'escenario.jpg')
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.json')

CHARACTERS = ['pantoja', 'parada', 'nehuen', 'luciano', 'nico']
BOSS = 'nico'

# Escenarios: la imagen se escala con la misma proporción en X e Y (sin deformar)
STAGES = {
    'aula': dict(name='AULA DEL IES 10', file='escenario.jpg', height=860, ground_src=1330, indoor=True),
    'plaza': dict(name='LA PLAZA', file='plaza.png', height=989, ground_src=700, indoor=False),
}
STAGE_ORDER = ['aula', 'plaza']

# Estadio: la imagen se escala manteniendo proporción (sin deformar)
STAGE_HEIGHT = 860
GROUND_SRC_Y = 1330            # línea del piso en la imagen original (px)

# ------------------------------------------------------------------ controles
ACTIONS = ['izquierda', 'derecha', 'arriba', 'abajo', 'golpe', 'patada', 'especial', 'ultimate', 'bloquear']
ACTION_NAMES = {
    'izquierda': 'IZQUIERDA', 'derecha': 'DERECHA', 'arriba': 'SALTAR', 'abajo': 'AGACHARSE',
    'golpe': 'PUÑETAZO', 'patada': 'PATADA', 'especial': 'ESPECIAL', 'ultimate': 'ULTIMATE',
    'bloquear': 'BLOQUEAR',
}
DEFAULT_CONTROLS = {
    1: {'izquierda': [pygame.K_a], 'derecha': [pygame.K_d], 'arriba': [pygame.K_w],
        'abajo': [pygame.K_s], 'golpe': [pygame.K_f], 'patada': [pygame.K_g],
        'especial': [pygame.K_r], 'ultimate': [pygame.K_t], 'bloquear': [pygame.K_e]},
    2: {'izquierda': [pygame.K_LEFT], 'derecha': [pygame.K_RIGHT], 'arriba': [pygame.K_UP],
        'abajo': [pygame.K_DOWN], 'golpe': [pygame.K_1, pygame.K_KP1],
        'patada': [pygame.K_2, pygame.K_KP2], 'especial': [pygame.K_3, pygame.K_KP3],
        'ultimate': [pygame.K_4, pygame.K_KP4], 'bloquear': [pygame.K_5, pygame.K_KP5]},
}

DIFFICULTIES = ['FÁCIL', 'NORMAL', 'DIFÍCIL', 'EXTREMO']
TIMER_OPTIONS = [30, 60, 99, 0]          # 0 = infinito

DEFAULT_SETTINGS = {
    'music_volume': 0.6,
    'sfx_volume': 0.8,
    'voice_volume': 0.9,
    'round_time': 99,
    'difficulty': 1,
    'rounds_to_win': 2,
    'fullscreen': False,
    'crt': True,
    'show_intro': True,
    'controls': {str(k): v for k, v in DEFAULT_CONTROLS.items()},
}


class Settings:
    def __init__(self):
        self.data = json.loads(json.dumps(DEFAULT_SETTINGS))
        self.load()

    def load(self):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                d = json.load(f)
            for k, v in d.items():
                if k in self.data:
                    self.data[k] = v
            # completar acciones faltantes
            for p in ('1', '2'):
                ctl = self.data['controls'].setdefault(p, {})
                for a in ACTIONS:
                    ctl.setdefault(a, DEFAULT_CONTROLS[int(p)][a])
        except (OSError, ValueError):
            pass

    def save(self):
        try:
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=1)
        except OSError:
            pass

    def __getitem__(self, k):
        return self.data[k]

    def __setitem__(self, k, v):
        self.data[k] = v

    def controls(self, player):
        return self.data['controls'][str(player)]

    def reset_controls(self):
        self.data['controls'] = {str(k): dict(v) for k, v in DEFAULT_CONTROLS.items()}


# Colores de interfaz
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 214, 10)
ORANGE = (255, 140, 0)
RED = (230, 30, 40)
CYAN = (40, 210, 255)
IES_BLUE = (25, 60, 160)
IES_GREEN = (30, 200, 140)
