from config import asset_path

class CharacterManager:
    def __init__(self, loader, player, overlay):
        self.loader = loader
        self.player = player
        self.overlay = overlay

    def get_asset(self, spec, emoji_size, channel=None):
        if not spec:
            return None
        kind = str(spec.get("type", "emoji")).lower()
        value = spec.get("value", "")
        if kind == "emoji":
            return self.overlay.emoji_image(value, emoji_size)
        path = asset_path(value)
        if kind in ("image", "png", "jpg", "jpeg", "webp", "sticker"):
            image = self.loader.load_image(path)
            if image is None and spec.get("fallback_emoji"):
                return self.overlay.emoji_image(spec["fallback_emoji"], emoji_size)
            return image
        if kind == "gif":
            data = self.loader.load_gif(path)
            if data is None and spec.get("fallback_emoji"):
                return self.overlay.emoji_image(spec["fallback_emoji"], emoji_size)
            return self.player.frame(str(channel or path), data)
        return self.overlay.emoji_image(spec.get("fallback_emoji", "✨"), emoji_size)
