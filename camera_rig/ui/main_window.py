"""Main CameraRigUI window — thin bridge between UI and core logic."""
import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QDockWidget, QMessageBox
from PySide6.QtCore import Qt
from pymxs import runtime as rt

from camera_rig.theme import dark_palette, QSS
from camera_rig.widgets import SliderSpinRow, AboutDialog
from camera_rig.core import rig_builder, rig_controls, lens_controls, rig_utils
from camera_rig.core import steadicam as steadicam_mod
from camera_rig.core import rack_focus, vertigo as vertigo_mod, camera_shake
from camera_rig.core.bookmarks import ShotBookmark, save_bookmark, apply_bookmark
from camera_rig.framing.viewport_overlay import (
    ASPECT_PRESETS,
    set_safe_frame, set_aspect_ratio, get_current_aspect,
    install_overlay, uninstall_overlay, set_guide, set_guide_color,
    any_guide_active, GUIDE_DEFAULTS,
)
from camera_rig.ui.tabs.setup_tab import build_setup_tab
from camera_rig.ui.tabs.dolly_tab import build_dolly_tab
from camera_rig.ui.tabs.crane_tab import build_crane_tab
from camera_rig.ui.tabs.direct_tab import build_direct_tab
from camera_rig.ui.tabs.lens_tab import build_lens_tab
from camera_rig.ui.tabs.framing_tab import build_framing_tab
from camera_rig.ui.tabs.bookmarks_tab import build_bookmarks_tab
from camera_rig.ui.tabs.motion_tab import build_motion_tab
from camera_rig.ui.tabs.vertigo_tab import build_vertigo_tab

log = logging.getLogger(__name__)


class CameraRigUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Camera Rig Controller PRO")

        self.rig_nodes = {}
        self.selected_camera = None
        self.path_constraint_controller = None
        self.initial_target_local_pos = None
        self.initial_target_world_pos = None
        self.initial_target_world_y   = 0.0
        self.initial_target_world_x = 0.0
        self.initial_target_world_z = 0.0
        self.initial_crane_base_world_pos = None
        self.initial_master_world_pos     = None
        self.initial_master_rot           = None
        self.initial_crane_base_local_pos = None
        self.initial_crane_base_world_z = None
        self._initial_arm_z = 100.0
        self._bookmarks = []

        self._build_ui()
        self._connect_signals()
        self._populate_camera_list()
        self._set_controls_enabled(False)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)

        hdr_h = QHBoxLayout()
        hdr = QLabel("CAMERA RIG")
        hdr.setObjectName("lbl_header")
        hdr_h.addWidget(hdr)
        hdr_h.addStretch()
        btn_about = QPushButton("About")
        btn_about.setFixedSize(54, 22)
        btn_about.setStyleSheet(
            "QPushButton { background:transparent; border:1px solid #3a3a3a;"
            " border-radius:3px; color:#555; font-size:10px; }"
            " QPushButton:hover { border-color:#e8823c; color:#e8823c; }"
        )
        btn_about.clicked.connect(lambda: AboutDialog(self).exec())
        hdr_h.addWidget(btn_about)
        self.main_layout.addLayout(hdr_h)

        sub = QLabel("CONTROLLER  PRO  ·  3DS MAX")
        sub.setObjectName("lbl_sub")
        self.main_layout.addWidget(sub)

        self.tabs = QTabWidget()
        self.tabs.addTab(build_setup_tab(self),    "Setup")
        self.tabs.addTab(build_dolly_tab(self),    "Dolly")
        self.tabs.addTab(build_crane_tab(self),    "Crane")
        self.tabs.addTab(build_motion_tab(self),   "Motion")
        self.tabs.addTab(build_direct_tab(self),   "Direct Controls")
        self.tabs.addTab(build_lens_tab(self),     "Lens")
        self.tabs.addTab(build_framing_tab(self),  "Framing")
        self.tabs.addTab(build_bookmarks_tab(self),"Bookmarks")
        self.tabs.addTab(build_vertigo_tab(self),  "Vertigo")

        self.main_layout.addWidget(self.tabs)
        self.setLayout(self.main_layout)

    # ------------------------------------------------------------------
    # Signal Connections
    # ------------------------------------------------------------------

    def _connect_signals(self):
        self.camera_combo.currentIndexChanged.connect(self._on_camera_selection_changed)
        self.refresh_cameras_btn.clicked.connect(self._populate_camera_list)
        self.install_rig_btn.clicked.connect(self._install_rig)
        self.reset_all_btn.clicked.connect(self._reset_all)
        self.log_positions_btn.clicked.connect(self._on_log_positions)
        self.reset_dolly_btn.clicked.connect(self._reset_dolly)
        self.reset_crane_btn.clicked.connect(self._reset_crane)
        self.reset_direct_btn.clicked.connect(self._reset_direct)
        self.dolly_slider.valueChanged.connect(self._on_dolly_slider_changed)
        self.dolly_slider.sliderReleased.connect(self._on_dolly_slider_released)
        self.update_track_length_btn.clicked.connect(self._on_update_track_length)
        self.update_orbit_radius_btn.clicked.connect(self._on_update_orbit_radius)
        self.follow_path_checkbox.toggled.connect(self._on_follow_path_toggled)
        self.bank_checkbox.toggled.connect(self._on_bank_toggled)
        self.bank_amount_spin.valueChanged.connect(self._on_bank_amount_changed)
        self.refresh_paths_btn.clicked.connect(self._populate_path_list)
        self.assign_path_btn.clicked.connect(self._assign_path)
        self.crane_arm_slider.valueChanged.connect(self._on_crane_arm_changed)
        self.crane_arm_slider.sliderReleased.connect(self._on_crane_arm_released)
        self.crane_base_slider.valueChanged.connect(self._on_crane_base_changed)
        self.crane_base_slider.sliderReleased.connect(self._on_crane_base_released)
        self.arm_reach_row.valueChanged.connect(lambda _: self._on_arm_reach_changed())
        self.orbit_mode_checkbox.toggled.connect(self._on_orbit_mode_changed)
        self.truck_row.valueChanged.connect(lambda _: self._on_truck_changed())
        self.pedestal_row.valueChanged.connect(lambda _: self._on_pedestal_changed())
        self.pan_row.valueChanged.connect(lambda _: self._on_pan_changed())
        self.tilt_row.valueChanged.connect(lambda _: self._on_tilt_changed())
        self.roll_row.valueChanged.connect(lambda _: self._on_roll_changed())
        self.toggle_helpers_btn.clicked.connect(self._toggle_helpers)
        self.lookat_checkbox.toggled.connect(self._on_lookat_toggled)
        self.focal_row.valueChanged.connect(lambda _: self._on_focal_changed())
        self.near_clip_spin.valueChanged.connect(self._on_clipping_changed)
        self.far_clip_spin.valueChanged.connect(self._on_clipping_changed)
        self.dof_checkbox.toggled.connect(self._on_dof_toggled)
        self.focus_dist_row.valueChanged.connect(lambda _: self._on_focus_dist_changed())
        self.reset_lens_btn.clicked.connect(self._reset_lens)
        self.log_cam_props_btn.clicked.connect(self._on_log_cam_props)
        # Framing — aspect
        self.apply_aspect_btn.clicked.connect(self._on_apply_aspect)
        self.apply_golden_btn.clicked.connect(self._on_apply_golden)
        self.safe_frame_checkbox.toggled.connect(self._on_safe_frame_toggled)
        # Framing — guides (checkbox + color combo + swatch per guide)
        _guide_keys = ('thirds', 'golden', 'center', 'diag', 'triangle', 'spiral')
        for _key in _guide_keys:
            chk   = getattr(self, f'guide_{_key}_checkbox')
            combo = getattr(self, f'guide_{_key}_color_combo')
            swatch= getattr(self, f'guide_{_key}_swatch')
            chk.toggled.connect(self._make_guide_toggle(_key))
            combo.currentIndexChanged.connect(self._make_color_combo_handler(_key))
            swatch.clicked.connect(self._make_swatch_handler(_key))
        # Bookmarks
        self.save_bookmark_btn.clicked.connect(self._on_save_bookmark)
        self.apply_bookmark_btn.clicked.connect(self._on_apply_bookmark)
        self.delete_bookmark_btn.clicked.connect(self._on_delete_bookmark)
        # Orbit / Arc
        self.create_orbit_btn.clicked.connect(self._on_create_orbit)
        self.restore_line_btn.clicked.connect(self._on_restore_line_track)
        # Bake Easing
        self.bake_dolly_btn.clicked.connect(self._on_bake_dolly)
        # Steadicam
        self.steadicam_checkbox.toggled.connect(self._on_steadicam_toggled)
        self.steadicam_tension_row.valueChanged.connect(lambda _: self._on_steadicam_params_changed())
        self.steadicam_drag_row.valueChanged.connect(lambda _: self._on_steadicam_params_changed())
        self.steadicam_recalc_btn.clicked.connect(self._on_steadicam_recalc)
        # Camera Shake
        self.shake_checkbox.toggled.connect(self._on_shake_toggled)
        self.shake_frequency_row.valueChanged.connect(lambda _: self._on_shake_params_changed())
        self.shake_strength_x_row.valueChanged.connect(lambda _: self._on_shake_params_changed())
        self.shake_strength_y_row.valueChanged.connect(lambda _: self._on_shake_params_changed())
        self.shake_strength_z_row.valueChanged.connect(lambda _: self._on_shake_params_changed())
        self.shake_seed_spin.valueChanged.connect(lambda _: self._on_shake_seed_changed())
        self.shake_randomize_btn.clicked.connect(self._on_shake_randomize)
        # Rack Focus / Picker
        self.pick_focus_btn.clicked.connect(self._on_pick_focus_subject)
        self.bake_rack_btn.clicked.connect(self._on_bake_rack_focus)
        # Vertigo
        self.bake_vertigo_btn.clicked.connect(self._on_bake_vertigo)
        self.vertigo_subject_dist_row.valueChanged.connect(lambda _: self._update_vertigo_preview())
        self.vertigo_dolly_end_row.valueChanged.connect(lambda _: self._update_vertigo_preview())

    # ------------------------------------------------------------------
    # Controls enable/disable
    # ------------------------------------------------------------------

    def _set_controls_enabled(self, enabled):
        for i in range(1, self.tabs.count()):
            self.tabs.setTabEnabled(i, enabled)
        self.reset_all_btn.setEnabled(enabled)
        self.toggle_helpers_btn.setEnabled(enabled)
        self.lookat_checkbox.setEnabled(enabled)

    def _on_log_positions(self):
        """Print all rig node world positions to the Max listener for debugging."""
        if not self.rig_nodes:
            print("[CameraRig] No rig loaded.")
            return
        from camera_rig.core.rig_builder import log_rig_positions
        print(log_rig_positions(self.rig_nodes))

    # ------------------------------------------------------------------
    # Camera Selection
    # ------------------------------------------------------------------

    def _on_camera_selection_changed(self, index):
        camera = self.camera_combo.itemData(index)
        if not (camera and rt.isValidNode(camera)):
            self._set_controls_enabled(False)
            self.install_rig_btn.setText("Install Rig")
            self.install_rig_btn.setEnabled(False)
            self.rig_nodes = {}
            return

        self.selected_camera = camera
        rig_root = rt.getNodeByName(f"RIG_{camera.name}_DOLLY_CTRL")

        if rig_root and rt.isValidNode(rig_root):
            self.install_rig_btn.setText("Rig Installed")
            self.install_rig_btn.setEnabled(False)
            self._load_rig(camera)
            self._set_controls_enabled(True)
        else:
            self.install_rig_btn.setText("Install Rig")
            self.install_rig_btn.setEnabled(True)
            self.rig_nodes = {}
            self._set_controls_enabled(False)

    def _populate_camera_list(self):
        self.camera_combo.blockSignals(True)
        self.camera_combo.clear()
        scene_cameras = [obj for obj in rt.objects if rt.isKindOf(obj, rt.Camera)]
        if not scene_cameras:
            self.camera_combo.addItem("No cams!")
            self.install_rig_btn.setEnabled(False)
            self.camera_combo.blockSignals(False)
            return
        for cam in scene_cameras:
            self.camera_combo.addItem(cam.name, userData=cam)
        self.camera_combo.blockSignals(False)
        self._on_camera_selection_changed(self.camera_combo.currentIndex())

    # ------------------------------------------------------------------
    # Rig Install / Load
    # ------------------------------------------------------------------

    def _install_rig(self):
        self.selected_camera = self.camera_combo.currentData()
        if not (self.selected_camera and rt.isValidNode(self.selected_camera)):
            QMessageBox.warning(self, "Warning", "Please select a valid camera from the list.")
            return

        cam = self.selected_camera
        cam_name = cam.name

        # ── PRE-INSTALL LOG ──────────────────────────────────────────
        def fmt(val):
            return f"{float(val):.3f}"

        def fmtpos(pos):
            return f"({fmt(pos.x)}, {fmt(pos.y)}, {fmt(pos.z)})"

        print("=" * 60)
        print(f"[RIG] Installing on: {cam_name}")
        unit_type = rt.execute('units.SystemType as string')
        print(f"[SCN] system units = {unit_type}")
        print(f"[CAM] pos          = {fmtpos(cam.pos)}")
        print(f"[CAM] dir          = ({cam.dir.x:.3f}, {cam.dir.y:.3f}, {cam.dir.z:.3f})")
        try:
            print(f"[CAM] lens         = {cam.lens:.1f} mm")
        except Exception:
            pass
        has_target = (rt.isProperty(cam, 'target') and cam.target and rt.isValidNode(cam.target))
        if has_target:
            t = cam.target
            print(f"[CAM] target       = {t.name}  pos={fmtpos(t.pos)}")
        else:
            print(f"[CAM] target       = None (Free Camera)")
        print(f"[CAM] track_len    = {fmt(self.track_length_spinbox.value())}")
        print("-" * 60)

        rig_builder.cleanup_old_rig(cam_name)

        track_length  = self.track_length_spinbox.value()
        crane_height  = self.crane_height_spinbox.value()
        self.rig_nodes = rig_builder.install_camera_rig(cam, track_length, crane_height)
        self.path_constraint_controller = self.rig_nodes.pop('_path_ctrl', None)
        self._initial_arm_z = self.rig_nodes.pop('_initial_arm_z', 100.0)

        # ── POST-INSTALL LOG ─────────────────────────────────────────
        print("[RIG] Nodes created:")
        key_order = ['dolly', 'crane_base', 'crane_arm', 'master', 'pivot', 'target', 'track']
        for key in key_order:
            node = self.rig_nodes.get(key)
            if node and rt.isValidNode(node):
                parent_name = node.parent.name if node.parent else "None"
                print(f"  {key:<12s}  {node.name:<40s}  pos={fmtpos(node.pos)}  parent={parent_name}")
            else:
                print(f"  {key:<12s}  NOT FOUND")
        print(f"[RIG] initial_arm_z = {fmt(self._initial_arm_z)}")
        print("=" * 60)

        positions = rig_builder.capture_initial_positions(self.rig_nodes, cam)
        self.initial_target_local_pos      = positions.get('target_local_pos')
        self.initial_target_world_pos      = positions.get('target_world_pos')
        self.initial_target_world_x        = positions.get('target_world_x', 0.0)
        self.initial_target_world_y        = positions.get('target_world_y', 0.0)
        self.initial_target_world_z        = positions.get('target_world_z', 0.0)
        self.initial_crane_base_world_pos  = positions.get('crane_base_world_pos')
        self.initial_crane_base_local_pos  = positions.get('crane_base_local_pos')
        self.initial_crane_base_world_z    = positions.get('crane_base_world_z')
        self.initial_master_world_pos      = positions.get('master_world_pos')
        self.initial_master_rot            = positions.get('master_rot')

        # Sync dolly slider to 50% (center of track)
        self.dolly_slider.blockSignals(True)
        self.dolly_slider.setValue(500)
        self.dolly_slider.blockSignals(False)
        self.dolly_percent_label.setText("50.0%")

        QMessageBox.information(self, "Success", "Rig installed successfully!")
        self._on_camera_selection_changed(self.camera_combo.currentIndex())

        # ── POST-CONSTRAINT LOG — force MXS evaluation ──────────────
        rt.redrawViews()
        print("[RIG] Final world positions:")
        key_order = ['dolly', 'crane_base', 'crane_arm', 'master', 'pivot', 'target', 'track']
        for key in key_order:
            node = self.rig_nodes.get(key)
            if node and rt.isValidNode(node):
                rt.py_log_node = node
                pos = rt.execute('at time currentTime py_log_node.pos')
                rt.py_log_node = rt.undefined
                if pos:
                    parent_name = node.parent.name if node.parent else "None"
                    print(f"  {key:<12s}  pos={fmtpos(pos)}  parent={parent_name}")
        rt.py_log_cam = cam
        cam_pos_eval = rt.execute('at time currentTime py_log_cam.pos')
        rt.py_log_cam = rt.undefined
        if cam_pos_eval:
            print(f"[CAM] final pos = {fmtpos(cam_pos_eval)}")
        print("=" * 60)

    def _load_rig(self, camera):
        self.rig_nodes = rig_builder.load_existing_rig(camera)
        self.path_constraint_controller = self.rig_nodes.pop('_path_ctrl', None)

        positions = rig_builder.capture_initial_positions(self.rig_nodes, camera)
        self.initial_target_local_pos      = positions.get('target_local_pos')
        self.initial_target_world_pos      = positions.get('target_world_pos')
        self.initial_target_world_x        = positions.get('target_world_x', 0.0)
        self.initial_target_world_y        = positions.get('target_world_y', 0.0)
        self.initial_target_world_z        = positions.get('target_world_z', 0.0)
        self.initial_crane_base_world_pos  = positions.get('crane_base_world_pos')
        self.initial_crane_base_local_pos  = positions.get('crane_base_local_pos')
        self.initial_crane_base_world_z    = positions.get('crane_base_world_z')
        self.initial_master_world_pos      = positions.get('master_world_pos')
        self.initial_master_rot            = positions.get('master_rot')
        self._initial_arm_z = positions.get('arm_z', 100.0)

        self._sync_ui_to_rig()

    # ------------------------------------------------------------------
    # Sync UI ← Rig State
    # ------------------------------------------------------------------

    def _sync_ui_to_rig(self):
        rows = [self.truck_row, self.pedestal_row, self.pan_row, self.tilt_row, self.roll_row, self.arm_reach_row]
        sliders = [self.dolly_slider, self.crane_arm_slider, self.crane_base_slider]
        for r in rows:
            r.blockAll(True)
        for s in sliders:
            s.blockSignals(True)

        try:
            state = rig_utils.read_rig_state(self.rig_nodes, self.selected_camera)

            if 'dolly_percent' in state and state['dolly_percent'] is not None:
                pct = float(state['dolly_percent'])
                self.dolly_slider.setValue(int(pct * 10))
                self.dolly_percent_label.setText(f"{pct:.1f}%")
            if 'crane_arm_angle' in state and state['crane_arm_angle'] is not None:
                self.crane_arm_slider.setValue(int(state['crane_arm_angle'] * 10))
            if 'crane_base_angle' in state and state['crane_base_angle'] is not None:
                self.crane_base_slider.setValue(int(state['crane_base_angle'] * 10))
            if 'arm_z' in state:
                self.arm_reach_row.value = state['arm_z']
            if 'roll' in state and state['roll'] is not None:
                self.roll_row.value = float(state['roll'])
            if 'focal_length' in state:
                self.focal_row.value = state['focal_length']
                self.fov_label.setText(f"{rig_utils.focal_to_fov(state['focal_length']):.1f}°")
            if 'near_clip' in state:
                self.near_clip_spin.setValue(state['near_clip'])
            if 'far_clip' in state:
                self.far_clip_spin.setValue(state['far_clip'])
            if 'dof_enabled' in state:
                self.dof_checkbox.setChecked(state['dof_enabled'])
            if 'focus_dist' in state:
                self.focus_dist_row.blockAll(True)
                self.focus_dist_row.value = state['focus_dist']
                self.focus_dist_row.blockAll(False)

            self.current_aspect_label.setText(get_current_aspect())

        except Exception as e:
            log.warning("Error syncing UI to rig: %s", e)
        finally:
            for r in rows:
                r.blockAll(False)
            for s in sliders:
                s.blockSignals(False)

    # ------------------------------------------------------------------
    # Dolly Handlers
    # ------------------------------------------------------------------

    def _on_dolly_slider_changed(self, value):
        self.dolly_percent_label.setText(f"{value / 10.0:.1f}%")

    def _on_dolly_slider_released(self):
        percent = self.dolly_slider.value() / 10.0
        rig_controls.update_dolly_scene(self.path_constraint_controller, self.rig_nodes, percent)

    # ------------------------------------------------------------------
    # Track length update + Flow/Bank
    # ------------------------------------------------------------------

    def _on_update_track_length(self):
        """Resize the straight track in local space of TRACK_CTRL (pivot stays fixed)."""
        track = self.rig_nodes.get('track')
        if not (track and rt.isValidNode(track)):
            return
        new_len = self.track_length_spinbox.value()
        half    = new_len / 2.0
        rt.py_track = track
        rt.py_half  = half
        rt.execute("""
        (
            -- resize in local space — pivot stays at track_ctrl center
            in coordSys py_track.parent (
                setKnotPoint py_track 1 1 [-py_half, 0, 0]
                setKnotPoint py_track 1 2 [ py_half, 0, 0]
            )
            updateShape py_track
        )
        """)
        rt.py_track = rt.py_half = rt.undefined
        rt.redrawViews()

    def _on_update_orbit_radius(self):
        """Update the orbit circle track radius in the scene."""
        orbit = self.rig_nodes.get('orbit_track')
        if not (orbit and rt.isValidNode(orbit)):
            return
        new_radius = self.orbit_radius_spin.value()
        rt.py_orbit  = orbit
        rt.py_radius = new_radius
        rt.execute('try(py_orbit.radius = py_radius)catch(donothing); py_orbit=undefined; py_radius=undefined;')
        rt.redrawViews()

    def _on_follow_path_toggled(self, checked: bool):
        self.bank_checkbox.setEnabled(checked)
        if not checked:
            self.bank_amount_spin.setEnabled(False)
        if self.path_constraint_controller:
            self._apply_path_options(self.path_constraint_controller)

    def _on_bank_toggled(self, checked: bool):
        self.bank_amount_spin.setEnabled(
            checked and self.follow_path_checkbox.isChecked())
        if self.path_constraint_controller:
            self._apply_path_options(self.path_constraint_controller)

    def _on_bank_amount_changed(self, value: float):
        if self.path_constraint_controller:
            self._apply_path_options(self.path_constraint_controller)

    # ------------------------------------------------------------------
    # Crane Handlers
    # ------------------------------------------------------------------

    def _on_crane_arm_changed(self, value):
        self.crane_arm_label.setText(f"{value / 10.0:.1f}°")

    def _on_crane_arm_released(self):
        angle = float(self.crane_arm_slider.value()) / 10.0
        rig_controls.update_crane_arm(self.rig_nodes, angle)

    def _on_crane_base_changed(self, value):
        self.crane_base_label.setText(f"{value / 10.0:.1f}°")

    def _on_crane_base_released(self):
        angle = float(self.crane_base_slider.value()) / 10.0
        rig_controls.update_crane_base(self.rig_nodes, angle)

    def _on_arm_reach_changed(self):
        rig_controls.update_arm_reach(self.rig_nodes, self.arm_reach_row.value)

    # ------------------------------------------------------------------
    # Direct Control Handlers
    # ------------------------------------------------------------------

    def _on_truck_changed(self):
        rx, ry = self._cam_right_vector()
        rig_controls.update_truck(
            self.rig_nodes, self.truck_row.value,
            self.initial_crane_base_world_pos, self.lock_target_checkbox.isChecked(),
            cam_right_x=rx, cam_right_y=ry,
        )

    def _on_pedestal_changed(self):
        rig_controls.update_pedestal(
            self.rig_nodes, self.pedestal_row.value,
            self.initial_crane_base_world_z, self.lock_target_checkbox.isChecked()
        )

    def _on_pan_changed(self):
        if self.orbit_mode_checkbox.isChecked():
            rig_controls.update_pan_orbit(self.rig_nodes, self.pan_row.value)
        else:
            rx, ry = self._cam_right_vector()
            rig_controls.update_target_pan(
                self.rig_nodes, self.pan_row.value,
                self.initial_target_world_x,
                self.initial_target_world_y,
                cam_right_x=rx, cam_right_y=ry,
            )

    def _on_tilt_changed(self):
        if self.orbit_mode_checkbox.isChecked():
            rig_controls.update_tilt_orbit(self.rig_nodes, self.tilt_row.value)
        else:
            rig_controls.update_target_tilt(
                self.rig_nodes, self.tilt_row.value, self.initial_target_world_z
            )

    def _on_roll_changed(self):
        rig_controls.update_roll(self.rig_nodes, self.roll_row.value)

    def _cam_right_vector(self):
        """Return (rx, ry) — camera right vector projected on XY plane, normalized."""
        cam = self.selected_camera
        if cam and rt.isValidNode(cam):
            rt.py_cam = cam
            row1 = rt.execute('py_cam.transform.row1')  # camera local X = right
            rt.py_cam = rt.undefined
            if row1:
                import math
                length = math.sqrt(row1.x ** 2 + row1.y ** 2)
                if length > 0.001:
                    return row1.x / length, row1.y / length
        return 1.0, 0.0

    def _on_orbit_mode_changed(self, checked: bool):
        # Reset pan/tilt sliders when switching mode to avoid jump
        for row in (self.pan_row, self.tilt_row):
            row.blockAll(True)
            row.value = 0.0
            row.blockAll(False)
        if checked:
            self.aim_mode_label.setText("Mode: Orbit  —  target rotates around camera")
            self.pan_row._spin.setSuffix("°")
            self.tilt_row._spin.setSuffix("°")
        else:
            self.aim_mode_label.setText("Mode: Linear  —  target moves on straight line")
            self.pan_row._spin.setSuffix(" u")
            self.tilt_row._spin.setSuffix(" u")

    # ------------------------------------------------------------------
    # Setup Handlers
    # ------------------------------------------------------------------

    def _toggle_helpers(self):
        is_hidden = rig_utils.toggle_helpers_visibility(self.rig_nodes)
        self.toggle_helpers_btn.setText("Show Rig Helpers" if is_hidden else "Hide Rig Helpers")

    def _on_lookat_toggled(self, checked):
        weight = 100 if checked else 0
        rig_utils.set_lookat_weight(self.rig_nodes, weight)

    # ------------------------------------------------------------------
    # Lens Handlers
    # ------------------------------------------------------------------

    def _on_log_cam_props(self):
        """Print all detected camera properties to Max Listener."""
        cam = self.selected_camera
        if not (cam and rt.isValidNode(cam)):
            print("[Lens] No camera selected.")
            return
        info = lens_controls.get_camera_info(cam)
        print(f"[Lens] Camera: {cam.name}  type={info['type']}")
        for k, v in info.items():
            if k != 'type':
                print(f"  {k:<20s} = {v}")

    def _on_focal_changed(self):
        fl = self.focal_row.value
        lens_controls.update_focal_length(self.selected_camera, fl)
        self.fov_label.setText(f"{rig_utils.focal_to_fov(fl):.1f}°")

    def _on_clipping_changed(self):
        lens_controls.update_clipping(
            self.selected_camera, self.near_clip_spin.value(), self.far_clip_spin.value()
        )

    def _on_dof_toggled(self, checked):
        lens_controls.update_dof(self.selected_camera, checked)
        self.focus_dist_row.setEnabled(checked)

    def _on_focus_dist_changed(self):
        lens_controls.update_dof_distance(self.selected_camera, self.focus_dist_row.value)

    # ------------------------------------------------------------------
    # Framing Handlers
    # ------------------------------------------------------------------

    # ── Framing helpers ────────────────────────────────────────────────

    _COLOR_VALUES = {
        "White":  (255, 255, 255), "Yellow": (255, 220,   0),
        "Orange": (255, 140,   0), "Red":    (220,  50,  50),
        "Green":  (  0, 220,  80), "Cyan":   (  0, 200, 220),
        "Blue":   ( 60, 100, 255), "Purple": (180, 100, 255),
    }

    def _apply_aspect_by_name(self, name: str):
        if name in ASPECT_PRESETS:
            w, h = ASPECT_PRESETS[name]
            set_aspect_ratio(w, h)
            set_safe_frame(True)
            self.safe_frame_checkbox.blockSignals(True)
            self.safe_frame_checkbox.setChecked(True)
            self.safe_frame_checkbox.blockSignals(False)
            self.current_aspect_label.setText(get_current_aspect())

    def _on_apply_aspect(self):
        self._apply_aspect_by_name(self.aspect_combo.currentText())

    def _on_apply_golden(self):
        self._apply_aspect_by_name(self.golden_combo.currentText())

    def _on_safe_frame_toggled(self, checked):
        set_safe_frame(checked)

    def _make_guide_toggle(self, key: str):
        def handler(checked: bool):
            if checked:
                install_overlay()
            kwargs = {key: checked}
            set_guide(**kwargs)
            if not any_guide_active():
                uninstall_overlay()
        return handler

    def _make_color_combo_handler(self, key: str):
        def handler(index: int):
            combo  = getattr(self, f'guide_{key}_color_combo')
            swatch = getattr(self, f'guide_{key}_swatch')
            name   = combo.currentText()
            if name == "Custom":
                return
            r, g, b = self._COLOR_VALUES.get(name, (255, 255, 255))
            self._guide_colors[key] = [r, g, b]
            from camera_rig.ui.tabs.framing_tab import _make_color_swatch
            swatch.setStyleSheet(_make_color_swatch(r, g, b))
            swatch.setToolTip(f"Current: rgb({r},{g},{b})")
            set_guide_color(key, r, g, b)
        return handler

    def _make_swatch_handler(self, key: str):
        def handler():
            from PySide6.QtWidgets import QColorDialog
            cur = self._guide_colors.get(key, [255, 255, 255])
            from PySide6.QtGui import QColor
            initial = QColor(cur[0], cur[1], cur[2])
            col = QColorDialog.getColor(initial, self, f"Guide Color — {key}")
            if not col.isValid():
                return
            r, g, b = col.red(), col.green(), col.blue()
            self._guide_colors[key] = [r, g, b]
            swatch = getattr(self, f'guide_{key}_swatch')
            from camera_rig.ui.tabs.framing_tab import _make_color_swatch
            swatch.setStyleSheet(_make_color_swatch(r, g, b))
            swatch.setToolTip(f"Current: rgb({r},{g},{b})")
            combo = getattr(self, f'guide_{key}_color_combo')
            combo.blockSignals(True)
            combo.setCurrentIndex(0)   # "Custom"
            combo.blockSignals(False)
            set_guide_color(key, r, g, b)
        return handler

    @property
    def _guide_colors(self):
        if not hasattr(self, '_guide_colors_store'):
            self._guide_colors_store = {k: list(v) for k, v in GUIDE_DEFAULTS.items()}
        return self._guide_colors_store

    # ------------------------------------------------------------------
    # Bookmark Handlers
    # ------------------------------------------------------------------

    def _on_save_bookmark(self):
        name = self.bookmark_name_edit.text().strip()
        if not name:
            name = f"Shot {len(self._bookmarks) + 1}"
        cam = self.selected_camera
        if not (cam and rt.isValidNode(cam)):
            return
        bm = save_bookmark(cam, self.rig_nodes, name)
        self._bookmarks.append(bm)
        self.bookmarks_list.addItem(bm.name)
        self.bookmark_name_edit.clear()

    def _on_apply_bookmark(self):
        idx = self.bookmarks_list.currentRow()
        if idx < 0 or idx >= len(self._bookmarks):
            return
        bm = self._bookmarks[idx]
        apply_bookmark(self.selected_camera, self.rig_nodes, bm)
        self._sync_ui_to_rig()

    def _on_delete_bookmark(self):
        idx = self.bookmarks_list.currentRow()
        if idx < 0 or idx >= len(self._bookmarks):
            return
        self._bookmarks.pop(idx)
        self.bookmarks_list.takeItem(idx)

    # ------------------------------------------------------------------
    # Reset Methods
    # ------------------------------------------------------------------

    def _reset_all(self):
        self._reset_dolly()
        self._reset_crane()
        self._reset_direct()
        self._reset_lens()
        # disable shake
        if self.shake_checkbox.isChecked():
            self.shake_checkbox.blockSignals(True)
            self.shake_checkbox.setChecked(False)
            self.shake_checkbox.blockSignals(False)
            camera_shake.remove_shake(self.rig_nodes)
        rt.redrawViews()

    def _reset_dolly(self):
        rig_controls.reset_dolly(self.path_constraint_controller, self.rig_nodes)
        self.dolly_slider.blockSignals(True)
        self.dolly_slider.setValue(0)
        self.dolly_slider.blockSignals(False)
        self.dolly_percent_label.setText("0.0%")

    def _reset_crane(self):
        rig_controls.reset_crane(self.rig_nodes, self._initial_arm_z)
        self.crane_arm_slider.blockSignals(True)
        self.crane_arm_slider.setValue(0)
        self.crane_arm_slider.blockSignals(False)
        self.crane_arm_label.setText("0.0°")
        self.crane_base_slider.blockSignals(True)
        self.crane_base_slider.setValue(0)
        self.crane_base_slider.blockSignals(False)
        self.crane_base_label.setText("0.0°")
        self.arm_reach_row.blockAll(True)
        self.arm_reach_row.value = self._initial_arm_z
        self.arm_reach_row.blockAll(False)

    def _reset_direct(self):
        # ── LOG BEFORE RESET ─────────────────────────────────────────
        print("=" * 50)
        print("[RESET DIRECT] BEFORE:")
        for key in ('crane_base', 'master', 'pivot', 'target'):
            node = self.rig_nodes.get(key)
            if node and rt.isValidNode(node):
                p = node.pos
                r = node.rotation
                print(f"  {key:<12s}  pos=({p.x:.3f}, {p.y:.3f}, {p.z:.3f})  rot=({r.x:.3f}, {r.y:.3f}, {r.z:.3f}, {r.w:.3f})")
        cam = self.selected_camera
        if cam and rt.isValidNode(cam):
            p = cam.pos
            print(f"  {'camera':<12s}  pos=({p.x:.3f}, {p.y:.3f}, {p.z:.3f})")
        print(f"  initial_target_world_pos     = {self.initial_target_world_pos}")
        print(f"  initial_crane_base_world_pos = {self.initial_crane_base_world_pos}")
        print("-" * 50)

        for row in (self.truck_row, self.pedestal_row, self.pan_row, self.tilt_row, self.roll_row):
            row.blockAll(True)
            row.value = 0.0
            row.blockAll(False)
        self.lock_target_checkbox.setChecked(False)
        rig_controls.reset_direct_controls(
            self.rig_nodes,
            initial_target_world_pos=self.initial_target_world_pos,
            initial_crane_base_world_pos=self.initial_crane_base_world_pos,
            initial_master_world_pos=self.initial_master_world_pos,
            initial_master_rot=self.initial_master_rot,
        )

        # ── LOG AFTER RESET ──────────────────────────────────────────
        rt.redrawViews()
        print("[RESET DIRECT] AFTER:")
        for key in ('crane_base', 'master', 'pivot', 'target'):
            node = self.rig_nodes.get(key)
            if node and rt.isValidNode(node):
                p = node.pos
                r = node.rotation
                print(f"  {key:<12s}  pos=({p.x:.3f}, {p.y:.3f}, {p.z:.3f})  rot=({r.x:.3f}, {r.y:.3f}, {r.z:.3f}, {r.w:.3f})")
        if cam and rt.isValidNode(cam):
            p = cam.pos
            print(f"  {'camera':<12s}  pos=({p.x:.3f}, {p.y:.3f}, {p.z:.3f})")
        print("=" * 50)

    def _reset_lens(self):
        cam = self.selected_camera
        lens_controls.reset_lens(cam)
        # Read back what was actually set — works for all camera types
        info = lens_controls.get_camera_info(cam) if cam and rt.isValidNode(cam) else {}

        fl = info.get('focal_length', 35.0) or 35.0
        self.focal_row.blockAll(True)
        self.focal_row.value = fl
        self.focal_row.blockAll(False)
        self.fov_label.setText(f"{rig_utils.focal_to_fov(fl):.1f}°")

        near = info.get('near_clip', 1.0) or 1.0
        self.near_clip_spin.blockSignals(True)
        self.near_clip_spin.setValue(near)
        self.near_clip_spin.blockSignals(False)

        far = info.get('far_clip', 10000.0) or 10000.0
        self.far_clip_spin.blockSignals(True)
        self.far_clip_spin.setValue(far)
        self.far_clip_spin.blockSignals(False)

        self.dof_checkbox.blockSignals(True)
        self.dof_checkbox.setChecked(False)
        self.dof_checkbox.blockSignals(False)

        self.focus_dist_row.blockAll(True)
        self.focus_dist_row.value = info.get('focus_dist', 300.0) or 300.0
        self.focus_dist_row.blockAll(False)

    # ------------------------------------------------------------------
    # Orbit / Arc Shot
    # ------------------------------------------------------------------

    def _on_create_orbit(self):
        if not self.selected_camera or not self.rig_nodes:
            return
        cam_name = self.selected_camera.name
        target = self.rig_nodes.get('target')
        if target and rt.isValidNode(target):
            center = target.pos
        else:
            center = self.rig_nodes['dolly'].pos
        radius = self.orbit_radius_spin.value()
        circle = rig_builder.create_orbit_track(cam_name, center, radius)
        self.rig_nodes['orbit_track'] = circle
        self._assign_orbit_path(circle)
        self.orbit_mode_label.setText("Mode: Orbit")

    def _on_restore_line_track(self):
        track = self.rig_nodes.get('track')
        if not track:
            return
        self._assign_orbit_path(track)
        self.orbit_mode_label.setText("Mode: Straight")

    def _assign_orbit_path(self, path_node):
        """Assign any spline node as the dolly path (reusable for both orbit and straight)."""
        dolly = self.rig_nodes.get('dolly')
        if not (dolly and rt.isValidNode(dolly)):
            return
        path_ctrl = rt.Path_Constraint()
        path_ctrl.path = path_node
        rt.py_dolly_node = dolly
        rt.py_path_ctrl = path_ctrl
        rt.execute('py_dolly_node.pos.controller = py_path_ctrl; py_dolly_node=undefined; py_path_ctrl=undefined;')
        self.path_constraint_controller = path_ctrl
        self.dolly_slider.blockSignals(True)
        self.dolly_slider.setValue(0)
        self.dolly_slider.blockSignals(False)
        self.dolly_percent_label.setText("0.0%")

    # ------------------------------------------------------------------
    # Bake Easing
    # ------------------------------------------------------------------

    _TANGENT_MAP = {
        "Ease (Slow)": "slow",
        "Linear":      "linear",
        "Fast":        "fast",
        "Smooth":      "smooth",
    }

    def _on_bake_dolly(self):
        if not self.path_constraint_controller:
            return
        tangent = self._TANGENT_MAP.get(self.ease_tangent_combo.currentText(), "slow")
        rig_controls.bake_dolly_easing(
            self.path_constraint_controller,
            int(self.ease_start_frame.value()),
            int(self.ease_end_frame.value()),
            float(self.ease_start_pct.value()),
            float(self.ease_end_pct.value()),
            self.ease_in_checkbox.isChecked(),
            self.ease_out_checkbox.isChecked(),
            tangent_type=tangent,
        )
        # Sync slider to end percent
        self.dolly_slider.blockSignals(True)
        self.dolly_slider.setValue(int(self.ease_end_pct.value() * 10))
        self.dolly_slider.blockSignals(False)
        self.dolly_percent_label.setText(f"{self.ease_end_pct.value():.1f}%")

    # ------------------------------------------------------------------
    # Steadicam
    # ------------------------------------------------------------------

    def _on_steadicam_toggled(self, checked):
        if not self.selected_camera or not self.rig_nodes:
            return
        cam_name = self.selected_camera.name
        if checked:
            steadicam_mod.install_steadicam(
                self.rig_nodes, cam_name,
                tension=self.steadicam_tension_row.value,
                drag=self.steadicam_drag_row.value,
            )
        else:
            steadicam_mod.remove_steadicam(self.rig_nodes)

    def _on_steadicam_params_changed(self):
        steadicam_mod.update_steadicam(
            self.rig_nodes,
            self.steadicam_tension_row.value,
            self.steadicam_drag_row.value,
        )

    def _on_steadicam_recalc(self):
        steadicam_mod.recalculate_steadicam(self.rig_nodes)

    # ------------------------------------------------------------------
    # Camera Shake
    # ------------------------------------------------------------------

    def _on_shake_toggled(self, checked: bool):
        if not self.rig_nodes:
            return
        if checked:
            camera_shake.install_shake(
                self.rig_nodes,
                frequency=self.shake_frequency_row.value,
                strength_x=self.shake_strength_x_row.value,
                strength_y=self.shake_strength_y_row.value,
                strength_z=self.shake_strength_z_row.value,
                seed=int(self.shake_seed_spin.value()),
            )
        else:
            camera_shake.remove_shake(self.rig_nodes)

    def _on_shake_params_changed(self):
        if not (self.rig_nodes and self.shake_checkbox.isChecked()):
            return
        camera_shake.update_shake(
            self.rig_nodes,
            frequency=self.shake_frequency_row.value,
            strength_x=self.shake_strength_x_row.value,
            strength_y=self.shake_strength_y_row.value,
            strength_z=self.shake_strength_z_row.value,
        )

    def _on_shake_seed_changed(self):
        if not (self.rig_nodes and self.shake_checkbox.isChecked()):
            return
        camera_shake.set_shake_seed(self.rig_nodes, int(self.shake_seed_spin.value()))

    def _on_shake_randomize(self):
        import random
        new_seed = random.randint(0, 9999)
        self.shake_seed_spin.blockSignals(True)
        self.shake_seed_spin.setValue(new_seed)
        self.shake_seed_spin.blockSignals(False)
        if self.rig_nodes and self.shake_checkbox.isChecked():
            camera_shake.set_shake_seed(self.rig_nodes, new_seed)

    # ------------------------------------------------------------------
    # Focus Subject Picker & Rack Focus
    # ------------------------------------------------------------------

    def _on_pick_focus_subject(self):
        cam = self.selected_camera
        if not (cam and rt.isValidNode(cam)):
            return
        dist = rack_focus.pick_focus_subject(cam)
        if dist is None:
            return
        self.focus_dist_row.blockAll(True)
        self.focus_dist_row.value = dist
        self.focus_dist_row.blockAll(False)
        from camera_rig.core import lens_controls
        lens_controls.update_dof_distance(cam, dist)
        rt.redrawViews()

    def _on_bake_rack_focus(self):
        cam = self.selected_camera
        if not (cam and rt.isValidNode(cam)):
            return
        tangent = self._TANGENT_MAP.get(self.rack_tangent_combo.currentText(), "slow")
        rack_focus.bake_rack_focus(
            cam,
            from_dist=self.rack_from_row.value,
            to_dist=self.rack_to_row.value,
            frame_start=int(self.rack_start_frame.value()),
            frame_end=int(self.rack_end_frame.value()),
            ease_in=self.rack_ease_in.isChecked(),
            ease_out=self.rack_ease_out.isChecked(),
            tangent_type=tangent,
        )

    # ------------------------------------------------------------------
    # Vertigo Effect
    # ------------------------------------------------------------------

    def _update_vertigo_preview(self):
        cam = self.selected_camera
        if not (cam and rt.isValidNode(cam)):
            return
        try:
            from camera_rig.core.rig_utils import focal_to_fov
            focal = float(cam.lens) if rt.isProperty(cam, 'lens') else 35.0
            subj_dist = self.vertigo_subject_dist_row.value
            end_pct   = self.vertigo_dolly_end_row.value
            start_pct = self.vertigo_dolly_start_row.value
            dolly_offset = (end_pct - start_pct) * 10.0
            result = vertigo_mod.preview_vertigo(focal, subj_dist, dolly_offset)
            self.vertigo_fov_label.setText(f"Current FOV: {focal_to_fov(focal):.1f}°")
            self.vertigo_focal_end_label.setText(f"Required Focal at End: {result['focal_at_end']:.1f} mm")
        except Exception:
            pass

    def _on_bake_vertigo(self):
        cam = self.selected_camera
        if not (cam and rt.isValidNode(cam)):
            return
        if not self.path_constraint_controller:
            return
        direction = "push_in" if self.vertigo_direction_combo.currentIndex() == 1 else "pull_out"
        vertigo_mod.bake_vertigo(
            cam,
            self.path_constraint_controller,
            subject_dist=self.vertigo_subject_dist_row.value,
            dolly_start_pct=self.vertigo_dolly_start_row.value,
            dolly_end_pct=self.vertigo_dolly_end_row.value,
            frame_start=int(self.vertigo_start_frame.value()),
            frame_end=int(self.vertigo_end_frame.value()),
            direction=direction,
        )

    # ------------------------------------------------------------------
    # Path Assignment
    # ------------------------------------------------------------------

    def _populate_path_list(self):
        self.path_combo.clear()
        # Filter out rig helpers (RIG_ prefix) — show only user-created paths
        scene_paths = [
            obj for obj in rt.objects
            if rt.isKindOf(obj, rt.Shape)
            and not str(obj.name).startswith("RIG_")
        ]
        if not scene_paths:
            self.path_combo.addItem("No paths!")
            return
        for path in scene_paths:
            self.path_combo.addItem(path.name, userData=path)

    def _assign_path(self):
        dolly_ctrl = self.rig_nodes.get('dolly')
        if not (self.path_constraint_controller and rt.isValidNode(dolly_ctrl)):
            QMessageBox.warning(self, "Warning", "Install a rig first.")
            return
        selected_path = self.path_combo.currentData()
        if not selected_path:
            QMessageBox.warning(self, "Warning", "Select a valid path.")
            return
        path_ctrl = rt.Path_Constraint()
        path_ctrl.path = selected_path
        # Apply flow/bank settings from UI
        self._apply_path_options(path_ctrl)
        rt.py_dolly_node = dolly_ctrl
        rt.py_path_ctrl  = path_ctrl
        rt.execute('py_dolly_node.pos.controller = py_path_ctrl; py_dolly_node=undefined; py_path_ctrl=undefined;')
        self.path_constraint_controller = path_ctrl
        self.dolly_slider.blockSignals(True)
        self.dolly_slider.setValue(0)
        self.dolly_slider.blockSignals(False)
        self.dolly_percent_label.setText("0.0%")

    def _apply_path_options(self, path_ctrl):
        """Apply follow/bank settings to a Path_Constraint from the UI checkboxes."""
        follow = self.follow_path_checkbox.isChecked()
        bank   = self.bank_checkbox.isChecked() and follow
        rt.py_ctrl        = path_ctrl
        rt.py_follow      = follow
        rt.py_bank        = bank
        rt.py_bank_amount = float(self.bank_amount_spin.value())
        rt.execute("""
        (
            try ( py_ctrl.follow      = py_follow )      catch ( donothing )
            try ( py_ctrl.bank        = py_bank )        catch ( donothing )
            try ( py_ctrl.bank_amount = py_bank_amount ) catch ( donothing )
        )
        """)
        rt.py_ctrl = rt.py_follow = rt.py_bank = rt.py_bank_amount = rt.undefined


# ------------------------------------------------------------------
# Dockable Window Runner
# ------------------------------------------------------------------

_dock_widget = None


def run_camera_rig_tool():
    global _dock_widget
    try:
        if _dock_widget is not None:
            _dock_widget.close()
            _dock_widget = None
    except Exception:
        pass

    max_hwnd = rt.windows.getMAXHWND()
    max_qwidget = QWidget.find(max_hwnd)
    camera_rig_ui = CameraRigUI(parent=max_qwidget)
    camera_rig_ui.setPalette(dark_palette())
    camera_rig_ui.setStyleSheet(QSS)
    _dock_widget = QDockWidget("Camera Rig Controller", parent=max_qwidget)
    _dock_widget.setWidget(camera_rig_ui)
    _dock_widget.setFloating(True)
    _dock_widget.setMinimumWidth(360)
    _dock_widget.setObjectName("CameraRigControllerDock_Final")
    _dock_widget.setStyleSheet(QSS)
    _dock_widget.show()
