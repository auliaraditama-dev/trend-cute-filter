import time

class GestureDetector:
    def __init__(self, stability_seconds=0.25, lost_timeout=0.35):
        self.stability_seconds = float(stability_seconds)
        self.lost_timeout = float(lost_timeout)
        self.pending = None
        self.pending_since = time.perf_counter()
        self.active = None
        self.last_seen = time.perf_counter()

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

    def update(self, hands):
        now = time.perf_counter()
        if not hands:
            if now - self.last_seen >= self.lost_timeout:
                self.active = None
                self.pending = None
            return self.active

        self.last_seen = now
        current = self.count_fingers(hands[0])

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
