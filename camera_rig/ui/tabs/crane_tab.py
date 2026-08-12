from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel, QSlider, QPushButton,
)
from PySide6.QtCore import Qt
from camera_rig.widgets import SliderSpinRow


def build_crane_tab(ui):
    """Build the Crane tab and attach widgets to the ui instance."""
    tab = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(8)

    grp_arm = QGroupBox("Arm — Pitch")
    ga = QVBoxLayout()
    ga.setSpacing(6)
    ui.crane_arm_label = QLabel("0.0°")
    ui.crane_arm_label.setAlignment(Qt.AlignCenter)
    ui.crane_arm_label.setStyleSheet("color:#e8823c; font-size:13px; font-weight:600;")
    ga.addWidget(ui.crane_arm_label)
    ui.crane_arm_slider = QSlider(Qt.Horizontal)
    ui.crane_arm_slider.setRange(-900, 900)
    ga.addWidget(ui.crane_arm_slider)
    grp_arm.setLayout(ga)
    layout.addWidget(grp_arm)

    grp_base = QGroupBox("Base — Yaw")
    gb = QVBoxLayout()
    gb.setSpacing(6)
    ui.crane_base_label = QLabel("0.0°")
    ui.crane_base_label.setAlignment(Qt.AlignCenter)
    ui.crane_base_label.setStyleSheet("color:#e8823c; font-size:13px; font-weight:600;")
    gb.addWidget(ui.crane_base_label)
    ui.crane_base_slider = QSlider(Qt.Horizontal)
    ui.crane_base_slider.setRange(-1800, 1800)
    gb.addWidget(ui.crane_base_slider)
    grp_base.setLayout(gb)
    layout.addWidget(grp_base)

    grp_reach = QGroupBox("Arm Reach")
    gr = QVBoxLayout()
    gr.setSpacing(6)
    ui.arm_reach_row = SliderSpinRow("Height", 0, 2000, 100, decimals=1, unit=" u")
    gr.addWidget(ui.arm_reach_row)
    grp_reach.setLayout(gr)
    layout.addWidget(grp_reach)

    layout.addStretch()
    ui.reset_crane_btn = QPushButton("Reset Crane")
    ui.reset_crane_btn.setObjectName("btn_danger")
    layout.addWidget(ui.reset_crane_btn)
    tab.setLayout(layout)
    return tab
