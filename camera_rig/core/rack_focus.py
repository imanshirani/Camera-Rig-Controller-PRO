"""Rack focus and focus subject picker utilities."""
from pymxs import runtime as rt


def get_distance_to_node(camera, node) -> float:
    """Return world-space distance from camera position to a scene node."""
    return float(rt.length(camera.pos - node.pos))


def snap_focus_to_target(camera, rig_nodes: dict) -> float:
    """Set camera focus distance to the current camera→TARGET distance.

    Returns the distance that was applied.
    """
    target = rig_nodes.get('target')
    if not (target and rt.isValidNode(target)):
        return 0.0
    dist = get_distance_to_node(camera, target)
    _apply_focus_distance(camera, dist)
    return dist


def pick_focus_subject(camera) -> float | None:
    """Open an interactive pick session in 3ds Max.

    Returns distance from camera to picked node, or None if cancelled.
    """
    rt.execute('py_picked = pickObject prompt:"Pick focus subject"')
    picked = getattr(rt, 'py_picked', None)
    rt.py_picked = rt.undefined
    if picked is None or picked == rt.undefined:
        return None
    if not rt.isValidNode(picked):
        return None
    return get_distance_to_node(camera, picked)


def bake_rack_focus(camera, from_dist: float, to_dist: float,
                    frame_start: int, frame_end: int,
                    ease_in: bool, ease_out: bool,
                    tangent_type: str = "slow"):
    """Animate focus distance from from_dist to to_dist over frame range.

    Creates two animation keys with optional Ease In / Ease Out tangents.
    """
    rt.py_cam     = camera
    rt.py_v1      = from_dist
    rt.py_v2      = to_dist
    rt.py_t1      = frame_start
    rt.py_t2      = frame_end
    rt.py_ease_in  = ease_in
    rt.py_ease_out = ease_out
    rt.py_tangent  = tangent_type

    # Determine which property to animate
    if rt.isProperty(camera, 'mdof_focalDepth'):
        rt.execute("""
        (
            with animate on
            (
                at time py_t1 py_cam.mdof_focalDepth = py_v1
                at time py_t2 py_cam.mdof_focalDepth = py_v2
            )
            local atrack = py_cam.mdof_focalDepth.controller
            if atrack != undefined and atrack.keys.count >= 2 do
            (
                local ttype = case py_tangent of ("slow":#slow "linear":#linear "fast":#fast "smooth":#smooth default:#slow)
                if py_ease_in  do setTangentType atrack.keys[1]                #out ttype
                if py_ease_out do setTangentType atrack.keys[atrack.keys.count] #in  ttype
            )
        )
        """)
    elif rt.isProperty(camera, 'targetDistance'):
        rt.execute("""
        (
            with animate on
            (
                at time py_t1 py_cam.targetDistance = py_v1
                at time py_t2 py_cam.targetDistance = py_v2
            )
            local atrack = py_cam.targetDistance.controller
            if atrack != undefined and atrack.keys.count >= 2 do
            (
                local ttype = case py_tangent of ("slow":#slow "linear":#linear "fast":#fast "smooth":#smooth default:#slow)
                if py_ease_in  do setTangentType atrack.keys[1]                #out ttype
                if py_ease_out do setTangentType atrack.keys[atrack.keys.count] #in  ttype
            )
        )
        """)

    rt.py_cam = rt.py_v1 = rt.py_v2 = rt.undefined
    rt.py_t1  = rt.py_t2 = rt.undefined
    rt.py_ease_in = rt.py_ease_out = rt.undefined
    rt.py_tangent  = rt.undefined


def _apply_focus_distance(camera, dist: float):
    """Write focus distance to the appropriate camera property."""
    if rt.isProperty(camera, 'mdof_focalDepth'):
        camera.mdof_focalDepth = dist
    elif rt.isProperty(camera, 'targetDistance'):
        camera.targetDistance = dist
