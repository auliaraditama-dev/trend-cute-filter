import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, config):
        self.config = config
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=int(config.get("max_hands", 2)),
            min_detection_confidence=float(config.get("detection_confidence", 0.65)),
            min_tracking_confidence=float(config.get("tracking_confidence", 0.65)),
            model_complexity=1
        )
        self.draw_enabled = bool(config.get("draw_landmarks", True))

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        output = []
        if result.multi_hand_landmarks:
            h, w = frame.shape[:2]
            handedness = result.multi_handedness or []
            for i, hand in enumerate(result.multi_hand_landmarks):
                label = handedness[i].classification[0].label if i < len(handedness) else "Unknown"
                landmarks = [(int(p.x*w), int(p.y*h), float(p.z)) for p in hand.landmark]
                output.append({
                    "landmarks": landmarks,
                    "raw": hand,
                    "handedness": label
                })
                if self.draw_enabled:
                    self.mp_draw.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)
        return output

    def toggle_draw(self):
        self.draw_enabled = not self.draw_enabled
        return self.draw_enabled

    def close(self):
        self.hands.close()
