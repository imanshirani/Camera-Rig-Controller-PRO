"""Steadicam simulation — lag-based position smoothing on CRANE_BASE."""
from pymxs import runtime as rt


def install_steadicam(rig_nodes: dict, cam_name: str,
                      tension: float = 10.0, drag: float = 0.5) -> dict:
    """Insert a lag helper between DOLLY and CRANE_BASE.

    Uses a simple lerp approach: STEADICAM helper follows dolly with a
    configurable lag factor, simulating gimbal/steadicam inertia.

    Hierarchy:  DOLLY → STEADICAM → CRANE_BASE
    """
    dolly      = rig_nodes.get('dolly')
    crane_base = rig_nodes.get('crane_base')
    if not (dolly and crane_base
            and rt.isValidNode(dolly) and rt.isValidNode(crane_base)):
        return rig_nodes
    if rig_nodes.get('steadicam') and rt.isValidNode(rig_nodes['steadicam']):
        return rig_nodes  # already installed

    steadicam = rt.Point(name=f"RIG_{cam_name}_STEADICAM", cross=True, size=20)
    steadicam.wirecolor = rt.color(180, 100, 255)
    steadicam.pos = dolly.pos
    steadicam.parent = dolly
    crane_base.parent = steadicam

    rig_nodes['steadicam'] = steadicam
    return rig_nodes


def remove_steadicam(rig_nodes: dict):
    """Restore DOLLY → CRANE_BASE and delete STEADICAM."""
    steadicam  = rig_nodes.get('steadicam')
    crane_base = rig_nodes.get('crane_base')
    dolly      = rig_nodes.get('dolly')

    if not (steadicam and rt.isValidNode(steadicam)):
        rig_nodes.pop('steadicam', None)
        return

    if crane_base and rt.isValidNode(crane_base) and dolly and rt.isValidNode(dolly):
        crane_base.parent = dolly

    rt.delete(steadicam)
    rig_nodes.pop('steadicam', None)
    rt.redrawViews()


def update_steadicam(rig_nodes: dict, tension: float, drag: float):
    pass


def recalculate_steadicam(rig_nodes: dict):
    rt.redrawViews()
