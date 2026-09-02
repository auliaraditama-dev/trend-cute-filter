from pathlib import Path
import json

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
