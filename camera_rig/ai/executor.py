"""Tool executor — bridges Claude tool calls to actual rig functions."""
import json
from pymxs import runtime as rt
from camera_rig.core import rig_controls, lens_controls, rig_builder, camera_shake
from camera_rig.framing.viewport_overlay import (
    install_overlay, uninstall_overlay, set_guide, set_safe_frame,
    set_aspect_ratio, ASPECT_PRESETS, any_guide_active,
)


class ToolExecutor:
    """Executes tool calls from the AI agent using the current rig state."""

    def __init__(self, get_ui_state):
        """
        get_ui_state: callable that returns a dict with:
          - rig_nodes
          - selected_camera
          - path_constraint_controller
          - initial_* positions
          - cam_right_vector (tuple rx, ry)
        """
        self._get_state = get_ui_state

    def execute(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool and return a string result for Claude."""
        try:
            state = self._get_state()
            rig_nodes = state.get('rig_nodes', {})
            camera = state.get('selected_camera')
            path_ctrl = state.get('path_constraint_controller')

            if tool_name == 'get_camera_state':
                return self._get_camera_state(state)

            elif tool_name == 'move_dolly':
                pct = float(tool_input['percent'])
                rig_controls.update_dolly_scene(path_ctrl, rig_nodes, pct)
                return f"Dolly moved to {pct:.1f}%"

            elif tool_name == 'crane_pitch':
                angle = float(tool_input['angle'])
                rig_controls.update_crane_arm(rig_nodes, angle)
                return f"Crane arm pitched to {angle:.1f}°"

            elif tool_name == 'crane_yaw':
                angle = float(tool_input['angle'])
                rig_controls.update_crane_base(rig_nodes, angle)
                return f"Crane base rotated to {angle:.1f}°"

            elif tool_name == 'crane_height':
                z = float(tool_input['z_value'])
                rig_controls.update_arm_reach(rig_nodes, z)
                return f"Crane height set to {z:.2f}"

            elif tool_name == 'pan_orbit':
                angle = float(tool_input['angle'])
                rig_controls.update_pan_orbit(rig_nodes, angle)
                return f"Camera panned to {angle:.1f}° (orbit mode)"

            elif tool_name == 'tilt_orbit':
                angle = float(tool_input['angle'])
                rig_controls.update_tilt_orbit(rig_nodes, angle)
                return f"Camera tilted to {angle:.1f}° (orbit mode)"

            elif tool_name == 'roll_camera':
                angle = float(tool_input['angle'])
                rig_controls.update_roll(rig_nodes, angle)
                return f"Camera rolled to {angle:.1f}°"

            elif tool_name == 'set_focal_length':
                fl = float(tool_input['focal_mm'])
                lens_controls.update_focal_length(camera, fl)
                return f"Focal length set to {fl:.1f}mm"

            elif tool_name == 'set_focus_distance':
                dist = float(tool_input['distance'])
                lens_controls.update_dof_distance(camera, dist)
                return f"Focus distance set to {dist:.2f}"

            elif tool_name == 'set_dolly_keyframe':
                active_ctrl = rig_nodes.get('_ai_path_ctrl') or path_ctrl
                if not active_ctrl:
                    return "Error: no path constraint — install a rig first"
                frame   = int(tool_input['frame'])
                percent = float(tool_input['percent'])
                rt.py_ctrl    = active_ctrl
                rt.py_frame   = frame
                rt.py_percent = percent
                rt.execute("""
                (
                    with animate on
                    (
                        at time py_frame py_ctrl.percent = py_percent
                    )
                    py_ctrl=undefined; py_frame=undefined; py_percent=undefined
                )
                """)
                rt.redrawViews()
                return f"Keyframe set: dolly={percent:.1f}% at frame {frame}"

            elif tool_name == 'bake_dolly_animation':
                active_ctrl = rig_nodes.get('_ai_path_ctrl') or path_ctrl
                if not active_ctrl:
                    return "Error: no path constraint controller found — install a rig first"
                print(f"[AI-Bake] ctrl={active_ctrl}  type={rt.classOf(active_ctrl)}")
                # Set keys using addNewKey + setKeyValue (most reliable for Path_Constraint)
                rt.py_ctrl = active_ctrl
                rt.py_t1   = int(tool_input['frame_start'])
                rt.py_t2   = int(tool_input['frame_end'])
                rt.py_v1   = float(tool_input['percent_start'])
                rt.py_v2   = float(tool_input['percent_end'])
                rt.execute("""
                (
                    try(deleteKeys py_ctrl #allKeys)catch(donothing)
                    local k1 = addNewKey py_ctrl py_t1
                    local k2 = addNewKey py_ctrl py_t2
                    if k1 != undefined do k1.value = py_v1
                    if k2 != undefined do k2.value = py_v2
                    print ("[AI-Bake] keys created: " + (py_ctrl.keys.count as string))
                    py_ctrl=undefined; py_t1=undefined; py_t2=undefined
                    py_v1=undefined;   py_v2=undefined
                )
                """)
                rt.redrawViews()
                return (f"Dolly animation baked: {tool_input['percent_start']:.0f}% → "
                        f"{tool_input['percent_end']:.0f}% "
                        f"frames {tool_input['frame_start']}–{tool_input['frame_end']}")

            elif tool_name == 'create_orbit_track':
                radius = float(tool_input['radius'])
                target = rig_nodes.get('target')
                if target and rt.isValidNode(target):
                    cx = float(tool_input.get('center_x', target.pos.x))
                    cy = float(tool_input.get('center_y', target.pos.y))
                else:
                    cx = float(tool_input.get('center_x', 0))
                    cy = float(tool_input.get('center_y', 0))
                center   = rt.Point3(cx, cy, 0)
                cam_name = camera.name if camera and rt.isValidNode(camera) else "Camera"
                circle   = rig_builder.create_orbit_track(cam_name, center, radius)
                if not circle:
                    return "Failed to create orbit track — no camera selected"
                # Assign orbit track to dolly and store new path ctrl for bake
                dolly = rig_nodes.get('dolly')
                if dolly and rt.isValidNode(dolly):
                    new_ctrl = rt.Path_Constraint()
                    new_ctrl.path = circle
                    rt.py_dolly_node = dolly
                    rt.py_path_ctrl  = new_ctrl
                    rt.execute('py_dolly_node.pos.controller = py_path_ctrl; py_dolly_node=undefined; py_path_ctrl=undefined;')
                    # Store new path ctrl so bake_dolly_animation can use it
                    rig_nodes['_ai_path_ctrl'] = new_ctrl
                    rig_nodes['orbit_track']   = circle
                    return f"Orbit track created (radius={radius:.1f}) and assigned to dolly"
                return f"Orbit track created with radius={radius:.1f} but no dolly to assign to"

            elif tool_name == 'reset_controls':
                rig_controls.reset_direct_controls(
                    rig_nodes,
                    initial_target_world_pos=state.get('initial_target_world_pos'),
                    initial_crane_base_world_pos=state.get('initial_crane_base_world_pos'),
                    initial_master_world_pos=state.get('initial_master_world_pos'),
                    initial_master_rot=state.get('initial_master_rot'),
                )
                return "Direct controls reset"

            elif tool_name == 'reset_dolly':
                active_ctrl = rig_nodes.get('_ai_path_ctrl') or path_ctrl
                if active_ctrl:
                    rig_controls.reset_dolly(active_ctrl, rig_nodes)
                return "Dolly reset to 0% — all keyframes removed"

            elif tool_name == 'reset_crane':
                initial_arm_z = state.get('initial_arm_z', 127.0)
                rig_controls.reset_crane(rig_nodes, initial_arm_z)
                return "Crane arm and base reset to default"

            elif tool_name == 'reset_all':
                active_ctrl = rig_nodes.get('_ai_path_ctrl') or path_ctrl
                if active_ctrl:
                    rig_controls.reset_dolly(active_ctrl, rig_nodes)
                initial_arm_z = state.get('initial_arm_z', 127.0)
                rig_controls.reset_crane(rig_nodes, initial_arm_z)
                rig_controls.reset_direct_controls(
                    rig_nodes,
                    initial_target_world_pos=state.get('initial_target_world_pos'),
                    initial_crane_base_world_pos=state.get('initial_crane_base_world_pos'),
                    initial_master_world_pos=state.get('initial_master_world_pos'),
                    initial_master_rot=state.get('initial_master_rot'),
                )
                rt.redrawViews()
                return "Full rig reset — dolly, crane, and all direct controls"

            elif tool_name == 'set_follow_path':
                active_ctrl = rig_nodes.get('_ai_path_ctrl') or path_ctrl
                if not active_ctrl:
                    return "Error: no path constraint found"
                enabled     = bool(tool_input['enabled'])
                bank        = bool(tool_input.get('bank', False)) and enabled
                bank_amount = float(tool_input.get('bank_amount', 0.5))
                rt.py_ctrl        = active_ctrl
                rt.py_follow      = enabled
                rt.py_bank        = bank
                rt.py_bank_amount = bank_amount
                rt.execute("""
                (
                    try(py_ctrl.follow = py_follow)catch(donothing)
                    try(py_ctrl.bank   = py_bank)catch(donothing)
                    if py_bank do try(py_ctrl.bank_amount = py_bank_amount)catch(donothing)
                    py_ctrl=undefined; py_follow=undefined; py_bank=undefined; py_bank_amount=undefined
                )
                """)
                rt.redrawViews()
                status = "enabled" if enabled else "disabled"
                return f"Follow path {status}" + (f" with banking={bank_amount}" if bank else "")

            elif tool_name == 'set_camera_shake':
                enabled = bool(tool_input['enabled'])
                if enabled:
                    camera_shake.install_shake(
                        rig_nodes,
                        frequency=float(tool_input.get('frequency', 0.5)),
                        strength_x=float(tool_input.get('strength_x', 2.0)),
                        strength_y=float(tool_input.get('strength_y', 2.0)),
                        strength_z=float(tool_input.get('strength_z', 1.0)),
                    )
                    return "Camera shake enabled"
                else:
                    camera_shake.remove_shake(rig_nodes)
                    return "Camera shake disabled"

            elif tool_name == 'set_composition_guide':
                thirds   = tool_input.get('thirds')
                golden   = tool_input.get('golden')
                center   = tool_input.get('center')
                diagonal = tool_input.get('diagonal')
                triangle = tool_input.get('triangle')
                spiral   = tool_input.get('spiral')
                any_on   = any(v for v in [thirds, golden, center, diagonal, triangle, spiral] if v is True)
                if any_on:
                    install_overlay()
                set_guide(
                    thirds=thirds, golden=golden, center=center,
                    diag=diagonal, triangle=triangle, spiral=spiral,
                )
                if not any_guide_active():
                    uninstall_overlay()
                active = [k for k, v in {
                    'thirds': thirds, 'golden': golden, 'center': center,
                    'diagonal': diagonal, 'triangle': triangle, 'spiral': spiral
                }.items() if v]
                return f"Guides active: {', '.join(active)}" if active else "All guides hidden"

            elif tool_name == 'set_safe_frame':
                enabled = bool(tool_input['enabled'])
                set_safe_frame(enabled)
                return f"Safe frame {'shown' if enabled else 'hidden'}"

            elif tool_name == 'set_aspect_ratio':
                ratio_str = str(tool_input['ratio'])
                # Try preset lookup first
                preset_map = {
                    '2.39': '2.39:1 (Anamorphic Scope)',
                    '1.85': '1.85:1 (Flat / US Widescreen)',
                    '1.78': '1.78:1 (16:9 HD)',
                    '1.33': '1.33:1 (4:3 Classic / Academy)',
                    '1.618': '1.618:1 (Golden Ratio — φ)',
                    '16:9': '1.78:1 (16:9 HD)',
                    '4:3':  '1.33:1 (4:3 Classic / Academy)',
                }
                preset_name = preset_map.get(ratio_str)
                if preset_name and preset_name in ASPECT_PRESETS:
                    w, h = ASPECT_PRESETS[preset_name]
                else:
                    # Parse w:h format
                    parts = ratio_str.replace(':', ' ').split()
                    w = int(float(parts[0])) if parts else 1920
                    h = int(float(parts[1])) if len(parts) > 1 else 1080
                set_aspect_ratio(w, h)
                set_safe_frame(True)
                return f"Aspect ratio set to {w}×{h} ({ratio_str})"

            elif tool_name == 'restore_straight_track':
                track = rig_nodes.get('track')
                dolly = rig_nodes.get('dolly')
                if track and dolly and rt.isValidNode(track) and rt.isValidNode(dolly):
                    new_ctrl = rt.Path_Constraint()
                    new_ctrl.path = track
                    rt.py_dolly_node = dolly
                    rt.py_path_ctrl  = new_ctrl
                    rt.execute('py_dolly_node.pos.controller = py_path_ctrl; py_dolly_node=undefined; py_path_ctrl=undefined;')
                    rig_nodes['_ai_path_ctrl'] = new_ctrl
                    rt.redrawViews()
                    return "Straight track restored and assigned to dolly"
                return "No straight track found"

            else:
                return f"Unknown tool: {tool_name}"

        except Exception as e:
            return f"Error executing {tool_name}: {e}"

    def _get_camera_state(self, state: dict) -> str:
        """Build a readable state description for Claude."""
        rig_nodes = state.get('rig_nodes', {})
        camera = state.get('selected_camera')
        path_ctrl = state.get('path_constraint_controller')

        lines = ["=== Current Camera Rig State ==="]

        if not rig_nodes:
            return "No rig installed. Install a rig first."

        # Dolly percent
        if path_ctrl:
            try:
                pct = float(path_ctrl.percent)
                lines.append(f"Dolly position: {pct:.1f}%")
            except Exception:
                lines.append("Dolly position: unknown")

        # Crane
        crane_arm = rig_nodes.get('crane_arm')
        if crane_arm and rt.isValidNode(crane_arm):
            rt.py_node = crane_arm
            pitch = rt.execute('if isproperty py_node.rotation.controller "x_rotation" then py_node.rotation.controller.x_rotation else 0')
            rt.py_node = rt.undefined
            lines.append(f"Crane arm pitch: {float(pitch or 0):.1f}°")
            lines.append(f"Crane arm height: {float(crane_arm.pos.z):.2f}")

        crane_base = rig_nodes.get('crane_base')
        if crane_base and rt.isValidNode(crane_base):
            rt.py_node = crane_base
            yaw = rt.execute('if isproperty py_node.rotation.controller "z_rotation" then py_node.rotation.controller.z_rotation else 0')
            rt.py_node = rt.undefined
            lines.append(f"Crane base yaw: {float(yaw or 0):.1f}°")

        # Camera
        if camera and rt.isValidNode(camera):
            info = lens_controls.get_camera_info(camera)
            lines.append(f"Camera: {camera.name} ({info.get('type', 'unknown')})")
            if info.get('focal_length') is not None:
                lines.append(f"Focal length: {info['focal_length']:.1f}mm")
            if info.get('focus_dist') is not None:
                lines.append(f"Focus distance: {info['focus_dist']:.2f}")
            p = camera.pos
            lines.append(f"Camera world pos: ({p.x:.2f}, {p.y:.2f}, {p.z:.2f})")

        return "\n".join(lines)
