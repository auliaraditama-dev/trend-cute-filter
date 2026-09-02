import math
import time

class InteractionEngine:
    def __init__(self):
        self.last_active = {}
        self.last_context = {}

    def _dist(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _gesture_match(self, hand, trigger):
        gestures = trigger.get("gestures", [])
        counts = trigger.get("finger_counts", [])
        if gestures and hand.get("gesture") not in gestures:
            return False
        if counts and hand.get("finger_count") not in counts:
            return False
        return True

    def _best_near(self, faces, hands, trigger, anchor_name="face_center"):
        best = None
        limit = float(trigger.get("distance", 0.85))
        hand_anchor = trigger.get("hand_anchor", "palm")
        for face in faces:
            target = face["anchors"].get(anchor_name, face["anchors"]["face_center"])
            ref = max(face["face_width"], 1.0)
            for hand in hands:
                if not self._gesture_match(hand, trigger):
                    continue
                hp = hand.get("anchors", {}).get(hand_anchor, hand.get("anchors", {}).get("palm"))
                if hp is None:
                    continue
                d = self._dist(hp, target) / ref
                if d <= limit and (best is None or d < best[0]):
                    best = (d, face, hand)
        return best

    def _pose_match(self, face, trigger):
        axis = trigger.get("axis", "roll")
        value = float(face.get(axis, 0.0))
        minimum = trigger.get("min")
        maximum = trigger.get("max")
        if minimum is not None and value < float(minimum):
            return False
        if maximum is not None and value > float(maximum):
            return False
        return True

    def _match(self, rule, faces, hands):
        trigger = rule.get("trigger", {})
        kind = trigger.get("type", "gesture_near_face")
        if kind in ("hand_near_face", "gesture_near_face"):
            return self._best_near(faces, hands, trigger, "face_center")
        if kind == "gesture_near_anchor":
            return self._best_near(faces, hands, trigger, trigger.get("face_anchor", "right_cheek"))
        if kind == "fingertip_near_anchor":
            local = dict(trigger)
            local["hand_anchor"] = trigger.get("hand_anchor", "index_tip")
            return self._best_near(faces, hands, local, trigger.get("face_anchor", "nose"))
        if kind == "face_expression":
            expression = trigger.get("expression", "mouth_open")
            for face in faces:
                if face.get("expressions", {}).get(expression):
                    return (0.0, face, None)
        if kind == "head_pose":
            for face in faces:
                if self._pose_match(face, trigger):
                    return (0.0, face, None)
        if kind == "gesture":
            for hand in hands:
                if self._gesture_match(hand, trigger):
                    return (0.0, None, hand)
        return None

    def evaluate(self, rules, faces, hands):
        now = time.perf_counter()
        active = []
        for index, rule in enumerate(rules):
            if not rule.get("enabled", True):
                continue
            key = str(rule.get("id", f"interaction_{index}"))
            match = self._match(rule, faces, hands)
            hold = float(rule.get("trigger", {}).get("hold_seconds", 0.25))
            if match:
                _, face, hand = match
                context = {"face": face, "hand": hand, "rule": rule}
                self.last_active[key] = now
                self.last_context[key] = context
                active.append((key, context))
            elif key in self.last_active and now - self.last_active[key] <= hold:
                context = self.last_context.get(key)
                if context:
                    active.append((key, context))
            else:
                self.last_active.pop(key, None)
                self.last_context.pop(key, None)
        return active
