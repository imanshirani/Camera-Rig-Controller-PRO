"""Rig creation, cleanup, and loading logic."""
import os
from pymxs import runtime as rt

_SHAPES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "assets", "shape.max"
)

# Shape names as stored in shape.max → rig key
_SHAPE_MAP = {
    'DOLLY_CTRL':   'dolly',
    'CRANE_BASE':   'crane_base',
    'CRANE_ARM':    'crane_arm',
    'MASTER':       'master',
    'PIVOT':        'pivot',
    'TARGET':       'target',
    'TRACK_CTRL':   'track_ctrl',
}




def _load_custom_shapes() -> dict:
    """Merge shape.max once and return {shape_name: node} for all found shapes.

    Returns empty dict if file missing or merge fails.
    """
    if not os.path.isfile(_SHAPES_FILE):
        return {}

    # Record all object names before merge
    before = {str(obj.name) for obj in rt.objects}

    try:
        rt.mergeMaxFile(_SHAPES_FILE, rt.Name("neverReparent"))
    except Exception:
        return {}

    # Find newly added objects
    shapes = {}
    for obj in rt.objects:
        name = str(obj.name)
        if name not in before and name in _SHAPE_MAP:
            shapes[name] = obj

    return shapes


def cleanup_old_rig(cam_name: str):
    """Delete all existing rig nodes for the given camera name."""
    prefix = f"RIG_{cam_name}_"
    to_delete = [
        obj for obj in rt.objects
        if obj.name.startswith(prefix) and rt.isValidNode(obj)
    ]
    for obj in to_delete:
        rt.delete(obj)


def install_camera_rig(camera, track_length: float, crane_height: float = 127.0) -> dict:
    """Create a full camera rig and return the rig_nodes dict."""
    cam_name  = camera.name
    cam_pos   = camera.pos  # world position in system units

    # camera target
    s_camera_target = None
    target_pos = camera.pos + (camera.dir * 300.0)
    if (rt.isProperty(camera, 'target')
            and camera.target
            and rt.isValidNode(camera.target)):
        s_camera_target = camera.target
        target_pos = s_camera_target.pos

    # camera forward direction flattened to XY plane for track orientation
    cam_dir = camera.dir
    rt.py_dir = rt.Point3(cam_dir.x, cam_dir.y, 0)
    flat_len = rt.execute('length py_dir')
    rt.py_dir = rt.undefined
    if flat_len and float(flat_len) > 0.001:
        dir_x = cam_dir.x / float(flat_len)
        dir_y = cam_dir.y / float(flat_len)
    else:
        dir_x, dir_y = 1.0, 0.0

    rig_nodes = {}
    custom = _load_custom_shapes()

    def _get_or_make(shape_key, make_fn):
        node = custom.get(shape_key)
        if node and rt.isValidNode(node):
            node.name = f"RIG_{cam_name}_{shape_key}"
            # delete any other shapes with same key that got merged as duplicates
            for other_key, other_node in list(custom.items()):
                if other_key == shape_key and other_node != node and rt.isValidNode(other_node):
                    rt.delete(other_node)
            return node
        return make_fn()

    # ── Step 1: Create all nodes at their correct world positions ────

    # DOLLY: on the ground under camera (z=0)
    ground_pos = rt.Point3(cam_pos.x, cam_pos.y, 0)
    dolly = _get_or_make("DOLLY_CTRL", lambda: rt.Point(
        name=f"RIG_{cam_name}_DOLLY_CTRL", pos=ground_pos, cross=True, size=25))
    dolly.wirecolor = rt.yellow
    dolly.pos = ground_pos
    rig_nodes['dolly'] = dolly

    # CRANE_BASE: same as dolly on the ground
    crane_base = _get_or_make("CRANE_BASE", lambda: rt.Rectangle(
        name=f"RIG_{cam_name}_CRANE_BASE", pos=ground_pos, length=60, width=60))
    crane_base.wirecolor = rt.color(255, 140, 0)
    crane_base.pos = ground_pos
    rig_nodes['crane_base'] = crane_base

    # CRANE_ARM: crane_height units above camera
    arm_world_pos = rt.Point3(cam_pos.x, cam_pos.y, cam_pos.z + crane_height)
    crane_arm = _get_or_make("CRANE_ARM", lambda: rt.Point(
        name=f"RIG_{cam_name}_CRANE_ARM", axistripod=True, size=30))
    crane_arm.wirecolor = rt.color(255, 140, 0)
    crane_arm.pos = arm_world_pos
    rig_nodes['crane_arm'] = crane_arm

    # MASTER: at crane_arm world position
    master = _get_or_make("MASTER", lambda: rt.Circle(
        name=f"RIG_{cam_name}_MASTER", radius=50))
    master.wirecolor = rt.yellow
    master.pos = arm_world_pos
    rig_nodes['master'] = master

    # PIVOT: at crane_arm height, camera is child so it moves here too
    pivot = _get_or_make("PIVOT", lambda: rt.Point(
        name=f"RIG_{cam_name}_PIVOT", cross=True, box=True, size=15))
    pivot.wirecolor = rt.color(0, 180, 255)
    pivot.pos = arm_world_pos
    rig_nodes['pivot'] = pivot

    # TARGET: in front of camera at crane height
    target_pos_at_height = rt.Point3(
        target_pos.x, target_pos.y, arm_world_pos.z)
    target_node = _get_or_make("TARGET", lambda: rt.Point(
        name=f"RIG_{cam_name}_TARGET", cross=True, centermarker=True, size=10))
    target_node.wirecolor = rt.color(0, 220, 100)
    target_node.pos = target_pos_at_height
    rig_nodes['target'] = target_node

    # TRACK_CTRL: helper at camera ground position — user moves this to reposition track
    track_ctrl = _get_or_make("TRACK_CTRL", lambda: rt.Point(
        name=f"RIG_{cam_name}_TRACK_CTRL", cross=True, size=20))
    track_ctrl.wirecolor = rt.color(120, 120, 120)
    track_ctrl.pos = ground_pos
    rig_nodes['track_ctrl'] = track_ctrl

    # TRACK: built in LOCAL space of track_ctrl (pivot = center of track)
    # knots at (-half, 0, 0) and (+half, 0, 0) in local space
    half = track_length / 2.0
    track_path = rt.Line(name=f"RIG_{cam_name}_TRACK")
    track_path.wirecolor = rt.color(120, 120, 120)
    rt.addNewSpline(track_path)
    # Build in world space matching camera direction, pivot at ground_pos
    rt.addKnot(track_path, 1, rt.Name("corner"), rt.Name("line"),
               rt.Point3(cam_pos.x - dir_x * half, cam_pos.y - dir_y * half, 0))
    rt.addKnot(track_path, 1, rt.Name("corner"), rt.Name("line"),
               rt.Point3(cam_pos.x + dir_x * half, cam_pos.y + dir_y * half, 0))
    rt.updateShape(track_path)
    # Parent track to ctrl — now moving ctrl moves the whole track
    track_path.parent = track_ctrl
    rig_nodes['track'] = track_path

    # ── Step 2: LookAt on pivot (before parenting) ───────────────────
    lookat_ctrl = rt.LookAt_Constraint()
    lookat_ctrl.appendTarget(target_node, 100)
    rt.py_pivot_node  = pivot
    rt.py_lookat_ctrl = lookat_ctrl
    rt.execute('py_pivot_node.rotation.controller = py_lookat_ctrl; py_pivot_node=undefined; py_lookat_ctrl=undefined;')

    # ── Step 3: Move camera to crane height before parenting ─────────
    # Max preserves world position on parent — we want camera at crane height
    camera.pos = arm_world_pos
    if s_camera_target:
        s_camera_target.pos = target_pos_at_height

    # ── Step 3: Build hierarchy ───────────────────────────────────────
    crane_base.parent  = dolly
    crane_arm.parent   = crane_base
    master.parent      = crane_arm
    pivot.parent       = master
    target_node.parent = master
    camera.parent      = pivot
    if s_camera_target:
        s_camera_target.parent = target_node

    # ── Step 4: Path constraint AFTER hierarchy ──────────────────────
    # Now dolly (and all its children) move together to track center
    path_ctrl = rt.Path_Constraint()
    path_ctrl.path = track_path
    rt.py_dolly_node = dolly
    rt.py_path_ctrl  = path_ctrl
    rt.execute('py_dolly_node.pos.controller = py_path_ctrl; py_dolly_node=undefined; py_path_ctrl=undefined;')
    path_ctrl.percent = 0.0

    rig_nodes['_initial_arm_z'] = float(arm_world_pos.z)
    rig_nodes['_path_ctrl']     = path_ctrl
    return rig_nodes


def load_existing_rig(camera) -> dict:
    """Find existing rig nodes by naming convention. Returns dict or empty dict."""
    cam_name = camera.name
    base_names = {
        'dolly':      '_DOLLY_CTRL',
        'master':     '_MASTER',
        'target':     '_TARGET',
        'pivot':      '_PIVOT',
        'crane_base': '_CRANE_BASE',
        'crane_arm':  '_CRANE_ARM',
        'track':      '_TRACK',
        'track_ctrl': '_TRACK_CTRL',
    }
    rig_nodes = {}
    for key, suffix in base_names.items():
        node = rt.getNodeByName(f"RIG_{cam_name}{suffix}")
        if node and rt.isValidNode(node):
            rig_nodes[key] = node

    # Load path constraint controller
    dolly_node = rig_nodes.get('dolly')
    if dolly_node:
        rt.py_dolly_node = dolly_node
        rig_nodes['_path_ctrl'] = rt.execute('py_dolly_node.pos.controller')
        rt.py_dolly_node = rt.undefined

    return rig_nodes


def capture_initial_positions(rig_nodes: dict, camera) -> dict:
    """Capture initial positions needed for reset operations.

    Returns dict with keys: target_local_pos, crane_base_local_pos, crane_base_world_z, arm_z
    """
    result = {}

    # Capture world positions for reset — no local space calculations needed
    target_node = rig_nodes.get('target')
    if target_node and rt.isValidNode(target_node):
        result['target_world_pos'] = rt.Point3(
            target_node.pos.x, target_node.pos.y, target_node.pos.z)
        result['target_world_x'] = float(target_node.pos.x)
        result['target_world_y'] = float(target_node.pos.y)
        result['target_world_z'] = float(target_node.pos.z)

    crane_base_node = rig_nodes.get('crane_base')
    if crane_base_node and rt.isValidNode(crane_base_node):
        result['crane_base_world_pos'] = rt.Point3(
            crane_base_node.pos.x, crane_base_node.pos.y, crane_base_node.pos.z)
        result['crane_base_world_z'] = float(crane_base_node.pos.z)

    master_node = rig_nodes.get('master')
    if master_node and rt.isValidNode(master_node):
        result['master_world_pos'] = rt.Point3(
            master_node.pos.x, master_node.pos.y, master_node.pos.z)
        result['master_rot'] = rt.copy(master_node.rotation)

    crane_arm = rig_nodes.get('crane_arm')
    if crane_arm and rt.isValidNode(crane_arm):
        result['arm_z'] = float(crane_arm.pos.z)

    return result


def create_orbit_track(cam_name: str, center_pos, radius: float):
    """Create a circular spline track for orbit/arc shots.

    center_pos: rt.Point3 — center of the orbit (usually target node position)
    radius: float — orbit radius in scene units
    Returns the Circle spline node.
    """
    old = rt.getNodeByName(f"RIG_{cam_name}_ORBIT_TRACK")
    if old and rt.isValidNode(old):
        rt.delete(old)

    circle = rt.Circle(
        name=f"RIG_{cam_name}_ORBIT_TRACK",
        pos=rt.Point3(center_pos.x, center_pos.y, 0),
        radius=radius,
    )
    circle.wirecolor = rt.color(120, 120, 120)
    return circle


def log_rig_positions(rig_nodes: dict) -> str:
    """Return a formatted string of all rig node world positions for debugging."""
    lines = ["=== Rig Node Positions ==="]
    for key, node in rig_nodes.items():
        if key.startswith('_'):
            continue
        if rt.isValidNode(node):
            pos = node.pos
            lines.append(f"  {node.name:<40s}  ({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f})")
        else:
            lines.append(f"  {key:<40s}  (invalid)")
    return "\n".join(lines)
