from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageSequence

class AssetLoader:
    def __init__(self):
        self.image_cache = {}
        self.gif_cache = {}

    def load_image(self, path):
        path = str(Path(path))
        if path in self.image_cache:
            return self.image_cache[path]
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if image is None:
            return None
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
        elif image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        self.image_cache[path] = image
        return image

    def load_gif(self, path):
        path = str(Path(path))
        if path in self.gif_cache:
            return self.gif_cache[path]
        if not Path(path).exists():
            return None
        im = Image.open(path)
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(im):
            rgba = frame.convert("RGBA")
            arr = np.array(rgba)
            bgra = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
            frames.append(bgra)
            durations.append(max(int(frame.info.get("duration", 80)), 20))
        data = {"frames": frames, "durations": durations}
        self.gif_cache[path] = data
        return data

    def clear(self):
        self.image_cache.clear()
        self.gif_cache.clear()
