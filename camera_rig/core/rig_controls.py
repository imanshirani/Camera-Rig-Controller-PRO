"""Rig movement control functions — dolly, crane, direct controls."""
from pymxs import runtime as rt


def update_dolly_scene(path_ctrl, rig_nodes: dict, percent: float):
    if path_ctrl and rt.isValidNode(rig_nodes.get('dolly')):
        path_ctrl.percent = percent
        rt.redrawViews()


def update_crane_arm(rig_nodes: dict, angle: float):
    crane_arm = rig_nodes.get('crane_arm')
    if not (crane_arm and rt.isValidNode(crane_arm)):
        return
    rt.py_temp_node = crane_arm
    rt.py_val = angle
    rt.execute('try(py_temp_node.rotation.controller.x_rotation = py_val)catch(donothing); py_temp_node=undefined; py_val=undefined;')
    rt.redrawViews()


def update_crane_base(rig_nodes: dict, angle: float):
    crane_base = rig_nodes.get('crane_base')
    if not (crane_base and rt.isValidNode(crane_base)):
        return
    rt.py_temp_node = crane_base
    rt.py_val = angle
    rt.execute('try(py_temp_node.rotation.controller.z_rotation = py_val)catch(donothing); py_temp_node=undefined; py_val=undefined;')
    rt.redrawViews()


def update_arm_reach(rig_nodes: dict, z_value: float):
    crane_arm = rig_nodes.get('crane_arm')
    if not (crane_arm and rt.isValidNode(crane_arm)):
        return
    rt.py_temp_node = crane_arm
    rt.py_val = z_value
    rt.execute('try(py_temp_node.pos.z = py_val)catch(donothing); py_temp_node=undefined; py_val=undefined;')
    rt.redrawViews()


def update_truck(rig_nodes: dict, offset: float, initial_world_pos, lock_target: bool,
                 cam_right_x: float = 0.0, cam_right_y: float = 1.0):
    """Move crane_base left/right perpendicular to camera forward direction.

    cam_right_x/y: the right vector of the camera projected on XY plane (normalized).
    """
    crane_base = rig_nodes.get('crane_base')
    if not (crane_base and rt.isValidNode(crane_base)):
        return
    if initial_world_pos is None:
        return

    rt.py_node    = crane_base
    rt.py_init_x  = float(initial_world_pos.x)
    rt.py_init_y  = float(initial_world_pos.y)
    rt.py_right_x = cam_right_x
    rt.py_right_y = cam_right_y
    rt.py_val     = offset
    rt.py_lock    = lock_target

    target_name = rig_nodes['target'].name if rig_nodes.get('target') else ""
    rt.execute(f"""
    (
        local old_pos = py_node.pos
        local new_x = py_init_x + py_right_x * py_val
        local new_y = py_init_y + py_right_y * py_val
        py_node.pos = [new_x, new_y, py_node.pos.z]
        if py_lock do
        (
            local move_vec = py_node.pos - old_pos
            local t = getNodeByName "{target_name}"
            if t != undefined do t.pos += move_vec
        )
    )
    """)
    rt.py_node = rt.py_init_x = rt.py_init_y = rt.undefined
    rt.py_right_x = rt.py_right_y = rt.py_val = rt.py_lock = rt.undefined
    rt.redrawViews()


def update_pedestal(rig_nodes: dict, offset: float, initial_world_z: float, lock_target: bool):
    crane_base = rig_nodes.get('crane_base')
    if not (crane_base and rt.isValidNode(crane_base)):
        return
    if initial_world_z is None:
        return

    rt.py_node = crane_base
    rt.py_val = initial_world_z + offset
    rt.py_lock_state = lock_target

    target_name = rig_nodes['target'].name if rig_nodes.get('target') else ""
    rt.execute(f"""
    (
        local old_pos_world = py_node.pos
        py_node.pos.z = py_val
        if py_lock_state do
        (
            local move_vec = py_node.pos - old_pos_world
            local t = getNodeByName "{target_name}"
            if t != undefined do (t.pos += move_vec)
        )
    )
    """)
    rt.py_node = rt.undefined
    rt.py_val = rt.undefined
    rt.py_lock_state = rt.undefined
    rt.redrawViews()


def update_target_pan(rig_nodes: dict, value: float,
                      initial_world_x: float = 0.0, initial_world_y: float = 0.0,
                      cam_right_x: float = 1.0, cam_right_y: float = 0.0):
    """Move TARGET left/right — same axis as tilt but horizontal."""
    target = rig_nodes.get('target')
    if not (target and rt.isValidNode(target)):
        return
    rt.py_target  = target
    rt.py_init_x  = initial_world_x
    rt.py_init_y  = initial_world_y
    rt.py_rx      = cam_right_x
    rt.py_ry      = cam_right_y
    rt.py_val     = value
    rt.execute("""
    (
        py_target.pos.x = py_init_x + py_rx * py_val
        py_target.pos.y = py_init_y + py_ry * py_val
        py_target=undefined; py_init_x=undefined; py_init_y=undefined
        py_rx=undefined; py_ry=undefined; py_val=undefined
    )
    """)
    rt.redrawViews()


def update_target_tilt(rig_nodes: dict, value: float, initial_world_z: float = 0.0):
    """Move TARGET along world Z axis for tilt (up/down) — Linear mode."""
    target = rig_nodes.get('target')
    if not (target and rt.isValidNode(target)):
        return
    rt.py_target = target
    rt.py_val = initial_world_z + value
    rt.execute('py_target.pos.z = py_val; py_target=undefined; py_val=undefined;')
    rt.redrawViews()


def update_pan_orbit(rig_nodes: dict, angle: float):
    """Rotate MASTER around its Z axis — TARGET orbits around camera (Orbit mode pan)."""
    master = rig_nodes.get('master')
    if not (master and rt.isValidNode(master)):
        return
    rt.py_temp_node = master
    rt.py_val = angle
    rt.execute(
        'try(py_temp_node.rotation.controller.z_rotation = py_val)catch(donothing);'
        'py_temp_node=undefined; py_val=undefined;'
    )
    rt.redrawViews()


def update_tilt_orbit(rig_nodes: dict, angle: float):
    """Rotate MASTER around its X axis — TARGET orbits around camera (Orbit mode tilt)."""
    master = rig_nodes.get('master')
    if not (master and rt.isValidNode(master)):
        return
    rt.py_temp_node = master
    rt.py_val = angle
    rt.execute(
        'try(py_temp_node.rotation.controller.x_rotation = py_val)catch(donothing);'
        'py_temp_node=undefined; py_val=undefined;'
    )
    rt.redrawViews()


def update_roll(rig_nodes: dict, angle: float):
    pivot = rig_nodes.get('pivot')
    if not (pivot and rt.isValidNode(pivot)):
        return
    rt.py_temp_node = pivot
    rt.py_val = angle
    # LookAt_Constraint roll property: try both naming conventions
    rt.execute("""
    (
        local ctrl = py_temp_node.rotation.controller
        local done = false
        try ( ctrl.roll = py_val;       done = true ) catch ( donothing )
        if not done do
        try ( ctrl.rollAngle = py_val;  done = true ) catch ( donothing )
        if not done do
        try ( ctrl.z_rotation = py_val; done = true ) catch ( donothing )
        py_temp_node = undefined
        py_val = undefined
    )
    """)
    rt.redrawViews()


def reset_dolly(path_ctrl, rig_nodes: dict):
    if not (path_ctrl and rt.isValidNode(rig_nodes.get('dolly'))):
        return
    current_mode = rt.execute('animateMode')
    is_auto_key_on = current_mode in [rt.Name('auto'), rt.Name('set')]
    if is_auto_key_on:
        rt.execute('animate off')
    rt.py_temp_ctrl = path_ctrl
    rt.execute('try(deleteKeys py_temp_ctrl #allKeys)catch(donothing); py_temp_ctrl=undefined;')
    path_ctrl.percent = 0
    if is_auto_key_on:
        rt.execute('animate on')


def reset_crane(rig_nodes: dict, initial_arm_z: float):
    current_mode = rt.execute('animateMode')
    is_auto_key_on = current_mode in [rt.Name('auto'), rt.Name('set')]
    if is_auto_key_on:
        rt.execute('animate off')

    crane_arm = rig_nodes.get('crane_arm')
    if crane_arm and rt.isValidNode(crane_arm):
        rt.py_temp_node = crane_arm
        rt.execute(
            'try(deleteKeys py_temp_node.rotation.controller #allKeys)catch(donothing);'
            'try(py_temp_node.rotation.controller.x_rotation = 0)catch(donothing);'
            'py_temp_node=undefined;'
        )

    crane_base = rig_nodes.get('crane_base')
    if crane_base and rt.isValidNode(crane_base):
        rt.py_temp_node = crane_base
        rt.execute(
            'try(deleteKeys py_temp_node.rotation.controller #allKeys)catch(donothing);'
            'try(py_temp_node.rotation.controller.z_rotation = 0)catch(donothing);'
            'py_temp_node=undefined;'
        )

    # reset arm reach
    if crane_arm and rt.isValidNode(crane_arm):
        rt.py_temp_node = crane_arm
        rt.py_val = initial_arm_z
        rt.execute('try(py_temp_node.pos.z = py_val)catch(donothing); py_temp_node=undefined; py_val=undefined;')

    if is_auto_key_on:
        rt.execute('animate on')


def reset_direct_controls(rig_nodes: dict,
                          initial_target_world_pos=None,
                          initial_crane_base_world_pos=None,
                          initial_master_world_pos=None,
                          **kwargs):
    """Reset truck/pedestal/pan/tilt/roll to their initial world positions."""
    current_mode = rt.execute('animateMode')
    is_auto_key_on = current_mode in [rt.Name('auto'), rt.Name('set')]
    if is_auto_key_on:
        rt.execute('animate off')

    def _reset_node_pos(node, world_pos):
        if not (node and rt.isValidNode(node) and world_pos):
            return
        rt.py_node = node
        rt.py_pos  = world_pos
        rt.execute(
            'try(deleteKeys py_node.pos.controller #allKeys)catch(donothing);'
            'py_node.pos = py_pos;'
            'py_node=undefined; py_pos=undefined;'
        )

    def _reset_node_rot(node):
        if not (node and rt.isValidNode(node)):
            return
        rt.py_node = node
        rt.execute(
            'try(deleteKeys py_node.rotation.controller #allKeys)catch(donothing);'
            'try(py_node.rotation.controller.x_rotation = 0)catch(donothing);'
            'try(py_node.rotation.controller.y_rotation = 0)catch(donothing);'
            'try(py_node.rotation.controller.z_rotation = 0)catch(donothing);'
            'py_node=undefined;'
        )

    # Reset CRANE_BASE world pos (resets truck/pedestal)
    _reset_node_pos(rig_nodes.get('crane_base'), initial_crane_base_world_pos)

    # Reset MASTER: rotation first, then fix position
    master = rig_nodes.get('master')
    initial_master_rot = kwargs.get('initial_master_rot')
    if master and rt.isValidNode(master) and initial_master_rot and initial_master_world_pos:
        rt.py_node = master
        rt.py_rot  = initial_master_rot
        rt.py_pos  = initial_master_world_pos
        rt.execute("""
        (
            try(deleteKeys py_node.rotation.controller #allKeys)catch(donothing)
            try(deleteKeys py_node.pos.controller #allKeys)catch(donothing)
            py_node.rotation = py_rot
            py_node.pos = py_pos
            py_node = undefined; py_rot = undefined; py_pos = undefined
        )
        """)

    # Reset TARGET world pos (resets linear pan/tilt)
    _reset_node_pos(rig_nodes.get('target'), initial_target_world_pos)

    # Reset roll on PIVOT
    pivot = rig_nodes.get('pivot')
    if pivot and rt.isValidNode(pivot):
        rt.py_temp_node = pivot
        rt.execute("""
        (
            local ctrl = py_temp_node.rotation.controller
            try ( ctrl.roll      = 0 ) catch ( donothing )
            try ( ctrl.rollAngle = 0 ) catch ( donothing )
            py_temp_node = undefined
        )
        """)

    if is_auto_key_on:
        rt.execute('animate on')
    rt.redrawViews()


def bake_dolly_easing(path_ctrl, frame_start: int, frame_end: int,
                      val_start: float, val_end: float,
                      ease_in: bool, ease_out: bool,
                      tangent_type: str = "slow"):
    """Bake dolly animation keys with optional Ease In / Ease Out tangents.

    Deletes existing keys on path_ctrl.percent, creates two keys
    (frame_start → val_start, frame_end → val_end), then applies
    #slow tangent type for ease-in on key 1 and/or ease-out on last key.
    """
    rt.py_ctrl        = path_ctrl
    rt.py_t1          = frame_start
    rt.py_t2          = frame_end
    rt.py_v1          = val_start
    rt.py_v2          = val_end
    rt.py_ease_in     = ease_in
    rt.py_ease_out    = ease_out
    rt.py_tangent     = tangent_type
    rt.execute("""
    (
        -- Get or create the percent sub-controller
        local atrack = py_ctrl.percent.controller
        if atrack == undefined do
        (
            atrack = bezier_float()
            py_ctrl.percent.controller = atrack
        )
        -- Clear existing keys
        try(deleteKeys atrack #allKeys)catch(donothing)
        -- Add keyframes directly on the sub-controller
        local k1 = addNewKey atrack py_t1
        local k2 = addNewKey atrack py_t2
        if k1 != undefined do ( k1.value = py_v1 )
        if k2 != undefined do ( k2.value = py_v2 )
        -- Apply tangent type
        if atrack.keys.count >= 2 do
        (
            local ttype = case py_tangent of (
                "slow":   #slow
                "linear": #linear
                "fast":   #fast
                "smooth": #smooth
                default:  #slow
            )
            try (
                if py_ease_in  do atrack.keys[1].outTangentType               = ttype
                if py_ease_out do atrack.keys[atrack.keys.count].inTangentType = ttype
            ) catch ( donothing )
        )
    )
    """)
    rt.py_ctrl     = rt.undefined
    rt.py_t1       = rt.undefined
    rt.py_t2       = rt.undefined
    rt.py_v1       = rt.undefined
    rt.py_v2       = rt.undefined
    rt.py_ease_in  = rt.undefined
    rt.py_ease_out = rt.undefined
    rt.py_tangent  = rt.undefined
