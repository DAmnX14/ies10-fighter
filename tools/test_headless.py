"""
Prueba automática sin ventana: recorre todas las pantallas, simula combates
CPU vs CPU con todos los personajes y verifica colisiones, daño y sonidos.
Uso: python tools/test_headless.py [carpeta_capturas]
"""
import os
import sys
import random
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
import pygame
import config as C

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'documentation', 'capturas')
os.makedirs(OUT, exist_ok=True)

from main import Game

played = []


def main():
    g = Game()
    orig_play = g.audio.play
    def spy(name, vol=1.0):
        played.append(name); orig_play(name, vol)
    g.audio.play = spy
    g.settings['crt'] = True

    def run(n, shot=None, at=None):
        for i in range(n):
            g.step()
            if shot and at is not None and i in at:
                pygame.image.save(g.screen, os.path.join(OUT, f'{shot}_{i}.png'))

    def key(k):
        g.scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode=''))

    from screens.intro import IntroScene
    g.change(lambda: IntroScene(g), instant=True)
    run(1130, 'intro', {60, 220, 400, 580, 700, 820, 1000})
    run(60)
    from screens.main_menu import TitleScene
    g.change(lambda: TitleScene(g), instant=True)
    run(60, 'titulo', {50})
    key(pygame.K_RETURN); run(30)
    key(pygame.K_DOWN); run(20, 'menu', {15})
    from screens.character_select import CharacterSelect
    g.change(lambda: CharacterSelect(g, 'versus'), instant=True)
    run(30)
    key(pygame.K_f); key(pygame.K_RIGHT); run(10); key(pygame.K_1)
    run(60, 'seleccion', {20})
    from screens.versus import VersusScreen
    g.change(lambda: VersusScreen(g, 'pantoja', 'parada', 'cpu'), instant=True)
    run(120, 'vs', {100})
    from screens.fight import FightScene
    from game.ai import AIController
    stats = {}
    pairs = [('pantoja', 'parada'), ('nehuen', 'luciano'), ('parada', 'nehuen'), ('luciano', 'pantoja')]
    for idx, (a, b) in enumerate(pairs):
        done = {}
        fs = FightScene(g, a, b, 'cpu', lambda s: done.setdefault('x', 1), 3)
        fs.ctrl[1] = AIController(3)
        g.change(lambda: fs, instant=True)
        m = fs.match
        dmg_events = 0
        last = (m.p1.health, m.p2.health)
        ult_shot = False
        for i in range(60 * 200):
            if i % 600 == 0:
                m.p1.meter = m.p2.meter = 100      # forzar ultimates para probarlos
            g.step()
            h = (m.p1.health, m.p2.health)
            if h != last:
                dmg_events += 1
                last = h
            if i in (400, 1500):
                pygame.image.save(g.screen, os.path.join(OUT, f'combate_{a}_{b}_{i}.png'))
            if m.cutin and m.cutin['t'] == 20 and not ult_shot:
                pygame.image.save(g.screen, os.path.join(OUT, f'ultimate_{a}_{b}.png')); ult_shot = True
            if any(f.move is not None and f.move.get('ult') and f.mframe == 6 for f in (m.p1, m.p2)) and i % 3 == 0 \
                    and not os.path.exists(os.path.join(OUT, f'ult_accion_{a}_{b}.png')):
                pygame.image.save(g.screen, os.path.join(OUT, f'ult_accion_{a}_{b}.png'))
            if done:
                break
        stats[(a, b)] = dict(ticks=i, damage_events=dmg_events, winner=m.winner.name if m.winner else None,
                             rounds=m.round, p1=m.p1.wins, p2=m.p2.wins)
        print(a, 'vs', b, stats[(a, b)], flush=True)
    from screens.results import ResultScreen
    g.change(lambda: ResultScreen(g, 'nehuen', 'luciano', 1, 'versus'), instant=True)
    run(120, 'resultado', {100})
    from screens.gallery import GalleryScene
    g.change(lambda: GalleryScene(g), instant=True)
    run(40, 'galeria', {30})
    from screens.options import OptionsScene
    g.change(lambda: OptionsScene(g), instant=True)
    run(20, 'opciones', {10})
    # entrenamiento
    fs = FightScene(g, 'luciano', 'pantoja', 'training', lambda s: None, 1)
    g.change(lambda: fs, instant=True)
    run(120, 'entrenamiento', {100})
    from screens.arcade import ArcadeRun, LadderScreen, ContinueScreen, EndingScreen
    run_ = ArcadeRun(g, 'parada')
    g.change(lambda: LadderScreen(g, run_), instant=True)
    run(40, 'arcade', {30})
    g.change(lambda: EndingScreen(g, run_), instant=True)
    run(400, 'final', {350})
    used = sorted(set(played))
    print('sonidos reproducidos:', len(used))
    missing = [s for s in used if s not in g.audio.sounds]
    print('sonidos faltantes:', missing)
    pygame.quit()


if __name__ == '__main__':
    main()
