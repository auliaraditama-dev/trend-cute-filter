import math
import time

class AnimationState:
    def __init__(self, fade_speed=4.5):
        self.opacity = 0.0
        self.fade_speed = float(fade_speed)
        self.last = time.perf_counter()

    def update(self, visible, fade_speed=None):
        now = time.perf_counter()
        dt = min(now - self.last, 0.1)
        self.last = now
        speed = self.fade_speed if fade_speed is None else float(fade_speed)
        direction = 1.0 if visible else -1.0
        self.opacity = max(0.0, min(1.0, self.opacity + direction * speed * dt))
        return self.opacity

    def transform(self, base_scale, bounce=True, floating=True, rotation=False, phase=0.0):
        t = time.perf_counter() + phase
        scale = float(base_scale)
        y = 0.0
        angle = 0.0
        if bounce:
            scale *= 1.0 + 0.035 * math.sin(t * 7.0)
        if floating:
            y = math.sin(t * 2.8) * 0.035
        if rotation:
            angle = math.sin(t * 2.0) * 4.0
        return scale, y, angle

class AnimationBank:
    def __init__(self, default_fade_speed=4.5):
        self.default_fade_speed = float(default_fade_speed)
        self.states = {}

    def opacity(self, key, visible=True, fade_speed=None):
        if key not in self.states:
            self.states[key] = AnimationState(self.default_fade_speed)
        return self.states[key].update(visible, fade_speed)

    def transform(self, key, base_scale, animation=None):
        animation = animation or {}
        if key not in self.states:
            self.states[key] = AnimationState(self.default_fade_speed)
        phase = (sum(ord(c) for c in str(key)) % 100) / 37.0
        return self.states[key].transform(
            base_scale,
            animation.get("bounce", False),
            animation.get("floating", False),
            animation.get("rotation", False),
            phase
        )
