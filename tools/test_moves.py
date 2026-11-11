"""Prueba cada movimiento de cada personaje contra un rival quieto y reporta el daño."""
import os, sys
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
import pygame
import config as C
from main import Game
from game.combat import Match
from game.controls import InputState

MOVES = ['golpe', 'patada', 'golpe_fuerte', 'patada_fuerte', 'golpe_agachado', 'patada_agachado',
         'especial_1', 'especial_2', 'ultimate_1', 'ultimate_2']


def main():
    g = Game()
    shots = sys.argv[1] if len(sys.argv) > 1 else None
    bad = []
    for c in C.CHARACTERS:
        row = []
        for mv in MOVES:
            best = 0
            for dist in (150, 260, 420):
                m = Match(g, c, 'pantoja' if c != 'pantoja' else 'luciano', 'versus')
                m.state = 'fight'; m.controls_enabled = True
                m.p1.state = m.p2.state = 'idle'
                mid = m.stage.w / 2
                m.p1.x, m.p2.x = mid - dist / 2, mid + dist / 2
                inputs = {1: InputState(), 2: InputState()}
                h0 = m.p2.health
                m.p1.meter = 100
                if mv.startswith('ultimate'):
                    m.p1.start_ultimate(mv)
                else:
                    m.p1.start_move(mv)
                for i in range(400):
                    m.update(inputs)
                    if shots and dist == 260 and mv.startswith('ultimate') and i in (70, 110):
                        g.world_surf.fill((0, 0, 0))
                        m.draw(g.screen)
                        pygame.image.save(g.screen, os.path.join(shots, f'mov_{c}_{mv}_{i}.png'))
                dmg = h0 - m.p2.health
                best = max(best, dmg)
            row.append(f'{mv}={best}')
            if best <= 0:
                bad.append((c, mv))
        print(c, ' '.join(row), flush=True)
    print('SIN DAÑO:', bad)
    pygame.quit()


if __name__ == '__main__':
    main()
