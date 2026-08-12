"""Utility functions for rig management."""
import math
from pymxs import runtime as rt


def focal_to_fov(focal_mm: float, sensor_width: float = 36.0) -> float:
    """Convert focal length (mm) to horizontal FOV (degrees) assuming 36mm sensor."""
    if focal_mm <= 0:
        return 0.0
    return math.degrees(2.0 * math.atan((sensor_width / 2.0) / focal_mm))


def toggle_helpers_visibility(rig_nodes: dict) -> bool:
    """Toggle visibility of all rig helper nodes.

    Returns the new hidden state (True = now hidden).
    """
    is_any_hidden = any(
        rt.isValidNode(n) and n.isHidden
        for k, n in rig_nodes.items()
        if not k.startswith('_')
    )
    new_state = not is_any_hidden
    for k, n in rig_nodes.items():
        if k.startswith('_'):
            continue
        if rt.isValidNode(n):
            n.isHidden = new_state
    rt.redrawViews()
    return new_state


def set_lookat_weight(rig_nodes: dict, weight: int):
    """Set the LookAt constraint weight (0 = free aim, 100 = locked on target)."""
    pivot = rig_nodes.get('pivot')
    if not (pivot and rt.isValidNode(pivot)):
        return
    rt.py_temp_node = pivot
    rt.py_val = weight
    rt.execute(
        'try(py_temp_node.rotation.controller.targets[1].weight = py_val)catch(donothing);'
        'py_temp_node=undefined; py_val=undefined;'
    )
    rt.redrawViews()


def read_rig_state(rig_nodes: dict, camera) -> dict:
    """Read current rig state for UI syncing.

    Returns dict with keys: dolly_percent, crane_arm_angle, crane_base_angle,
    arm_z, roll, focal_length, near_clip, far_clip, dof_enabled
    """
    state = {}

    dolly_node = rig_nodes.get('dolly')
    if dolly_node and rt.isValidNode(dolly_node):
        rt.py_dolly_node = dolly_node
        val = rt.execute(
            'if isproperty py_dolly_node.pos.controller "percent" '
            'then py_dolly_node.pos.controller.percent else 0'
        )
        state['dolly_percent'] = float(val) if val is not None else 0.0
        rt.py_dolly_node = rt.undefined

    crane_arm = rig_nodes.get('crane_arm')
    if crane_arm and rt.isValidNode(crane_arm):
        rt.py_node = crane_arm
        val = rt.execute(
            'if isproperty py_node.rotation.controller "x_rotation" '
            'then py_node.rotation.controller.x_rotation else 0'
        )
        state['crane_arm_angle'] = float(val) if val is not None else 0.0
        try:
            state['arm_z'] = float(crane_arm.pos.z)
        except Exception:
            state['arm_z'] = 0.0
        rt.py_node = rt.undefined

    crane_base = rig_nodes.get('crane_base')
    if crane_base and rt.isValidNode(crane_base):
        rt.py_node = crane_base
        val = rt.execute(
            'if isproperty py_node.rotation.controller "z_rotation" '
            'then py_node.rotation.controller.z_rotation else 0'
        )
        state['crane_base_angle'] = float(val) if val is not None else 0.0
        rt.py_node = rt.undefined

    pivot = rig_nodes.get('pivot')
    if pivot and rt.isValidNode(pivot):
        rt.py_node = pivot
        val = rt.execute(
            'if isproperty py_node.rotation.controller "rollAngle" '
            'then py_node.rotation.controller.rollAngle else 0'
        )
        state['roll'] = float(val) if val is not None else 0.0
        rt.py_node = rt.undefined

    if camera and rt.isValidNode(camera):
        from camera_rig.core.lens_controls import get_camera_info
        info = get_camera_info(camera)
        if info.get('focal_length') is not None:
            state['focal_length'] = info['focal_length']
        if info.get('near_clip') is not None:
            state['near_clip'] = info['near_clip']
        if info.get('far_clip') is not None:
            state['far_clip'] = info['far_clip']
        if info.get('dof_enabled') is not None:
            state['dof_enabled'] = bool(info['dof_enabled'])
        if info.get('focus_dist') is not None:
            state['focus_dist'] = info['focus_dist']

    return state
