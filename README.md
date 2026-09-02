<div align="center">

# 🎀 Trend Cute Filter Studio

### Face Tracking + Hand Gesture + PNG/GIF Sticker + Cute Preset Engine

<img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/OpenCV-Realtime-green?style=for-the-badge&logo=opencv">
<img src="https://img.shields.io/badge/MediaPipe-Face%20%2B%20Hand-orange?style=for-the-badge">
<img src="https://img.shields.io/badge/Custom-PNG%20%7C%20GIF%20%7C%20Emoji-ff69b4?style=for-the-badge">

</div>

---

## ✨ Fitur Lengkap

- Webcam realtime 30–60 FPS tergantung perangkat
- Mirror camera
- MediaPipe Face Mesh
- Multi-face tracking
- MediaPipe Hands
- Multi-hand tracking
- 21 hand landmarks
- Face anchors presisi untuk kepala, mata, alis, pipi, hidung, mulut, dagu
- Head roll, yaw, pitch estimation
- Face overlay mengikuti posisi, ukuran, dan rotasi kepala
- PNG transparan
- JPG/JPEG/WebP
- Animated GIF
- Unicode emoji
- GIF/image cache
- Fallback emoji jika asset custom hilang
- 0–5 finger filter lama tetap tersedia
- Named gesture `fist`, `point`, `peace`, `three`, `four`, `open_palm`, `thumb`, `pinch`
- Gesture stabilization
- Hand-to-face proximity trigger
- Fingertip-to-face-anchor trigger
- Blink trigger
- Mouth-open trigger
- Smile state
- Head tilt state
- Fade animation
- Bounce animation
- Floating animation
- Rotation animation
- Sparkle particle
- Heart particle
- Flower particle
- Soft glow face paint
- Blush face paint
- Nose blush
- Freckles
- Preset system
- Hot switch preset tanpa restart
- Auto reload `config.json`
- Screenshot
- Video recording
- Debug HUD
- Toggle face mesh
- Toggle hand mesh
- Toggle particles
- Toggle procedural face paint
- Config validator
- Optional Windows WAV sound feedback
- Auto-cycle preset
- Toggle HandFX/interactions saat runtime
- Asset contoh original siap uji

## 🎭 Preset Bawaan

### 1. Cat Cute

- Cat ears
- Pink blush
- Nose blush
- White cheek squiggles
- Small sparkle decoration

### 2. Flower Stamps

- Cute flower stickers di forehead dan pipi
- Nose bandage sticker
- Soft blush

### 3. Bunny Soft

- Bunny ears
- White/pink cheek hearts
- Soft glow
- Pink blush

### 4. Comic Pink Cap

- Pink star cap original
- Comic moustache original
- Head tracking + rotation

### 5. Teddy Freckles

- Teddy face stamps
- Freckles
- Soft blush

### 6. Minimal Hearts

- Minimal cheek hearts
- Soft blush

Preset dibuat sebagai interpretasi original dari gaya filter cute umum. Asset tidak menyalin logo atau karakter bermerek dari gambar referensi.

## 📂 Struktur Project

```text
trend-cute-filter/
├── assets/
│   ├── characters/
│   │   ├── cat.png
│   │   ├── cat_ears_pair.png
│   │   ├── bunny_ears_pair.png
│   │   ├── cheek_squiggle.png
│   │   ├── cheek_hearts.png
│   │   ├── flower_stamp.png
│   │   ├── teddy_stamp.png
│   │   ├── pink_star_cap.png
│   │   ├── comic_moustache.png
│   │   ├── nose_bandage.png
│   │   └── white_sparkles.png
│   ├── gifs/
│   │   ├── teddy.gif
│   │   ├── cute_burst.gif
│   │   └── sparkle_pop.gif
│   ├── particles/
│   ├── sounds/
│   └── icons/
├── src/
│   ├── main.py
│   ├── camera.py
│   ├── face_tracker.py
│   ├── face_painter.py
│   ├── preset_manager.py
│   ├── hand_tracker.py
│   ├── gesture_detector.py
│   ├── interaction_engine.py
│   ├── gif_loader.py
│   ├── gif_player.py
│   ├── overlay_engine.py
│   ├── animation.py
│   ├── particle_system.py
│   ├── character_manager.py
│   ├── effects.py
│   ├── config.py
│   └── utils.py
├── tools/
│   └── validate_config.py
├── output/
├── config.json
├── requirements.txt
├── setup.sh
├── run.sh
└── README.md
```

## 🚀 Setup Windows Git Bash

Project ditujukan untuk setup kamu yang `python3` mengarah ke Python 3.11.

```bash
cd /d/Development/Project/trend-cute-filter
bash setup.sh
```

Manual:

```bash
python3 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python tools/validate_config.py
```

## ▶️ Run

```bash
bash run.sh
```

atau:

```bash
source .venv/Scripts/activate
python src/main.py
```

## ⌨️ Controls

| Key | Fungsi |
|---|---|
| `1`–`6` | Pilih preset wajah |
| `N` | Preset berikutnya |
| `B` | Preset sebelumnya |
| `S` | Screenshot |
| `R` | Start/stop recording |
| `C` | Reload config |
| `L` | Toggle hand landmarks |
| `F` | Toggle face mesh |
| `D` | Toggle debug HUD |
| `P` | Toggle particles |
| `V` | Toggle face paint |
| `A` | Auto-cycle preset |
| `H` | Toggle hand filter |
| `I` | Toggle interactions |
| `M` | Mute/unmute sound |
| `Q` | Quit |

## 🎯 Face Anchors

```text
face_center
head
head_top
head_left
head_right
forehead
forehead_left
forehead_right
left_eye
right_eye
left_pupil
right_pupil
left_brow
right_brow
between_eyes
left_cheek
right_cheek
left_cheek_inner
right_cheek_inner
nose
nose_bridge
mouth
upper_lip
lower_lip
chin
```

## ✋ Hand Anchors

```text
palm
wrist
thumb_tip
index_tip
middle_tip
ring_tip
pinky_tip
```

## 🖼 Custom PNG Sticker

Taruh asset:

```text
assets/characters/my_sticker.png
```

Tambahkan ke salah satu preset di `config.json`:

```json
{
  "id": "my_left_cheek_sticker",
  "enabled": true,
  "target": "face",
  "anchor": "left_cheek",
  "type": "image",
  "value": "assets/characters/my_sticker.png",
  "fallback_emoji": "✨",
  "scale": 0.25,
  "offset_x": 0.0,
  "offset_y": 0.0,
  "follow_rotation": true,
  "opacity": 1.0,
  "animation": {
    "bounce": true,
    "floating": false,
    "rotation": false
  }
}
```

## 🎞 Custom GIF

```json
{
  "id": "my_head_gif",
  "enabled": true,
  "target": "face",
  "anchor": "head_top",
  "type": "gif",
  "value": "assets/gifs/my_filter.gif",
  "fallback_emoji": "🎀",
  "scale": 0.8,
  "offset_y": -0.1,
  "follow_rotation": true
}
```

## 🎨 Membuat Preset Sendiri

Tambahkan item baru:

```json
"my_preset": {
  "name": "My Preset",
  "paint": {
    "enabled": true,
    "soft_glow": 0.05,
    "blush": {
      "enabled": true,
      "alpha": 0.15,
      "width": 0.16,
      "height": 0.06,
      "blur": 0.03,
      "color_bgr": [150, 150, 255]
    }
  },
  "layers": []
}
```

Masukkan ID preset ke `face_presets.order`.

## 🤏 Gesture Interactions

### Open palm dekat wajah

Memunculkan animated cute burst.

### Peace dekat pipi

Memunculkan flower sticker dan flower particles.

### Pinch dekat pipi

Memunculkan heart sticker dan heart particles.

### Blink

Memunculkan sparkle.

### Mouth open

Memunculkan animated sparkle pop.

### Head tilt

Memunculkan flower effect.

## 🧩 Trigger Types

```text
gesture
gesture_near_face
hand_near_face
gesture_near_anchor
fingertip_near_anchor
face_expression
head_pose
```

## 📸 Output

Screenshot dan video disimpan di:

```text
output/
```

## ⚙️ Validasi Config

```bash
python tools/validate_config.py
```

Output sukses:

```text
CONFIG VALID
```

## 🧪 Tips Tracking

- Gunakan pencahayaan cukup
- Wajah tidak terlalu jauh dari kamera
- Hindari tangan menutup seluruh wajah terlalu lama
- PNG transparan idealnya memiliki ruang kosong yang tidak berlebihan
- Gunakan asset 512–1024 px untuk kualitas baik
- Kurangi jumlah GIF besar jika FPS turun
- Set `max_faces` ke `1` jika hanya satu pengguna untuk performa lebih tinggi
- Naikkan `smoothing` jika sticker terasa bergetar

## 🔧 Performance

Jika laptop berat menjalankan filter:

```json
"camera": {
  "width": 960,
  "height": 540,
  "fps": 30
}
```

Lalu:

```json
"face_tracking": {
  "max_faces": 1
}
```

## 🔄 Konsep Effect House

Arsitektur project ini meniru konsep umum editor AR seperti Effect House:

```text
Camera
  ↓
Face Tracker ─────→ Face Anchors ─────→ Sticker Layers
  ↓                                      ↓
Expression State                         PNG/GIF
  ↓                                      ↓
Interaction Engine ────────────────→ Animation

Hand Tracker
  ↓
Gesture Detector
  ↓
Distance to Face
  ↓
Cute Interaction Trigger
```

Ini tetap aplikasi Python/OpenCV/MediaPipe, bukan file native Effect House.
