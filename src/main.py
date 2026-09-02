import cv2
import time
from config import load_config, ROOT, ConfigWatcher
from camera import Camera
from hand_tracker import HandTracker
from face_tracker import FaceTracker
from gesture_detector import GestureDetector
from interaction_engine import InteractionEngine
from gif_loader import AssetLoader
from gif_player import GIFPlayer
from overlay_engine import OverlayEngine
from animation import AnimationBank
from particle_system import ParticleSystem
from character_manager import CharacterManager
from face_painter import FacePainter
from preset_manager import PresetManager
from sound_engine import SoundEngine
from effects import Recorder, screenshot
from utils import FPSCounter, put_text


def anchor_for(spec, frame, face=None, hand=None):
    target = spec.get("target", "face")
    anchor_name = spec.get("anchor", "face_center" if target == "face" else "palm")
    if target == "face" and face:
        return face["anchors"].get(anchor_name, face["anchors"]["face_center"]), face["face_width"], face["roll"]
    if target == "hand" and hand:
        return hand.get("anchors", {}).get(anchor_name, hand.get("anchors", {}).get("palm")), hand.get("hand_size", 120.0), 0.0
    return (frame.shape[1] / 2.0, frame.shape[0] / 2.0), frame.shape[1], 0.0


def render_effect(frame, spec, key, manager, overlay, animations, face=None, hand=None, default_fade=4.5):
    anchor, reference, tracked_angle = anchor_for(spec, frame, face, hand)
    if anchor is None:
        return frame, None
    scale = float(spec.get("scale", 0.55))
    anim = spec.get("animation", {})
    animated_scale, float_y, extra_angle = animations.transform(key, scale, anim)
    target_width = max(20, int(reference * animated_scale))
    opacity = animations.opacity(key, True, spec.get("fade_speed", default_fade)) * float(spec.get("opacity", 1.0))
    asset = manager.get_asset(spec, max(42, int(target_width * 0.82)), channel=key)
    if asset is None:
        return frame, None
    asset = overlay.resize_rgba(asset, target_width)
    angle = extra_angle + (tracked_angle if spec.get("follow_rotation", False) else 0.0)
    asset = overlay.rotate_rgba(asset, angle)
    ox = float(spec.get("offset_x", 0.0)) * reference
    oy = float(spec.get("offset_y", 0.0)) * reference + float_y * reference
    center = (int(anchor[0] + ox), int(anchor[1] + oy))
    frame = overlay.overlay(frame, asset, center, opacity)
    return frame, center


def emit_for_spec(particles, enabled, last_particle, key, center, spec):
    if not enabled or center is None:
        return
    particle = spec.get("particle", "none")
    if particle == "none":
        return
    now = time.perf_counter()
    interval = float(spec.get("particle_interval", 0.09))
    if now - last_particle.get(key, 0.0) >= interval:
        particles.emit(center[0], center[1], particle, int(spec.get("particle_count", 2)))
        last_particle[key] = now


def main():
    config = load_config()
    camera = Camera(config["camera"]).open()
    hand_tracker = HandTracker(config["hand_tracking"])
    face_tracker = FaceTracker(config["face_tracking"])
    detector = GestureDetector(
        config["gesture"].get("stability_seconds", 0.25),
        config["gesture"].get("lost_hand_timeout", 0.35)
    )
    interactions = InteractionEngine()
    loader = AssetLoader()
    player = GIFPlayer()
    overlay = OverlayEngine()
    manager = CharacterManager(loader, player, overlay)
    animations = AnimationBank(config.get("animation", {}).get("fade_speed", 4.5))
    particles = ParticleSystem(config["particles"].get("max_particles", 120))
    painter = FacePainter()
    presets = PresetManager(config)
    recorder = Recorder(ROOT / "output", config["camera"].get("fps", 30))
    sounds = SoundEngine(ROOT)
    fps_counter = FPSCounter()
    watcher = ConfigWatcher(interval=config.get("runtime", {}).get("reload_interval", 0.7))
    last_particle = {}
    debug = bool(config.get("ui", {}).get("debug", True))
    particles_enabled = bool(config.get("particles", {}).get("enabled", True))
    paint_enabled = True
    hand_filter_enabled = bool(config.get("hand_filter", {}).get("enabled", True))
    interactions_enabled = True
    auto_cycle = False
    auto_cycle_interval = float(config.get("face_presets", {}).get("auto_cycle_interval", 8.0))
    last_auto_cycle = time.perf_counter()
    previous_interaction_keys = set()

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break

            if config.get("runtime", {}).get("auto_reload", True) and watcher.changed():
                config = load_config()
                loader.clear()
                player.reset()
                presets.update(config, preserve=True)
                debug = bool(config.get("ui", {}).get("debug", debug))
                particles_enabled = bool(config.get("particles", {}).get("enabled", particles_enabled))
                auto_cycle_interval = float(config.get("face_presets", {}).get("auto_cycle_interval", auto_cycle_interval))
                print("Config auto reloaded")

            hands = hand_tracker.process(frame)
            hands = detector.enrich(hands)
            faces = face_tracker.process(frame) if config.get("face_tracking", {}).get("enabled", True) else []
            stable_count = detector.update(hands)
            if auto_cycle and time.perf_counter() - last_auto_cycle >= auto_cycle_interval:
                presets.next()
                sounds.play("assets/sounds/switch.wav")
                last_auto_cycle = time.perf_counter()
            preset = presets.current()

            if paint_enabled:
                for face in faces:
                    painter.apply(frame, face, preset.get("paint", {}))

            for face in faces:
                for idx, spec in enumerate(config.get("face_overlays", [])):
                    if not spec.get("enabled", True):
                        continue
                    key = f"legacy_face:{face['index']}:{spec.get('id', idx)}"
                    frame, center = render_effect(frame, spec, key, manager, overlay, animations, face=face)
                    emit_for_spec(particles, particles_enabled, last_particle, key, center, spec)

                for idx, spec in enumerate(preset.get("layers", [])):
                    if not spec.get("enabled", True):
                        continue
                    key = f"preset:{presets.active}:{face['index']}:{spec.get('id', idx)}"
                    frame, center = render_effect(frame, spec, key, manager, overlay, animations, face=face)
                    emit_for_spec(particles, particles_enabled, last_particle, key, center, spec)

            hand_filter = config.get("hand_filter", {})
            gesture_spec = config.get("gestures", {}).get(str(stable_count)) if stable_count is not None else None
            if hand_filter_enabled and hand_filter.get("enabled", True) and hands and gesture_spec:
                merged = dict(gesture_spec)
                merged.setdefault("target", "hand")
                merged.setdefault("anchor", hand_filter.get("anchor", "palm"))
                merged.setdefault("scale", hand_filter.get("scale", 1.55))
                merged.setdefault("offset_x", hand_filter.get("offset_x", 0.0))
                merged.setdefault("offset_y", hand_filter.get("offset_y", -0.8))
                merged.setdefault("animation", hand_filter.get("animation", {"bounce": True, "floating": True}))
                key = f"hand_filter:{stable_count}"
                frame, center = render_effect(frame, merged, key, manager, overlay, animations, hand=hands[0])
                emit_for_spec(particles, particles_enabled, last_particle, key, center, merged)

            active_interactions = interactions.evaluate(config.get("interactions", []), faces, hands) if interactions_enabled else []
            active_interaction_keys = {key for key, _ in active_interactions}
            for new_key in active_interaction_keys - previous_interaction_keys:
                for rule in config.get("interactions", []):
                    if str(rule.get("id", "")) == str(new_key):
                        sounds.play(rule.get("sound", "assets/sounds/pop.wav"))
                        break
            previous_interaction_keys = active_interaction_keys
            for key, context in active_interactions:
                rule = context["rule"]
                spec = rule.get("effect", {})
                render_key = f"interaction:{key}"
                frame, center = render_effect(
                    frame,
                    spec,
                    render_key,
                    manager,
                    overlay,
                    animations,
                    face=context.get("face"),
                    hand=context.get("hand")
                )
                emit_for_spec(particles, particles_enabled, last_particle, render_key, center, spec)

            if particles_enabled:
                particles.update_draw(frame)

            fps = fps_counter.update()
            if debug:
                gesture_name = hands[0].get("gesture", "None") if hands else "None"
                count_label = "None" if stable_count is None else str(stable_count)
                put_text(frame, f"Preset: {presets.name()} [{presets.active or '-'}]", (18, 30))
                put_text(frame, f"Faces: {len(faces)} | Hands: {len(hands)} | Gesture: {gesture_name} | Fingers: {count_label}", (18, 58), 0.55, 1)
                put_text(frame, f"Interactions: {len(active_interactions)} | FPS: {fps:.1f} | REC: {'ON' if recorder.active else 'OFF'} | Auto: {'ON' if auto_cycle else 'OFF'}", (18, 86), 0.55, 1)
                if faces:
                    face = faces[0]
                    expr = [k for k, v in face.get("expressions", {}).items() if v]
                    put_text(frame, f"Face: {', '.join(expr) if expr else 'None'} | Yaw {face.get('yaw',0):.1f} Pitch {face.get('pitch',0):.1f} Roll {face.get('roll',0):.1f}", (18, 114), 0.5, 1)
                put_text(frame, "1-9 Preset | N/B Next/Prev | A Auto | H HandFX | I Interact | M Sound | Q Quit | S Shot | R Record | C Reload | L/F Mesh | D Debug | P Particles | V Paint", (18, frame.shape[0] - 18), 0.40, 1)

            recorder.write(frame)
            cv2.imshow("Trend Cute Filter - Face + Hand Studio", frame)
            key = cv2.waitKey(1) & 0xFF
            controls = config.get("controls", {})

            if key == ord(controls.get("quit", "q")):
                break
            if ord("1") <= key <= ord("9"):
                if presets.select_index(key - ord("1")):
                    sounds.play("assets/sounds/switch.wav")
                    last_auto_cycle = time.perf_counter()
                    print(f"Preset: {presets.name()}")
            if key == ord(controls.get("next_preset", "n")):
                presets.next()
                sounds.play("assets/sounds/switch.wav")
                last_auto_cycle = time.perf_counter()
                print(f"Preset: {presets.name()}")
            if key == ord(controls.get("previous_preset", "b")):
                presets.previous()
                sounds.play("assets/sounds/switch.wav")
                last_auto_cycle = time.perf_counter()
                print(f"Preset: {presets.name()}")
            if key == ord(controls.get("screenshot", "s")):
                path = screenshot(frame, ROOT / "output")
                print(f"Screenshot: {path}")
            if key == ord(controls.get("record", "r")):
                active, path = recorder.toggle(frame)
                print(f"Recording {'started' if active else 'saved'}: {path}")
            if key == ord(controls.get("hand_landmarks", "l")):
                print(f"Hand landmarks: {hand_tracker.toggle_draw()}")
            if key == ord(controls.get("face_landmarks", "f")):
                print(f"Face landmarks: {face_tracker.toggle_draw()}")
            if key == ord(controls.get("debug", "d")):
                debug = not debug
            if key == ord(controls.get("particles", "p")):
                particles_enabled = not particles_enabled
            if key == ord(controls.get("paint", "v")):
                paint_enabled = not paint_enabled
            if key == ord(controls.get("auto_cycle", "a")):
                auto_cycle = not auto_cycle
                last_auto_cycle = time.perf_counter()
            if key == ord(controls.get("hand_filter", "h")):
                hand_filter_enabled = not hand_filter_enabled
            if key == ord(controls.get("interactions", "i")):
                interactions_enabled = not interactions_enabled
                previous_interaction_keys = set()
            if key == ord(controls.get("sound", "m")):
                print(f"Sound: {sounds.toggle()}")
            if key == ord(controls.get("reload", "c")):
                config = load_config()
                loader.clear()
                player.reset()
                presets.update(config, preserve=True)
                print("Config reloaded")

    finally:
        recorder.close()
        hand_tracker.close()
        face_tracker.close()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
