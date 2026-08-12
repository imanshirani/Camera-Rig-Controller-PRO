"""Vertigo (Dolly Zoom) tab UI."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QSpinBox,
)
from camera_rig.widgets import SliderSpinRow


def build_vertigo_tab(ui):
    """Build the Vertigo tab and attach widgets to the ui instance."""
    tab = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(8)

    # ── Vertigo / Dolly Zoom ─────────────────────────────────────────
    grp = QGroupBox("Vertigo / Dolly Zoom")
    g = QVBoxLayout()
    g.setSpacing(8)

    ui.vertigo_subject_dist_row = SliderSpinRow(
        "Subject Distance", 1.0, 10000.0, 300.0, decimals=1, unit=" u"
    )
    g.addWidget(ui.vertigo_subject_dist_row)

    ui.vertigo_dolly_start_row = SliderSpinRow(
        "Dolly Start %", 0.0, 100.0, 0.0, decimals=1, unit="%"
    )
    g.addWidget(ui.vertigo_dolly_start_row)

    ui.vertigo_dolly_end_row = SliderSpinRow(
        "Dolly End %", 0.0, 100.0, 80.0, decimals=1, unit="%"
    )
    g.addWidget(ui.vertigo_dolly_end_row)

    frame_row = QHBoxLayout()
    lbl_sf = QLabel("Start F:")
    lbl_sf.setObjectName("lbl_section")
    ui.vertigo_start_frame = QSpinBox()
    ui.vertigo_start_frame.setRange(-10000, 10000)
    ui.vertigo_start_frame.setValue(0)
    lbl_ef = QLabel("End F:")
    lbl_ef.setObjectName("lbl_section")
    ui.vertigo_end_frame = QSpinBox()
    ui.vertigo_end_frame.setRange(-10000, 10000)
    ui.vertigo_end_frame.setValue(100)
    frame_row.addWidget(lbl_sf)
    frame_row.addWidget(ui.vertigo_start_frame)
    frame_row.addWidget(lbl_ef)
    frame_row.addWidget(ui.vertigo_end_frame)
    g.addLayout(frame_row)

    dir_row = QHBoxLayout()
    lbl_dir = QLabel("Direction:")
    lbl_dir.setObjectName("lbl_section")
    ui.vertigo_direction_combo = QComboBox()
    ui.vertigo_direction_combo.addItems([
        "Pull Out (zoom in)",
        "Push In (zoom out)",
    ])
    dir_row.addWidget(lbl_dir)
    dir_row.addWidget(ui.vertigo_direction_combo)
    g.addLayout(dir_row)

    vertigo_tangent_row = QHBoxLayout()
    lbl_vt = QLabel("Tangent:")
    lbl_vt.setObjectName("lbl_section")
    ui.vertigo_tangent_combo = QComboBox()
    ui.vertigo_tangent_combo.addItems(["Ease (Slow)", "Linear", "Fast", "Smooth"])
    vertigo_tangent_row.addWidget(lbl_vt)
    vertigo_tangent_row.addWidget(ui.vertigo_tangent_combo)
    g.addLayout(vertigo_tangent_row)

    ui.bake_vertigo_btn = QPushButton("Bake Vertigo")
    ui.bake_vertigo_btn.setObjectName("btn_primary")
    g.addWidget(ui.bake_vertigo_btn)

    grp.setLayout(g)
    layout.addWidget(grp)

    # ── Preview ──────────────────────────────────────────────────────
    grp_prev = QGroupBox("Preview")
    gp = QVBoxLayout()
    gp.setSpacing(6)
    ui.vertigo_fov_label = QLabel("Current FOV: --")
    ui.vertigo_fov_label.setObjectName("lbl_section")
    ui.vertigo_focal_end_label = QLabel("Required Focal at End: --")
    ui.vertigo_focal_end_label.setStyleSheet("color:#e8823c; font-weight:600;")
    gp.addWidget(ui.vertigo_fov_label)
    gp.addWidget(ui.vertigo_focal_end_label)
    grp_prev.setLayout(gp)
    layout.addWidget(grp_prev)

    layout.addStretch()
    tab.setLayout(layout)
    return tab
