import time

class GIFPlayer:
    def __init__(self):
        self.key = None
        self.index = 0
        self.last = time.perf_counter()

    def reset(self, key=None):
        self.key = key
        self.index = 0
        self.last = time.perf_counter()

    def frame(self, key, data):
        if not data or not data.get("frames"):
            return None
        now = time.perf_counter()
        if self.key != key:
            self.reset(key)
        duration = data["durations"][self.index] / 1000.0
        if now - self.last >= duration:
            self.index = (self.index + 1) % len(data["frames"])
            self.last = now
        return data["frames"][self.index]
