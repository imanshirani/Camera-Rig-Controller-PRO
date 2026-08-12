"""Framing tab — Aspect Ratio presets, Safe Frame, and Composition Guides."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QCheckBox,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from camera_rig.framing.viewport_overlay import GUIDE_DEFAULTS

_CINEMA_PRESETS = [
    "2.39:1 (Anamorphic Scope)",
    "2.35:1 (Anamorphic Classic)",
    "1.85:1 (Flat / US Widescreen)",
    "1.78:1 (16:9 HD)",
    "1.66:1 (European Widescreen)",
    "1.43:1 (IMAX)",
    "1.33:1 (4:3 Classic / Academy)",
    "1:1 (Square / Instagram)",
    "9:16 (Vertical / Mobile)",
]

_GOLDEN_PRESETS = [
    "1.618:1 (Golden Ratio — φ)",
    "1.272:1 (Golden Root — √φ)",
    "2.058:1 (Golden Square — φ²)",
]

# Ordered list of guides: (widget_suffix, label_text, guide_key)
_GUIDES = [
    ("thirds",   "Rule of Thirds",    "thirds"),
    ("golden",   "Golden Ratio Lines","golden"),
    ("center",   "Center Cross",      "center"),
    ("diag",     "Diagonal Lines",    "diag"),
    ("triangle", "Golden Triangle",   "triangle"),
    ("spiral",   "Golden Spiral",     "spiral"),
]

_COLOR_NAMES = [
    "Custom",
    "White",   "Yellow",  "Orange",  "Red",
    "Green",   "Cyan",    "Blue",    "Purple",
]

_COLOR_VALUES = {
    "White":  (255, 255, 255),
    "Yellow": (255, 220,   0),
    "Orange": (255, 140,   0),
    "Red":    (220,  50,  50),
    "Green":  (  0, 220,  80),
    "Cyan":   (  0, 200, 220),
    "Blue":   ( 60, 100, 255),
    "Purple": (180, 100, 255),
}


def _make_color_swatch(r: int, g: int, b: int) -> str:
    """Return a CSS background-color string for a colored swatch button."""
    return (
        f"QPushButton {{ background: rgb({r},{g},{b}); border: 1px solid #555;"
        f" border-radius: 3px; min-width: 22px; max-width: 22px;"
        f" min-height: 18px; max-height: 18px; }}"
        f"QPushButton:hover {{ border: 1px solid #e8823c; }}"
    )


def build_framing_tab(ui):
    """Build the Framing tab and attach widgets to the ui instance."""
    tab = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(8)

    # ── Cinema Aspect Ratios ─────────────────────────────────────────
    grp_cinema = QGroupBox("Cinema Aspect Ratios")
    gc = QVBoxLayout()
    gc.setSpacing(6)
    ui.aspect_combo = QComboBox()
    ui.aspect_combo.addItems(_CINEMA_PRESETS)
    ui.aspect_combo.setCurrentIndex(3)
    gc.addWidget(ui.aspect_combo)
    ui.apply_aspect_btn = QPushButton("Apply")
    ui.apply_aspect_btn.setObjectName("btn_primary")
    gc.addWidget(ui.apply_aspect_btn)
    ui.current_aspect_label = QLabel("")
    ui.current_aspect_label.setObjectName("lbl_section")
    gc.addWidget(ui.current_aspect_label)
    grp_cinema.setLayout(gc)
    layout.addWidget(grp_cinema)

    # ── Golden Ratio Aspects ─────────────────────────────────────────
    grp_golden = QGroupBox("Golden Ratio Aspects")
    gg = QVBoxLayout()
    gg.setSpacing(6)
    lbl_phi = QLabel("φ = 1.618  —  the golden proportion")
    lbl_phi.setStyleSheet("color:#888; font-size:10px;")
    gg.addWidget(lbl_phi)
    ui.golden_combo = QComboBox()
    ui.golden_combo.addItems(_GOLDEN_PRESETS)
    gg.addWidget(ui.golden_combo)
    ui.apply_golden_btn = QPushButton("Apply")
    ui.apply_golden_btn.setObjectName("btn_primary")
    gg.addWidget(ui.apply_golden_btn)
    grp_golden.setLayout(gg)
    layout.addWidget(grp_golden)

    # ── Safe Frame ───────────────────────────────────────────────────
    grp_safe = QGroupBox("Safe Frame")
    gs = QVBoxLayout()
    gs.setSpacing(6)
    ui.safe_frame_checkbox = QCheckBox("Show Safe Frame in Viewport")
    gs.addWidget(ui.safe_frame_checkbox)
    grp_safe.setLayout(gs)
    layout.addWidget(grp_safe)

    # ── Composition Guides ───────────────────────────────────────────
    grp_guides = QGroupBox("Composition Guides")
    gi = QVBoxLayout()
    gi.setSpacing(4)

    lbl_hint = QLabel("Checkbox = on/off   ·   Swatch = pick color")
    lbl_hint.setStyleSheet("color:#555; font-size:10px;")
    gi.addWidget(lbl_hint)

    for suffix, label_text, key in _GUIDES:
        r, g, b = GUIDE_DEFAULTS[key]
        ui._guide_colors[key] = [r, g, b]

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        # Checkbox
        chk = QCheckBox(label_text)
        setattr(ui, f'guide_{suffix}_checkbox', chk)
        row.addWidget(chk)

        row.addStretch()

        # Color combo
        color_combo = QComboBox()
        color_combo.setFixedWidth(80)
        color_combo.addItems(_COLOR_NAMES)
        color_combo.setCurrentIndex(0)
        setattr(ui, f'guide_{suffix}_color_combo', color_combo)
        row.addWidget(color_combo)

        # Swatch button shows current color
        swatch = QPushButton()
        swatch.setStyleSheet(_make_color_swatch(r, g, b))
        swatch.setToolTip(f"Current: rgb({r},{g},{b})")
        setattr(ui, f'guide_{suffix}_swatch', swatch)
        row.addWidget(swatch)

        gi.addLayout(row)

    grp_guides.setLayout(gi)
    layout.addWidget(grp_guides)

    layout.addStretch()
    tab.setLayout(layout)
    return tab
