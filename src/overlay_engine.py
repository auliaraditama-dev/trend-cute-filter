import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import platform

class OverlayEngine:
    def __init__(self):
        self.font_cache = {}

    def _font_candidates(self):
        if platform.system() == "Windows":
            return [
                "C:/Windows/Fonts/seguiemj.ttf",
                "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arial.ttf"
            ]
        return [
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]

    def emoji_image(self, text, size):
        key = (text, int(size))
        if key in self.font_cache:
            return self.font_cache[key].copy()
        font = None
        for candidate in self._font_candidates():
            try:
                font = ImageFont.truetype(candidate, int(size))
                break
            except Exception:
                pass
        if font is None:
            font = ImageFont.load_default()
        canvas = Image.new("RGBA", (int(size*2), int(size*2)), (0,0,0,0))
        draw = ImageDraw.Draw(canvas)
        bbox = draw.textbbox((0,0), text, font=font, embedded_color=True)
        tw = max(1, bbox[2]-bbox[0])
        th = max(1, bbox[3]-bbox[1])
        draw.text(((canvas.width-tw)//2, (canvas.height-th)//2), text, font=font, embedded_color=True)
        arr = np.array(canvas)
        bgra = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
        self.font_cache[key] = bgra
        return bgra.copy()

    def resize_rgba(self, image, target_width):
        if image is None or image.size == 0:
            return None
        h, w = image.shape[:2]
        if w <= 0:
            return None
        scale = float(target_width) / float(w)
        target_height = max(1, int(h * scale))
        return cv2.resize(image, (max(1, int(target_width)), target_height), interpolation=cv2.INTER_AREA)

    def rotate_rgba(self, image, angle):
        if image is None or abs(angle) < 0.01:
            return image
        h, w = image.shape[:2]
        center = (w/2, h/2)
        m = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = abs(m[0,0])
        sin = abs(m[0,1])
        nw = int(h*sin + w*cos)
        nh = int(h*cos + w*sin)
        m[0,2] += nw/2 - center[0]
        m[1,2] += nh/2 - center[1]
        return cv2.warpAffine(image, m, (nw,nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

    def overlay(self, frame, image, center, opacity=1.0):
        if image is None:
            return frame
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        fh, fw = frame.shape[:2]
        ih, iw = image.shape[:2]
        cx, cy = center
        x1 = int(cx - iw/2)
        y1 = int(cy - ih/2)
        x2 = x1 + iw
        y2 = y1 + ih
        sx1 = max(0, -x1)
        sy1 = max(0, -y1)
        sx2 = iw - max(0, x2-fw)
        sy2 = ih - max(0, y2-fh)
        dx1 = max(0, x1)
        dy1 = max(0, y1)
        dx2 = dx1 + max(0, sx2-sx1)
        dy2 = dy1 + max(0, sy2-sy1)
        if sx2 <= sx1 or sy2 <= sy1:
            return frame
        src = image[sy1:sy2, sx1:sx2].astype(np.float32)
        dst = frame[dy1:dy2, dx1:dx2].astype(np.float32)
        alpha = (src[:,:,3:4] / 255.0) * float(max(0.0, min(1.0, opacity)))
        out = src[:,:,:3]*alpha + dst*(1.0-alpha)
        frame[dy1:dy2, dx1:dx2] = out.astype(np.uint8)
        return frame
