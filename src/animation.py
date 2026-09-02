import math
import time

class AnimationState:
    def __init__(self, fade_speed=4.5):
        self.opacity = 0.0
        self.fade_speed = float(fade_speed)
        self.last = time.perf_counter()

    def update(self, visible):
        now = time.perf_counter()
        dt = min(now - self.last, 0.1)
        self.last = now
        direction = 1.0 if visible else -1.0
        self.opacity = max(0.0, min(1.0, self.opacity + direction*self.fade_speed*dt))
        return self.opacity

    def transform(self, base_scale, bounce=True, floating=True, rotation=False):
        t = time.perf_counter()
        scale = float(base_scale)
        y = 0
        angle = 0
        if bounce:
            scale *= 1.0 + 0.035*math.sin(t*7.0)
        if floating:
            y = int(math.sin(t*2.8)*10)
        if rotation:
            angle = math.sin(t*2.0)*4.0
        return scale, y, angle
