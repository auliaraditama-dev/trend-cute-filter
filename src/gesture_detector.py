import math
import time

class GestureDetector:
    def __init__(self, stability_seconds=0.25, lost_timeout=0.35):
        self.stability_seconds = float(stability_seconds)
        self.lost_timeout = float(lost_timeout)
        self.pending = None
        self.pending_since = time.perf_counter()
        self.active = None
        self.last_seen = time.perf_counter()

    def _dist(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def finger_states(self, hand):
        lm = hand["landmarks"]
        handed = hand["handedness"]
        thumb = lm[4][0] < lm[3][0] if handed == "Right" else lm[4][0] > lm[3][0]
        index = lm[8][1] < lm[6][1]
        middle = lm[12][1] < lm[10][1]
        ring = lm[16][1] < lm[14][1]
        pinky = lm[20][1] < lm[18][1]
        return [thumb, index, middle, ring, pinky]

    def count_fingers(self, hand):
        return sum(self.finger_states(hand))

    def named_gesture(self, hand):
        lm = hand["landmarks"]
        states = self.finger_states(hand)
        palm_width = max(self._dist(lm[5], lm[17]), 1.0)
        pinch_ratio = self._dist(lm[4], lm[8]) / palm_width
        if pinch_ratio < 0.28:
            return "pinch"
        patterns = {
            (False, False, False, False, False): "fist",
            (False, True, False, False, False): "point",
            (False, True, True, False, False): "peace",
            (False, True, True, True, False): "three",
            (False, True, True, True, True): "four",
            (True, True, True, True, True): "open_palm",
            (True, False, False, False, False): "thumb"
        }
        return patterns.get(tuple(states), f"fingers_{sum(states)}")

    def enrich(self, hands):
        for hand in hands:
            lm = hand["landmarks"]
            hand["finger_states"] = self.finger_states(hand)
            hand["finger_count"] = sum(hand["finger_states"])
            hand["gesture"] = self.named_gesture(hand)
            hand["anchors"] = {
                "wrist": (lm[0][0], lm[0][1]),
                "thumb_tip": (lm[4][0], lm[4][1]),
                "index_tip": (lm[8][0], lm[8][1]),
                "middle_tip": (lm[12][0], lm[12][1]),
                "ring_tip": (lm[16][0], lm[16][1]),
                "pinky_tip": (lm[20][0], lm[20][1]),
                "palm": self.anchor(hand)
            }
            hand["hand_size"] = max(self._dist(lm[5], lm[17]) * 2.2, 50.0)
        return hands

    def update(self, hands):
        now = time.perf_counter()
        if not hands:
            if now - self.last_seen >= self.lost_timeout:
                self.active = None
                self.pending = None
            return self.active
        self.last_seen = now
        current = hands[0].get("finger_count", self.count_fingers(hands[0]))
        if current != self.pending:
            self.pending = current
            self.pending_since = now
        if current != self.active and now - self.pending_since >= self.stability_seconds:
            self.active = current
        return self.active

    def anchor(self, hand):
        lm = hand["landmarks"]
        x = int((lm[0][0] + lm[5][0] + lm[9][0] + lm[13][0] + lm[17][0]) / 5)
        y = int((lm[0][1] + lm[5][1] + lm[9][1] + lm[13][1] + lm[17][1]) / 5)
        return x, y
