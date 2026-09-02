from pathlib import Path
import json
import time

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def asset_path(value):
    p = Path(value)
    if p.is_absolute():
        return p
    return ROOT / p

class ConfigWatcher:
    def __init__(self, path=CONFIG_PATH, interval=0.7):
        self.path = Path(path)
        self.interval = float(interval)
        self.last_check = 0.0
        self.last_mtime = self.path.stat().st_mtime if self.path.exists() else 0.0

    def changed(self):
        now = time.perf_counter()
        if now - self.last_check < self.interval:
            return False
        self.last_check = now
        if not self.path.exists():
            return False
        mtime = self.path.stat().st_mtime
        if mtime != self.last_mtime:
            self.last_mtime = mtime
            return True
        return False
