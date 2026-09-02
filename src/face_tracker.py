import cv2
import math
import numpy as np
import mediapipe as mp

class FaceTracker:
    def __init__(self, config):
        self.config = config
        self.mp_face = mp.solutions.face_mesh
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.mesh = self.mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=int(config.get("max_faces", 2)),
            refine_landmarks=bool(config.get("refine_landmarks", True)),
            min_detection_confidence=float(config.get("detection_confidence", 0.6)),
            min_tracking_confidence=float(config.get("tracking_confidence", 0.6))
        )
        self.draw_enabled = bool(config.get("draw_landmarks", False))
        self.smoothing = float(config.get("smoothing", 0.68))
        self.previous = {}

    def _avg(self, points, indices):
        xs = [points[i][0] for i in indices if i < len(points)]
        ys = [points[i][1] for i in indices if i < len(points)]
        if not xs:
            return (0.0, 0.0)
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def _dist(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _smooth_point(self, old, new):
        if old is None:
            return new
        s = max(0.0, min(0.95, self.smoothing))
        return (old[0] * s + new[0] * (1.0 - s), old[1] * s + new[1] * (1.0 - s))

    def _smooth_value(self, old, new):
        if old is None:
            return new
        s = max(0.0, min(0.95, self.smoothing))
        return old * s + new * (1.0 - s)

    def _head_pose(self, points, width, height):
        image_points = np.array([
            points[1][:2],
            points[152][:2],
            points[33][:2],
            points[263][:2],
            points[61][:2],
            points[291][:2]
        ], dtype=np.float64)
        model_points = np.array([
            (0.0, 0.0, 0.0),
            (0.0, -63.6, -12.5),
            (-43.3, 32.7, -26.0),
            (43.3, 32.7, -26.0),
            (-28.9, -28.9, -24.1),
            (28.9, -28.9, -24.1)
        ], dtype=np.float64)
        focal = float(width)
        camera_matrix = np.array([[focal, 0, width / 2.0], [0, focal, height / 2.0], [0, 0, 1]], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)
        try:
            ok, rotation_vector, translation_vector = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
            if not ok:
                return 0.0, 0.0, 0.0
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)
            pitch, yaw, roll = [float(v) for v in angles]
            return yaw, pitch, roll
        except Exception:
            return 0.0, 0.0, 0.0

    def _build_face(self, points, frame_width, frame_height):
        left_eye = self._avg(points, [33, 133, 159, 145])
        right_eye = self._avg(points, [362, 263, 386, 374])
        left_pupil = self._avg(points, [468, 469, 470, 471, 472]) if len(points) > 472 else left_eye
        right_pupil = self._avg(points, [473, 474, 475, 476, 477]) if len(points) > 477 else right_eye
        between_eyes = self._avg(points, [168, 6])
        forehead = points[10][:2]
        forehead_left = self._avg(points, [70, 63, 105])
        forehead_right = self._avg(points, [300, 293, 334])
        chin = points[152][:2]
        nose = points[1][:2]
        nose_bridge = self._avg(points, [6, 168, 197])
        mouth = self._avg(points, [13, 14, 61, 291])
        upper_lip = self._avg(points, [13, 0, 37, 267])
        lower_lip = self._avg(points, [14, 17, 84, 314])
        left_cheek = self._avg(points, [234, 93, 132])
        right_cheek = self._avg(points, [454, 323, 361])
        left_cheek_inner = self._avg(points, [50, 101, 205])
        right_cheek_inner = self._avg(points, [280, 330, 425])
        left_temple = points[127][:2]
        right_temple = points[356][:2]
        left_brow = self._avg(points, [70, 63, 105, 66, 107])
        right_brow = self._avg(points, [300, 293, 334, 296, 336])
        xs = [p[0] for p in points[:468]]
        ys = [p[1] for p in points[:468]]
        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)
        center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
        face_width = max(self._dist(left_temple, right_temple), x2 - x1, 1.0)
        face_height = max(self._dist(forehead, chin), y2 - y1, 1.0)
        visual_roll = math.degrees(math.atan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]))
        yaw, pitch, pose_roll = self._head_pose(points, frame_width, frame_height)
        roll = visual_roll if abs(visual_roll) <= 45.0 else pose_roll
        head_top = (forehead[0], forehead[1] - face_height * 0.22)
        head_left = (forehead_left[0] - face_width * 0.05, forehead_left[1] - face_height * 0.16)
        head_right = (forehead_right[0] + face_width * 0.05, forehead_right[1] - face_height * 0.16)
        mouth_ratio = self._dist(points[13], points[14]) / max(self._dist(points[61], points[291]), 1.0)
        left_eye_ratio = self._dist(points[159], points[145]) / max(self._dist(points[33], points[133]), 1.0)
        right_eye_ratio = self._dist(points[386], points[374]) / max(self._dist(points[362], points[263]), 1.0)
        mouth_width_ratio = self._dist(points[61], points[291]) / face_width
        expressions = {
            "mouth_open": mouth_ratio > float(self.config.get("mouth_open_threshold", 0.075)),
            "left_blink": left_eye_ratio < float(self.config.get("blink_threshold", 0.17)),
            "right_blink": right_eye_ratio < float(self.config.get("blink_threshold", 0.17)),
            "blink": left_eye_ratio < float(self.config.get("blink_threshold", 0.17)) and right_eye_ratio < float(self.config.get("blink_threshold", 0.17)),
            "smile": mouth_width_ratio > float(self.config.get("smile_threshold", 0.37)),
            "tilt_left": roll < -float(self.config.get("tilt_threshold", 12.0)),
            "tilt_right": roll > float(self.config.get("tilt_threshold", 12.0))
        }
        anchors = {
            "face_center": center,
            "head": center,
            "head_top": head_top,
            "head_left": head_left,
            "head_right": head_right,
            "forehead": forehead,
            "forehead_left": forehead_left,
            "forehead_right": forehead_right,
            "left_eye": left_eye,
            "right_eye": right_eye,
            "left_pupil": left_pupil,
            "right_pupil": right_pupil,
            "left_brow": left_brow,
            "right_brow": right_brow,
            "between_eyes": between_eyes,
            "left_cheek": left_cheek,
            "right_cheek": right_cheek,
            "left_cheek_inner": left_cheek_inner,
            "right_cheek_inner": right_cheek_inner,
            "nose": nose,
            "nose_bridge": nose_bridge,
            "mouth": mouth,
            "upper_lip": upper_lip,
            "lower_lip": lower_lip,
            "chin": chin
        }
        return {
            "landmarks": points,
            "anchors": anchors,
            "bbox": (x1, y1, x2, y2),
            "face_width": face_width,
            "face_height": face_height,
            "roll": roll,
            "yaw": yaw,
            "pitch": pitch,
            "expressions": expressions,
            "metrics": {
                "mouth_ratio": mouth_ratio,
                "mouth_width_ratio": mouth_width_ratio,
                "left_eye_ratio": left_eye_ratio,
                "right_eye_ratio": right_eye_ratio
            }
        }

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.mesh.process(rgb)
        faces = []
        if result.multi_face_landmarks:
            h, w = frame.shape[:2]
            raw_faces = []
            for raw in result.multi_face_landmarks:
                points = [(float(p.x * w), float(p.y * h), float(p.z)) for p in raw.landmark]
                face = self._build_face(points, w, h)
                face["raw"] = raw
                raw_faces.append(face)
            raw_faces.sort(key=lambda f: f["anchors"]["face_center"][0])
            for index, face in enumerate(raw_faces):
                prev = self.previous.get(index)
                if prev:
                    for name, point in list(face["anchors"].items()):
                        face["anchors"][name] = self._smooth_point(prev["anchors"].get(name), point)
                    for name in ("face_width", "face_height", "roll", "yaw", "pitch"):
                        face[name] = self._smooth_value(prev.get(name), face[name])
                face["index"] = index
                faces.append(face)
                if self.draw_enabled:
                    self.mp_draw.draw_landmarks(
                        image=frame,
                        landmark_list=face["raw"],
                        connections=self.mp_face.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_styles.get_default_face_mesh_contours_style()
                    )
            self.previous = {f["index"]: f for f in faces}
        else:
            self.previous = {}
        return faces

    def toggle_draw(self):
        self.draw_enabled = not self.draw_enabled
        return self.draw_enabled

    def close(self):
        self.mesh.close()
