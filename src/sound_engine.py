import platform
import threading
from pathlib import Path

class SoundEngine:
    def __init__(self, root):
        self.root = Path(root)
        self.enabled = True
        self.is_windows = platform.system() == "Windows"

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def play(self, value):
        if not self.enabled or not value or not self.is_windows:
            return
        path = Path(value)
        if not path.is_absolute():
            path = self.root / path
        if not path.exists():
            return
        def worker():
            try:
                import winsound
                winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()
