<div align="center">

# 🎀 Trend Cute Filter

### Real-time Gesture Controlled Emoji, PNG, Sticker, Image & GIF Filter

<img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/OpenCV-Realtime-green?style=for-the-badge">
<img src="https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange?style=for-the-badge">
<img src="https://img.shields.io/badge/Customizable-100%25-ff69b4?style=for-the-badge">

</div>

---

## ✨ Features

- Real-time webcam
- Hand tracking
- 0–5 finger gesture detection
- Gesture stabilization
- Emoji filter
- PNG/JPG/JPEG/WebP sticker filter
- Animated GIF filter
- Transparent alpha overlay
- Fallback emoji when file asset is missing
- Per-gesture custom filter mapping
- Fade animation
- Bounce animation
- Floating animation
- Optional rotation
- Sparkle particles
- Heart particles
- Flower particles
- Screenshot
- Video recording
- Runtime config reload
- Toggle hand landmarks
- GIF and image cache
- Mirror camera
- FPS counter

## 📂 Structure

```text
trend-cute-filter/
├── assets/
│   ├── gifs/
│   ├── characters/
│   ├── particles/
│   ├── sounds/
│   └── icons/
├── src/
│   ├── main.py
│   ├── camera.py
│   ├── hand_tracker.py
│   ├── gesture_detector.py
│   ├── gif_loader.py
│   ├── gif_player.py
│   ├── overlay_engine.py
│   ├── animation.py
│   ├── particle_system.py
│   ├── character_manager.py
│   ├── effects.py
│   ├── config.py
│   └── utils.py
├── output/
├── config.json
├── requirements.txt
└── README.md
```

## 🚀 Setup

```bash
python3 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## ▶️ Run

```bash
python src/main.py
```

## 🎛 Controls

| Key | Action |
|---|---|
| Q | Quit |
| S | Screenshot |
| R | Start/stop recording |
| C | Reload `config.json` |
| L | Toggle MediaPipe landmarks |

## 🎨 Customize Filter

Semua filter ada di `config.json`.

### Emoji

```json
"1": {
  "name": "Smile",
  "type": "emoji",
  "value": "😊",
  "particle": "sparkle"
}
```

### PNG Sticker

Simpan file ke:

```text
assets/characters/my_sticker.png
```

Kemudian:

```json
"2": {
  "name": "My Sticker",
  "type": "image",
  "value": "assets/characters/my_sticker.png",
  "fallback_emoji": "🐱",
  "particle": "heart"
}
```

### GIF

```json
"3": {
  "name": "My GIF",
  "type": "gif",
  "value": "assets/gifs/my_animation.gif",
  "fallback_emoji": "🧸",
  "particle": "sparkle"
}
```

Setelah mengubah `config.json`, tekan `C` saat aplikasi berjalan.

## 🖼 Supported Assets

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.gif`
- Unicode emoji

PNG transparan adalah format yang paling disarankan untuk sticker.

## 🎯 Gesture

| Finger Count | Config Key |
|---:|---|
| 0 | `"0"` |
| 1 | `"1"` |
| 2 | `"2"` |
| 3 | `"3"` |
| 4 | `"4"` |
| 5 | `"5"` |

## ⚙ Position & Animation

Ubah bagian:

```json
"filter": {
  "position": "hand",
  "scale": 0.32,
  "offset_x": 0,
  "offset_y": -120,
  "fade_speed": 4.5,
  "bounce": true,
  "floating": true,
  "rotation": false
}
```

## 📸 Output

Screenshot dan video tersimpan otomatis di:

```text
output/
```
