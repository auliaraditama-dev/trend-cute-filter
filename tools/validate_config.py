import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.json"

VALID_TYPES = {"emoji", "image", "png", "jpg", "jpeg", "webp", "sticker", "gif"}
VALID_FACE_ANCHORS = {
    "face_center", "head", "head_top", "head_left", "head_right", "forehead", "forehead_left", "forehead_right",
    "left_eye", "right_eye", "left_pupil", "right_pupil", "left_brow", "right_brow", "between_eyes",
    "left_cheek", "right_cheek", "left_cheek_inner", "right_cheek_inner", "nose", "nose_bridge",
    "mouth", "upper_lip", "lower_lip", "chin"
}
VALID_HAND_ANCHORS = {"palm", "wrist", "thumb_tip", "index_tip", "middle_tip", "ring_tip", "pinky_tip"}
VALID_TRIGGERS = {"hand_near_face", "gesture_near_face", "gesture_near_anchor", "fingertip_near_anchor", "face_expression", "gesture", "head_pose"}


def check_asset(spec, errors, label="asset"):
    kind = str(spec.get("type", "emoji")).lower()
    if kind not in VALID_TYPES:
        errors.append(f"{label} unknown type: {kind}")
    if kind != "emoji":
        value = spec.get("value")
        if not value:
            errors.append(f"{label} value is empty")
        else:
            path = Path(value)
            if not path.is_absolute():
                path = ROOT / path
            if not path.exists() and not spec.get("fallback_emoji"):
                errors.append(f"{label} missing asset without fallback: {value}")


def check_effect(spec, errors, label):
    check_asset(spec, errors, label)
    target = spec.get("target", "face")
    anchor = spec.get("anchor", "face_center" if target == "face" else "palm")
    if target == "face" and anchor not in VALID_FACE_ANCHORS:
        errors.append(f"{label} invalid face anchor: {anchor}")
    if target == "hand" and anchor not in VALID_HAND_ANCHORS:
        errors.append(f"{label} invalid hand anchor: {anchor}")


def main():
    errors = []
    warnings = []
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"INVALID JSON: {e}")
        raise SystemExit(1)

    for key, spec in data.get("gestures", {}).items():
        check_asset(spec, errors, f"gestures[{key}]")
        try:
            count = int(key)
            if count < 0 or count > 5:
                warnings.append(f"Gesture key outside 0-5: {key}")
        except ValueError:
            warnings.append(f"Gesture key is not numeric: {key}")

    for i, spec in enumerate(data.get("face_overlays", [])):
        check_effect(spec, errors, f"face_overlays[{i}]")

    presets = data.get("face_presets", {})
    items = presets.get("items", {})
    active = presets.get("active")
    order = presets.get("order", [])
    if active and active not in items:
        errors.append(f"face_presets active preset not found: {active}")
    for key in order:
        if key not in items:
            errors.append(f"face_presets order references missing preset: {key}")
    for preset_id, preset in items.items():
        for i, spec in enumerate(preset.get("layers", [])):
            check_effect(spec, errors, f"face_presets.{preset_id}.layers[{i}]")

    for i, rule in enumerate(data.get("interactions", [])):
        trigger = rule.get("trigger", {})
        kind = trigger.get("type", "gesture_near_face")
        if kind not in VALID_TRIGGERS:
            errors.append(f"interactions[{i}] invalid trigger: {kind}")
        face_anchor = trigger.get("face_anchor")
        hand_anchor = trigger.get("hand_anchor")
        if face_anchor and face_anchor not in VALID_FACE_ANCHORS:
            errors.append(f"interactions[{i}] invalid face anchor: {face_anchor}")
        if hand_anchor and hand_anchor not in VALID_HAND_ANCHORS:
            errors.append(f"interactions[{i}] invalid hand anchor: {hand_anchor}")
        check_effect(rule.get("effect", {}), errors, f"interactions[{i}].effect")

    for item in warnings:
        print(f"WARNING: {item}")
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        raise SystemExit(1)
    print("CONFIG VALID")
    print(f"Gesture filters: {len(data.get('gestures', {}))}")
    print(f"Face presets: {len(items)}")
    print(f"Legacy face overlays: {len(data.get('face_overlays', []))}")
    print(f"Interactions: {len(data.get('interactions', []))}")

if __name__ == "__main__":
    main()
