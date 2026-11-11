"""Cámara del combate: seguimiento, límites, zoom y temblor de pantalla."""
import random
import config as C


class Camera:
    def __init__(self, stage_w, stage_h):
        self.sw, self.sh = stage_w, stage_h
        self.x = (stage_w - C.WIDTH) / 2
        self.y = stage_h - C.HEIGHT
        self.base_y = self.y
        self.shake_amp = 0.0
        self.shake_t = 0
        self.ox = self.oy = 0
        self.zoom = 1.0
        self.zoom_target = 1.0
        self.focus = None

    def shake(self, amp, ticks):
        if amp >= self.shake_amp or self.shake_t <= 0:
            self.shake_amp, self.shake_t = amp, ticks

    def update(self, f1, f2):
        if self.focus is not None:
            cx = self.focus.x
        else:
            cx = (f1.x + f2.x) / 2
        tx = cx - C.WIDTH / 2
        tx = max(0, min(self.sw - C.WIDTH, tx))
        self.x += (tx - self.x) * 0.15
        # sube un poco si alguien salta alto
        top = min(f1.y, f2.y)
        ground = f1.ground_y
        lift = max(0, (ground - top) - 250) * 0.5
        ty = max(0, self.base_y - lift)
        self.y += (ty - self.y) * 0.12
        self.zoom += (self.zoom_target - self.zoom) * 0.15
        if self.shake_t > 0:
            self.shake_t -= 1
            k = self.shake_t / 30 + 0.2
            self.ox = random.uniform(-1, 1) * self.shake_amp * min(1, k)
            self.oy = random.uniform(-1, 1) * self.shake_amp * min(1, k)
        else:
            self.ox = self.oy = 0
            self.shake_amp = 0

    def to_screen(self, x, y):
        return x - self.x + self.ox, y - self.y + self.oy
