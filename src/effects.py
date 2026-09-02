import cv2
import time
from pathlib import Path

class Recorder:
    def __init__(self, output_dir, fps=30):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fps = int(fps)
        self.writer = None
        self.path = None

    @property
    def active(self):
        return self.writer is not None

    def toggle(self, frame):
        if self.writer is not None:
            self.writer.release()
            self.writer = None
            old = self.path
            self.path = None
            return False, old
        h, w = frame.shape[:2]
        name = time.strftime("video_%Y%m%d_%H%M%S.mp4")
        self.path = self.output_dir / name
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(str(self.path), fourcc, self.fps, (w,h))
        return True, self.path

    def write(self, frame):
        if self.writer is not None:
            self.writer.write(frame)

    def close(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None

def screenshot(frame, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / time.strftime("shot_%Y%m%d_%H%M%S.png")
    cv2.imwrite(str(path), frame)
    return path
