"""Herramientas del modo Entrenamiento (rival dummy, hitboxes, reinicio)."""
import pygame


class TrainingTools:
    MODES = 5

    def __init__(self, scene):
        self.scene = scene

    def handle_key(self, key):
        m = self.scene.match
        a = self.scene.audio
        if key == pygame.K_F1:
            m.dummy_mode = (m.dummy_mode + 1) % self.MODES
            a.play('menu_mover')
        elif key == pygame.K_F2:
            m.show_hitboxes = not m.show_hitboxes
            a.play('menu_mover')
        elif key == pygame.K_F3:
            for f in (m.p1, m.p2):
                f.reset_round()
                f.meter = 100
            m.projectiles = []
            a.play('menu_ok')
