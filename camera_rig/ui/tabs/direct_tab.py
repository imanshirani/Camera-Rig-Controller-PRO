from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox, QPushButton, QLabel,
)
from camera_rig.widgets import SliderSpinRow


def build_direct_tab(ui):
    """Build the Direct Controls tab and attach widgets to the ui instance."""
    tab = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(8)

    # ── Camera Position ──────────────────────────────────────────────
    grp_pos = QGroupBox("Camera Position")
    gp = QVBoxLayout()
    gp.setSpacing(8)
    ui.truck_row    = SliderSpinRow("Left / Right  (Truck)",   -1000, 1000, 0, decimals=1, unit=" u")
    ui.pedestal_row = SliderSpinRow("Up / Down  (Pedestal)",   -1000, 1000, 0, decimals=1, unit=" u")
    gp.addWidget(ui.truck_row)
    gp.addWidget(ui.pedestal_row)
    grp_pos.setLayout(gp)
    layout.addWidget(grp_pos)

    # ── Target Aim ───────────────────────────────────────────────────
    grp_aim = QGroupBox("Target Aim")
    ga = QVBoxLayout()
    ga.setSpacing(8)

    # Orbit mode toggle
    ui.orbit_mode_checkbox = QCheckBox("Orbit Mode  (Pan/Tilt rotate around camera)")
    ui.orbit_mode_checkbox.setChecked(False)
    ga.addWidget(ui.orbit_mode_checkbox)

    # hint label — updates when mode changes
    ui.aim_mode_label = QLabel("Mode: Linear  —  target moves on straight line")
    ui.aim_mode_label.setStyleSheet("color:#555; font-size:10px;")
    ga.addWidget(ui.aim_mode_label)

    ui.pan_row  = SliderSpinRow("Left / Right  (Pan)",  -1000, 1000, 0, decimals=1, unit=" u")
    ui.tilt_row = SliderSpinRow("Up / Down  (Tilt)",    -1000, 1000, 0, decimals=1, unit=" u")
    ga.addWidget(ui.pan_row)
    ga.addWidget(ui.tilt_row)
    grp_aim.setLayout(ga)
    layout.addWidget(grp_aim)

    # ── Camera Orientation ───────────────────────────────────────────
    grp_ori = QGroupBox("Camera Orientation")
    go = QVBoxLayout()
    go.setSpacing(8)
    ui.roll_row = SliderSpinRow("Roll  (Dutch Tilt)", -45.0, 45.0, 0.0, decimals=1, unit="°")
    go.addWidget(ui.roll_row)
    grp_ori.setLayout(go)
    layout.addWidget(grp_ori)

    ui.lock_target_checkbox = QCheckBox("Lock Target to Camera Position")
    layout.addWidget(ui.lock_target_checkbox)
    layout.addStretch()

    ui.reset_direct_btn = QPushButton("Reset Direct Controls")
    ui.reset_direct_btn.setObjectName("btn_danger")
    layout.addWidget(ui.reset_direct_btn)
    tab.setLayout(layout)
    return tab
