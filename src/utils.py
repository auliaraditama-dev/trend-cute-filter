import cv2
import time
from pathlib import Path

class FPSCounter:
    def __init__(self):
        self.last = time.perf_counter()
        self.fps = 0.0
        self.smooth = 0.9

    def update(self):
        now = time.perf_counter()
        dt = max(now - self.last, 1e-6)
        current = 1.0 / dt
        self.fps = self.fps * self.smooth + current * (1.0 - self.smooth)
        self.last = now
        return self.fps

def put_text(frame, text, pos, scale=0.65, thickness=2):
    cv2.putText(frame, str(text), pos, cv2.FONT_HERSHEY_SIMPLEX, scale, (255,255,255), thickness, cv2.LINE_AA)
    cv2.putText(frame, str(text), pos, cv2.FONT_HERSHEY_SIMPLEX, scale, (0,0,0), max(1, thickness-1), cv2.LINE_AA)

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
