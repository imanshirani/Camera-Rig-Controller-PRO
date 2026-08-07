# Camera Rig Controller PRO

A professional camera rigging tool for **3ds Max**, built with Python and PySide6.

[![Donate ❤️](https://img.shields.io/badge/Donate-PayPal-00457C?style=flat-square&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4)
![3dsmax](https://img.shields.io/badge/Autodesk-3ds%20Max-0696D7?style=flat-square&logo=autodesk)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=flat-square&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)
![Version](https://img.shields.io/badge/version-0.0.1-orange)

---

## Features

### Rig System
- One-click rig installation on any camera type (Standard, Physical, VRay, Corona)
- Full crane + dolly hierarchy: `DOLLY → CRANE_BASE → CRANE_ARM → MASTER → PIVOT → Camera`
- Custom shape support via `assets/shape.max`
- Adjustable crane height before install

### Dolly Tab
- Path-based dolly movement with percentage control
- Straight track with resizable length
- Orbit / Arc Shot — circular track around subject
- Custom path assignment with Flow and Bank support
- Bake dolly animation with Ease In/Out and tangent control

### Crane Tab
- Arm pitch (X rotation)
- Base yaw (Z rotation)
- Arm reach / height control

### Motion Tab
- **Steadicam** — lag helper node between dolly and crane
- **Camera Shake** — Noise Position controller on pivot with per-axis strength, frequency, and seed

### Direct Controls Tab
- Truck (left/right relative to camera direction)
- Pedestal (up/down)
- Pan — Linear or Orbit mode
- Tilt (up/down)
- Roll / Dutch Tilt
- Lock Target to Camera toggle

### Lens Tab
- Focal length control (universal — works with all camera types)
- Near/Far clip planes
- DOF enable + Focus Distance
- Rack Focus — bake animated focus pull between two distances
- Focus Subject Picker — click any object to set focus distance
- Camera property logger for debugging

### Framing Tab
- Cinema aspect ratio presets (2.39:1, 1.85:1, 16:9, IMAX, and more)
- Golden Ratio aspect presets (φ, √φ, φ²)
- Safe Frame toggle
- Composition guides overlay directly on viewport:
  - Rule of Thirds
  - Golden Ratio Lines
  - Center Cross
  - Diagonal Lines
  - Golden Triangle
  - Golden Spiral
- Per-guide color picker with color presets

### Bookmarks Tab
- Save named camera position snapshots
- Restore any saved bookmark instantly
- Delete bookmarks

### Vertigo Tab
- Dolly Zoom (Hitchcock effect) — simultaneous dolly movement and focal length change
- Preview panel showing required focal length at end frame
- Push In / Pull Out direction

---

## Requirements

- **3ds Max 2022+**
- **Python 3.x** (bundled with 3ds Max)
- **PySide6** (bundled with 3ds Max 2022+)

---

## Installation

1. Clone or download this repository
2. Place the folder anywhere on your system
3. In 3ds Max, open the **MAXScript Editor** or **Script** menu
4. Run the file: `Camera Rig Controller PRO.py`

```
Camera Pro/
├── Camera Rig Controller PRO.py   ← Run this
├── assets/
│   └── shape.max                  ← Custom rig shapes (optional)
└── camera_rig/
    ├── core/                      ← 3ds Max logic
    └── ui/                        ← PySide6 interface
```

---

## Custom Shapes

To use custom shapes for rig controls, create a `shape.max` file inside the `assets/` folder containing objects with these exact names:

| Object Name  | Rig Node     |
|--------------|--------------|
| `DOLLY_CTRL` | Dolly        |
| `CRANE_BASE` | Crane Base   |
| `CRANE_ARM`  | Crane Arm    |
| `MASTER`     | Master       |
| `PIVOT`      | Pivot        |
| `TARGET`     | Target       |
| `TRACK_CTRL` | Track Handle |

If a shape is not found in the file, a primitive fallback is used automatically.

---

## Usage

1. **Setup Tab** — Select a camera, set Crane Height, click **Install Rig**
2. **Dolly Tab** — Move the camera along the track, create orbit paths
3. **Crane Tab** — Adjust crane arm pitch, base rotation, and reach
4. **Direct Controls** — Fine-tune camera and target position
5. **Lens Tab** — Control focal length, clipping, and depth of field
6. **Framing Tab** — Set aspect ratio and enable composition guides on viewport
7. **Motion Tab** — Add camera shake or steadicam simulation

---

## Architecture

```
camera_rig/
├── constants.py          — VERSION, URLs
├── theme.py              — Dark palette + QSS stylesheet
├── widgets/
│   ├── slider_spin_row.py — Slider + Spinbox compound widget
│   └── about_dialog.py
├── core/                 — Pure 3ds Max logic (no Qt)
│   ├── rig_builder.py    — Install, cleanup, load rig
│   ├── rig_controls.py   — Dolly, crane, direct controls
│   ├── rig_utils.py      — State reading, helpers
│   ├── lens_controls.py  — Focal, clipping, DOF (universal)
│   ├── camera_shake.py   — Noise Position controller
│   ├── steadicam.py      — Lag simulation
│   ├── rack_focus.py     — Focus pull animation
│   ├── vertigo.py        — Dolly zoom
│   └── bookmarks.py      — Shot bookmarks
├── framing/
│   └── viewport_overlay.py — Aspect ratios + composition guides
└── ui/
    ├── main_window.py    — CameraRigUI bridge class
    └── tabs/             — One file per tab
```

---

## Supported Camera Types

| Camera | Focal Length | Clipping | DOF |
|--------|-------------|---------|-----|
| Standard Free/Target | ✅ | ✅ | ✅ |
| Physical Camera | ✅ | ✅ | ✅ |
| VRay Physical Camera | ✅ | ✅ | ✅ |
| Corona Camera | ✅ | ✅ | ✅ |

---

## License

MIT License — free for personal and commercial use.

---

## Author

**Iman Shirani**

- GitHub: [github.com/imanshirani](https://github.com/imanshirani)
- Support: [PayPal Donate](https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4)
