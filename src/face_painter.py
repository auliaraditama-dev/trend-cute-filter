import cv2
import numpy as np
import math

class FacePainter:
    def __init__(self):
        pass

    def _blend(self, frame, layer, alpha):
        alpha = np.clip(alpha, 0.0, 1.0).astype(np.float32)
        if alpha.ndim == 2:
            alpha = alpha[:, :, None]
        frame[:] = (layer.astype(np.float32) * alpha + frame.astype(np.float32) * (1.0 - alpha)).astype(np.uint8)
        return frame

    def _soft_glow(self, frame, face, amount):
        amount = float(max(0.0, min(0.55, amount)))
        if amount <= 0.0:
            return frame
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = face["bbox"]
        pad = int(face["face_width"] * 0.08)
        rx1 = max(0, int(x1) - pad)
        ry1 = max(0, int(y1) - pad)
        rx2 = min(w, int(x2) + pad)
        ry2 = min(h, int(y2) + pad)
        if rx2 <= rx1 or ry2 <= ry1:
            return frame
        roi = frame[ry1:ry2, rx1:rx2]
        points = np.array([[int(p[0]) - rx1, int(p[1]) - ry1] for p in face["landmarks"][:468]], dtype=np.int32)
        hull = cv2.convexHull(points)
        mask = np.zeros(roi.shape[:2], dtype=np.uint8)
        cv2.fillConvexPoly(mask, hull, 255)
        mask = cv2.GaussianBlur(mask, (0, 0), max(2.0, face["face_width"] * 0.02))
        filtered = cv2.bilateralFilter(roi, 7, 28, 28)
        alpha = (mask.astype(np.float32) / 255.0) * amount
        roi[:] = (filtered.astype(np.float32) * alpha[:, :, None] + roi.astype(np.float32) * (1.0 - alpha[:, :, None])).astype(np.uint8)
        return frame

    def _ellipse_layer(self, frame, center, axes, angle, color, alpha, blur):
        layer = frame.copy()
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.ellipse(mask, (int(center[0]), int(center[1])), (max(1, int(axes[0])), max(1, int(axes[1]))), float(angle), 0, 360, 255, -1, cv2.LINE_AA)
        if blur > 0:
            mask = cv2.GaussianBlur(mask, (0, 0), float(blur))
        layer[:] = color
        a = (mask.astype(np.float32) / 255.0) * float(alpha)
        return self._blend(frame, layer, a)

    def _blush(self, frame, face, spec):
        color = tuple(int(v) for v in spec.get("color_bgr", [150, 145, 255]))
        alpha = float(spec.get("alpha", 0.22))
        width = face["face_width"] * float(spec.get("width", 0.17))
        height = face["face_width"] * float(spec.get("height", 0.07))
        blur = max(3.0, face["face_width"] * float(spec.get("blur", 0.028)))
        for name in ("left_cheek", "right_cheek"):
            center = face["anchors"].get(name)
            if center:
                self._ellipse_layer(frame, center, (width, height), face["roll"], color, alpha, blur)
        return frame

    def _nose_blush(self, frame, face, spec):
        color = tuple(int(v) for v in spec.get("color_bgr", [145, 145, 255]))
        alpha = float(spec.get("alpha", 0.14))
        size = face["face_width"] * float(spec.get("size", 0.055))
        center = face["anchors"].get("nose")
        if center:
            self._ellipse_layer(frame, center, (size, size * 0.7), face["roll"], color, alpha, max(2.0, size * 0.45))
        return frame

    def _freckles(self, frame, face, spec):
        count = int(spec.get("count", 9))
        color = tuple(int(v) for v in spec.get("color_bgr", [100, 120, 175]))
        radius = max(1, int(face["face_width"] * float(spec.get("radius", 0.005))))
        alpha = float(spec.get("alpha", 0.38))
        layer = frame.copy()
        left = face["anchors"].get("left_cheek")
        right = face["anchors"].get("right_cheek")
        if not left or not right:
            return frame
        points = []
        side_count = max(1, count // 2)
        for i in range(side_count):
            t = (i - (side_count - 1) / 2.0) / max(1.0, side_count - 1)
            points.append((left[0] + t * face["face_width"] * 0.12, left[1] - abs(t) * face["face_width"] * 0.025))
            points.append((right[0] + t * face["face_width"] * 0.12, right[1] - abs(t) * face["face_width"] * 0.025))
        for p in points[:count]:
            cv2.circle(layer, (int(p[0]), int(p[1])), radius, color, -1, cv2.LINE_AA)
        return cv2.addWeighted(layer, alpha, frame, 1.0 - alpha, 0)

    def apply(self, frame, face, spec):
        if not spec or not spec.get("enabled", True):
            return frame
        frame = self._soft_glow(frame, face, spec.get("soft_glow", 0.0))
        if spec.get("blush", {}).get("enabled", False):
            frame = self._blush(frame, face, spec["blush"])
        if spec.get("nose_blush", {}).get("enabled", False):
            frame = self._nose_blush(frame, face, spec["nose_blush"])
        if spec.get("freckles", {}).get("enabled", False):
            frame = self._freckles(frame, face, spec["freckles"])
        return frame
