"""Motion tab — Steadicam simulation and Camera Shake controls."""
import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox, QPushButton, QSpinBox, QHBoxLayout, QLabel,
)
from camera_rig.widgets import SliderSpinRow


def build_motion_tab(ui):
    """Build the Motion tab and attach widgets to the ui instance."""
    tab = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(8)

    # ── Steadicam / Gimbal ───────────────────────────────────────────
    grp_sc = QGroupBox("Steadicam / Gimbal")
    g_sc = QVBoxLayout()
    g_sc.setSpacing(8)

    ui.steadicam_checkbox = QCheckBox("Enable Steadicam")
    g_sc.addWidget(ui.steadicam_checkbox)

    ui.steadicam_tension_row = SliderSpinRow(
        "Spring Tension", 0.1, 50.0, 10.0, decimals=1
    )
    g_sc.addWidget(ui.steadicam_tension_row)

    ui.steadicam_drag_row = SliderSpinRow(
        "Drag", 0.01, 2.0, 0.5, decimals=2
    )
    g_sc.addWidget(ui.steadicam_drag_row)

    ui.steadicam_recalc_btn = QPushButton("Recalculate Simulation")
    g_sc.addWidget(ui.steadicam_recalc_btn)

    grp_sc.setLayout(g_sc)
    layout.addWidget(grp_sc)

    # ── Camera Shake ─────────────────────────────────────────────────
    grp_shake = QGroupBox("Camera Shake")
    g_sh = QVBoxLayout()
    g_sh.setSpacing(8)

    ui.shake_checkbox = QCheckBox("Enable Shake")
    g_sh.addWidget(ui.shake_checkbox)

    ui.shake_frequency_row = SliderSpinRow(
        "Frequency", 0.01, 10.0, 0.5, decimals=2
    )
    g_sh.addWidget(ui.shake_frequency_row)

    ui.shake_strength_x_row = SliderSpinRow(
        "Strength X", 0.0, 100.0, 2.0, decimals=1
    )
    g_sh.addWidget(ui.shake_strength_x_row)

    ui.shake_strength_y_row = SliderSpinRow(
        "Strength Y", 0.0, 100.0, 2.0, decimals=1
    )
    g_sh.addWidget(ui.shake_strength_y_row)

    ui.shake_strength_z_row = SliderSpinRow(
        "Strength Z", 0.0, 50.0, 1.0, decimals=1
    )
    g_sh.addWidget(ui.shake_strength_z_row)

    seed_row = QHBoxLayout()
    lbl_seed = QLabel("Seed:")
    lbl_seed.setObjectName("lbl_section")
    ui.shake_seed_spin = QSpinBox()
    ui.shake_seed_spin.setRange(0, 9999)
    ui.shake_seed_spin.setValue(42)
    ui.shake_randomize_btn = QPushButton("Randomize")
    seed_row.addWidget(lbl_seed)
    seed_row.addWidget(ui.shake_seed_spin)
    seed_row.addWidget(ui.shake_randomize_btn)
    g_sh.addLayout(seed_row)

    grp_shake.setLayout(g_sh)
    layout.addWidget(grp_shake)

    layout.addStretch()
    tab.setLayout(layout)
    return tab
