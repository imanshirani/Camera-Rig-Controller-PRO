"""Lens, clipping, and DOF control functions.

Supports Standard, Physical (target/free), VRay Physical, Corona cameras.
"""
from pymxs import runtime as rt


# ── Property name maps per camera type ───────────────────────────────────────

# focal length property names (in priority order)
_FOCAL_PROPS = ['lens', 'focal_length', 'focal_length_mm', 'focallength', 'fov']

# near/far clip property names
_NEAR_PROPS  = ['nearClip', 'near_clip', 'nearrange', 'clipNear']
_FAR_PROPS   = ['farClip',  'far_clip',  'farrange',  'clipFar']

# DOF enable property names
_DOF_ENABLE_PROPS = ['mpassEnabled', 'dof_on', 'use_dof', 'enable_dof']

# Focus distance property names
_FOCUS_PROPS = ['mdof_focalDepth', 'targetDistance', 'focus_distance',
                'dof_focus_dist', 'focalDistance']


def _get_prop(camera, names):
    """Return the first valid property name from the list, or None."""
    for name in names:
        if rt.isProperty(camera, name):
            return name
    return None


def _set_prop(camera, names, value):
    """Set the first valid property via MXS execute — works for all camera types."""
    for name in names:
        if rt.isProperty(camera, name):
            try:
                rt.py_lens_cam = camera
                rt.py_lens_val = value
                rt.execute(f'py_lens_cam.{name} = py_lens_val')
                rt.py_lens_cam = rt.undefined
                rt.py_lens_val = rt.undefined
                return True
            except Exception:
                rt.py_lens_cam = rt.undefined
                rt.py_lens_val = rt.undefined
                continue
    return False


def _get_value(camera, names, default=None):
    """Read the first valid property value."""
    for name in names:
        if rt.isProperty(camera, name):
            try:
                return float(getattr(camera, name))
            except Exception:
                continue
    return default


# ── Public API ────────────────────────────────────────────────────────────────

def get_focal_length(camera) -> float | None:
    return _get_value(camera, _FOCAL_PROPS)


def update_focal_length(camera, focal_mm: float):
    if not (camera and rt.isValidNode(camera)):
        return
    _set_prop(camera, _FOCAL_PROPS, focal_mm)
    rt.redrawViews()


def update_clipping(camera, near: float, far: float):
    if not (camera and rt.isValidNode(camera)):
        return
    _set_prop(camera, _NEAR_PROPS, near)
    _set_prop(camera, _FAR_PROPS,  far)


def get_clipping(camera) -> tuple:
    """Return (near, far) or (None, None)."""
    near = _get_value(camera, _NEAR_PROPS)
    far  = _get_value(camera, _FAR_PROPS)
    return near, far


def update_dof(camera, enabled: bool):
    if not (camera and rt.isValidNode(camera)):
        return
    _set_prop(camera, _DOF_ENABLE_PROPS, enabled)


def update_dof_distance(camera, dist: float):
    if not (camera and rt.isValidNode(camera)):
        return
    _set_prop(camera, _FOCUS_PROPS, dist)


def get_dof_distance(camera) -> float | None:
    return _get_value(camera, _FOCUS_PROPS)


def reset_lens(camera):
    if not (camera and rt.isValidNode(camera)):
        return
    _set_prop(camera, _FOCAL_PROPS,      35.0)
    _set_prop(camera, _NEAR_PROPS,        1.0)
    _set_prop(camera, _FAR_PROPS,     10000.0)
    _set_prop(camera, _DOF_ENABLE_PROPS, False)
    rt.redrawViews()


def get_camera_info(camera) -> dict:
    """Return a dict of all readable lens properties — useful for sync and debug."""
    if not (camera and rt.isValidNode(camera)):
        return {}
    return {
        'type':          str(rt.classOf(camera)),
        'focal_length':  _get_value(camera, _FOCAL_PROPS),
        'near_clip':     _get_value(camera, _NEAR_PROPS),
        'far_clip':      _get_value(camera, _FAR_PROPS),
        'dof_enabled':   _get_value(camera, _DOF_ENABLE_PROPS),
        'focus_dist':    _get_value(camera, _FOCUS_PROPS),
    }
