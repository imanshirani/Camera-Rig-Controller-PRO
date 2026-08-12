from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QCheckBox, QDoubleSpinBox,
)


def build_setup_tab(ui):
    """Build the Setup tab and attach widgets to the ui instance."""
    tab = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(8)

    grp = QGroupBox("Scene Camera")
    grp_layout = QVBoxLayout()
    grp_layout.setSpacing(6)

    lbl = QLabel("Select a camera:")
    lbl.setObjectName("lbl_section")
    grp_layout.addWidget(lbl)

    ui.camera_combo = QComboBox()
    grp_layout.addWidget(ui.camera_combo)

    # Crane height
    crane_row = QHBoxLayout()
    lbl_crane = QLabel("Crane Height:")
    lbl_crane.setObjectName("lbl_section")
    ui.crane_height_spinbox = QDoubleSpinBox()
    ui.crane_height_spinbox.setRange(0.0, 99999.0)
    ui.crane_height_spinbox.setValue(127.0)
    ui.crane_height_spinbox.setDecimals(2)
    crane_row.addWidget(lbl_crane)
    crane_row.addWidget(ui.crane_height_spinbox)
    grp_layout.addLayout(crane_row)

    btn_row = QHBoxLayout()
    ui.refresh_cameras_btn = QPushButton("Refresh")
    ui.install_rig_btn = QPushButton("Install Rig")
    ui.install_rig_btn.setObjectName("btn_primary")
    btn_row.addWidget(ui.refresh_cameras_btn)
    btn_row.addWidget(ui.install_rig_btn)
    grp_layout.addLayout(btn_row)
    grp.setLayout(grp_layout)
    layout.addWidget(grp)

    grp_rig = QGroupBox("Rig Controls")
    gr = QVBoxLayout()
    gr.setSpacing(6)
    ui.toggle_helpers_btn = QPushButton("Hide Rig Helpers")
    gr.addWidget(ui.toggle_helpers_btn)
    ui.lookat_checkbox = QCheckBox("Enable LookAt  (Target Lock)")
    ui.lookat_checkbox.setChecked(True)
    gr.addWidget(ui.lookat_checkbox)
    ui.log_positions_btn = QPushButton("Log Rig Positions")
    ui.log_positions_btn.setStyleSheet("font-size:10px;")
    gr.addWidget(ui.log_positions_btn)
    grp_rig.setLayout(gr)
    layout.addWidget(grp_rig)

    layout.addStretch()

    ui.reset_all_btn = QPushButton("Reset All Controls")
    ui.reset_all_btn.setObjectName("btn_danger")
    layout.addWidget(ui.reset_all_btn)
    tab.setLayout(layout)
    return tab
