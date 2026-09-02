import cv2
import time
from pathlib import Path
from config import load_config, ROOT
from camera import Camera
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from gif_loader import AssetLoader
from gif_player import GIFPlayer
from overlay_engine import OverlayEngine
from animation import AnimationState
from particle_system import ParticleSystem
from character_manager import CharacterManager
from effects import Recorder, screenshot
from utils import FPSCounter, put_text

def main():
    config = load_config()
    camera = Camera(config["camera"]).open()
    tracker = HandTracker(config["hand_tracking"])
    detector = GestureDetector(
        config["gesture"].get("stability_seconds", 0.25),
        config["gesture"].get("lost_hand_timeout", 0.35)
    )
    loader = AssetLoader()
    player = GIFPlayer()
    overlay = OverlayEngine()
    manager = CharacterManager(loader, player, overlay)
    animation = AnimationState(config["filter"].get("fade_speed", 4.5))
    particles = ParticleSystem(config["particles"].get("max_particles", 60))
    recorder = Recorder(ROOT / "output", config["camera"].get("fps", 30))
    fps_counter = FPSCounter()
    controls = config["controls"]
    last_particle = 0.0
    last_config_reload = 0.0

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break

            hands = tracker.process(frame)
            gesture = detector.update(hands)
            spec = config.get("gestures", {}).get(str(gesture)) if gesture is not None else None
            visible = spec is not None
            opacity = animation.update(visible)

            anchor = (frame.shape[1]//2, frame.shape[0]//2)
            if hands:
                anchor = detector.anchor(hands[0])

            fcfg = config["filter"]
            anchor = (
                int(anchor[0] + fcfg.get("offset_x", 0)),
                int(anchor[1] + fcfg.get("offset_y", -120))
            )

            scale, float_y, angle = animation.transform(
                fcfg.get("scale", 0.32),
                fcfg.get("bounce", True),
                fcfg.get("floating", True),
                fcfg.get("rotation", False)
            )

            if spec and opacity > 0:
                target_width = max(72, int(frame.shape[1] * scale))
                asset = manager.get_asset(spec, max(64, int(target_width*0.75)))
                asset = overlay.resize_rgba(asset, target_width)
                asset = overlay.rotate_rgba(asset, angle)
                frame = overlay.overlay(frame, asset, (anchor[0], anchor[1]+float_y), opacity)

                now = time.perf_counter()
                particle_kind = spec.get("particle", "none")
                if config["particles"].get("enabled", True) and now-last_particle >= 0.07:
                    particles.emit(anchor[0], anchor[1], particle_kind, 2)
                    last_particle = now

            if config["particles"].get("enabled", True):
                particles.update_draw(frame)

            fps = fps_counter.update()
            label = "None" if gesture is None else f'{gesture} - {spec.get("name","") if spec else "Unmapped"}'
            put_text(frame, f"Gesture: {label}", (18,32))
            put_text(frame, f"FPS: {fps:.1f}", (18,60))
            put_text(frame, f"REC: {'ON' if recorder.active else 'OFF'}", (18,88))
            put_text(frame, "Q Quit | S Screenshot | R Record | C Reload Config | L Landmarks", (18, frame.shape[0]-18), 0.5, 1)

            recorder.write(frame)
            cv2.imshow("Trend Cute Filter", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord(controls.get("quit","q")):
                break
            if key == ord(controls.get("screenshot","s")):
                path = screenshot(frame, ROOT / "output")
                print(f"Screenshot: {path}")
            if key == ord(controls.get("record","r")):
                active, path = recorder.toggle(frame)
                print(f"Recording {'started' if active else 'saved'}: {path}")
            if key == ord(controls.get("landmarks","l")):
                state = tracker.toggle_draw()
                print(f"Landmarks: {state}")
            if key == ord(controls.get("reload","c")):
                now = time.perf_counter()
                if now-last_config_reload > 0.25:
                    config = load_config()
                    loader.clear()
                    player.reset()
                    last_config_reload = now
                    print("Config reloaded")

    finally:
        recorder.close()
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
