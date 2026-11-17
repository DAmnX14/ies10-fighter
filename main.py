"""
IES 10 FIGHTER - juego de lucha 2D estilo arcade de los 90.
Ejecutar:  python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
import config as C


class Game:
    def __init__(self, headless=False):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption(C.GAME_TITLE)
        self.settings = C.Settings()
        icon_path = os.path.join(C.UI_DIR, 'icono.png')
        if os.path.exists(icon_path):
            pygame.display.set_icon(pygame.image.load(icon_path))
        flags = pygame.SCALED | (pygame.FULLSCREEN if self.settings['fullscreen'] else 0)
        try:
            self.screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT), flags, vsync=1)
        except pygame.error:
            self.screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT), flags)
        self.world_surf = pygame.Surface((C.WIDTH, C.HEIGHT)).convert()
        self.clock = pygame.time.Clock()
        from game.audio import Audio
        from game import assets
        from game.ui import Transition
        self.audio = Audio(self.settings)
        self.loading_screen()
        assets.preload_all()
        self.transition = Transition()
        self.scene = None
        self.stage_id = 'aula'
        self.running = True
        self.tick = 0

    def loading_screen(self):
        from game import ui
        self.screen.fill((8, 6, 20))
        ui.blit_center(self.screen, ui.text_gradient('IES 10 FIGHTER', 44, extrude=5), C.WIDTH / 2, C.HEIGHT / 2 - 30)
        ui.blit_center(self.screen, ui.text('CARGANDO...', 16, C.WHITE), C.WIDTH / 2, C.HEIGHT / 2 + 50)
        ui.blit_center(self.screen, ui.text('ARCE TECH', 14, (60, 220, 120)), C.WIDTH / 2, C.HEIGHT - 60)
        pygame.display.flip()

    def change(self, factory, instant=False):
        """Cambia de pantalla con transición. factory: función que crea la escena."""
        def go():
            self.scene = factory()
        if instant or self.scene is None:
            go()
        elif not self.transition.active:
            self.transition.start(go)

    def toggle_fullscreen(self):
        self.settings['fullscreen'] = not self.settings['fullscreen']
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            pass

    def run(self):
        from screens.intro import IntroScene
        from screens.main_menu import TitleScene
        if self.settings['show_intro']:
            self.change(lambda: IntroScene(self), instant=True)
        else:
            self.change(lambda: TitleScene(self), instant=True)
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif not self.transition.active:
                    self.scene.handle_event(e)
            self.step()
            pygame.display.flip()
            self.clock.tick(C.FPS)
        self.settings.save()
        pygame.quit()

    def step(self):
        from game import ui
        self.tick += 1
        self.scene.update()
        self.transition.update()
        self.scene.draw(self.screen)
        if self.settings['crt']:
            ui.crt(self.screen)
        self.transition.draw(self.screen)

    def quit(self):
        self.running = False


def main():
    Game().run()


if __name__ == '__main__':
    main()
