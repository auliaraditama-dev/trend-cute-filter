import time

class GIFPlayer:
    def __init__(self):
        self.states = {}

    def reset(self, key=None):
        if key is None:
            self.states.clear()
        else:
            self.states.pop(key, None)

    def frame(self, key, data):
        if not data or not data.get("frames"):
            return None
        now = time.perf_counter()
        state = self.states.get(key)
        if state is None:
            state = {"index": 0, "last": now}
            self.states[key] = state
        index = state["index"]
        duration = data["durations"][index] / 1000.0
        if now - state["last"] >= duration:
            index = (index + 1) % len(data["frames"])
            state["index"] = index
            state["last"] = now
        return data["frames"][index]
