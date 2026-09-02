class PresetManager:
    def __init__(self, config):
        self.active = None
        self.order = []
        self.items = {}
        self.update(config, preserve=False)

    def update(self, config, preserve=True):
        section = config.get("face_presets", {})
        items = section.get("items", {})
        order = [key for key in section.get("order", []) if key in items]
        if not order:
            order = list(items.keys())
        previous = self.active
        self.items = items
        self.order = order
        configured = section.get("active")
        if preserve and previous in self.items:
            self.active = previous
        elif configured in self.items:
            self.active = configured
        elif self.order:
            self.active = self.order[0]
        else:
            self.active = None

    def current(self):
        return self.items.get(self.active, {})

    def name(self):
        preset = self.current()
        return preset.get("name", self.active or "None")

    def select(self, key):
        if key in self.items:
            self.active = key
            return True
        return False

    def select_index(self, index):
        if 0 <= index < len(self.order):
            self.active = self.order[index]
            return True
        return False

    def next(self):
        if not self.order:
            return None
        if self.active not in self.order:
            self.active = self.order[0]
            return self.active
        index = (self.order.index(self.active) + 1) % len(self.order)
        self.active = self.order[index]
        return self.active

    def previous(self):
        if not self.order:
            return None
        if self.active not in self.order:
            self.active = self.order[0]
            return self.active
        index = (self.order.index(self.active) - 1) % len(self.order)
        self.active = self.order[index]
        return self.active
