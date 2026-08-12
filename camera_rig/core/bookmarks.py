"""Shot bookmark management — save and restore camera positions."""
from pymxs import runtime as rt


class ShotBookmark:
    """Stores a named camera state snapshot."""
    __slots__ = ('name', 'cam_pos', 'cam_rot', 'target_pos', 'focal_length', 'frame')

    def __init__(self, name: str, cam_pos, cam_rot, target_pos, focal_length: float, frame: int):
        self.name = name
        self.cam_pos = cam_pos
        self.cam_rot = cam_rot
        self.target_pos = target_pos
        self.focal_length = focal_length
        self.frame = frame


def save_bookmark(camera, rig_nodes: dict, name: str) -> ShotBookmark:
    """Capture current camera state as a bookmark."""
    cam_pos = rt.copy(camera.pos)
    cam_rot = rt.copy(camera.rotation)
    target_node = rig_nodes.get('target')
    target_pos = rt.copy(target_node.pos) if (target_node and rt.isValidNode(target_node)) else None
    focal_length = float(camera.lens) if rt.isProperty(camera, 'lens') else 35.0
    frame = int(rt.currentTime)
    return ShotBookmark(name, cam_pos, cam_rot, target_pos, focal_length, frame)


def apply_bookmark(camera, rig_nodes: dict, bookmark: ShotBookmark):
    """Restore camera to a previously saved bookmark state."""
    if not (camera and rt.isValidNode(camera)):
        return

    camera.pos = bookmark.cam_pos
    camera.rotation = bookmark.cam_rot

    target_node = rig_nodes.get('target')
    if target_node and rt.isValidNode(target_node) and bookmark.target_pos:
        target_node.pos = bookmark.target_pos

    if rt.isProperty(camera, 'lens'):
        camera.lens = bookmark.focal_length

    rt.currentTime = bookmark.frame
    rt.redrawViews()
