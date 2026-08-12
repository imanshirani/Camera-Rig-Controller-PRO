"""Vertigo (Dolly Zoom) effect — simultaneous dolly movement and focal length change."""
import math
from pymxs import runtime as rt


def compute_focal_for_distance(reference_focal: float, reference_dist: float,
                                new_dist: float) -> float:
    """Compute the focal length needed at new_dist to keep the same angular subject size.

    Holds focal / distance = constant.
    """
    if new_dist <= 0:
        return reference_focal
    return reference_focal * new_dist / reference_dist


def preview_vertigo(reference_focal: float, subject_dist: float,
                    dolly_offset: float, sensor_width: float = 36.0) -> dict:
    """Return preview values for Vertigo effect without baking.

    dolly_offset: positive = moving away from subject (pull out)
                  negative = moving toward subject (push in)

    Returns dict with 'focal_at_end' and 'fov_at_end'.
    """
    new_dist = subject_dist + dolly_offset
    focal_end = compute_focal_for_distance(reference_focal, subject_dist, new_dist)
    fov_end = math.degrees(2.0 * math.atan((sensor_width / 2.0) / focal_end)) if focal_end > 0 else 0.0
    return {'focal_at_end': focal_end, 'fov_at_end': fov_end}


def bake_vertigo(camera, path_ctrl, subject_dist: float,
                 dolly_start_pct: float, dolly_end_pct: float,
                 frame_start: int, frame_end: int,
                 direction: str = "pull_out"):
    """Bake a Dolly Zoom (Vertigo) effect.

    direction: "push_in"  = dolly moves toward subject (pct increases), zoom out (focal decreases)
               "pull_out" = dolly moves away from subject (pct decreases), zoom in (focal increases)

    Bakes one key per frame for smooth interpolation.
    """
    if frame_end <= frame_start:
        return
    if subject_dist <= 0:
        return

    total_frames = frame_end - frame_start
    reference_focal = float(camera.lens) if rt.isProperty(camera, 'lens') else 35.0

    # For pull_out: dolly moves from dolly_start_pct → dolly_end_pct (moving away → focal increases)
    # For push_in:  dolly moves from dolly_end_pct → dolly_start_pct (moving closer → focal decreases)
    if direction == "push_in":
        pct_range = dolly_end_pct - dolly_start_pct
    else:
        pct_range = dolly_end_pct - dolly_start_pct

    rt.py_cam       = camera
    rt.py_path_ctrl = path_ctrl
    rt.py_subj_dist = subject_dist
    rt.py_ref_focal = reference_focal
    rt.py_pct_start = dolly_start_pct
    rt.py_pct_range = pct_range
    rt.py_f_start   = frame_start
    rt.py_f_total   = total_frames

    rt.execute("""
    (
        for i = 0 to py_f_total do
        (
            local t = py_f_start + i
            local alpha = if py_f_total > 0 then (i as float / py_f_total) else 0.0
            local cur_pct = py_pct_start + alpha * py_pct_range

            -- dolly offset relative to start (positive = moved further from subject)
            local dolly_offset = alpha * py_pct_range * 10.0  -- scale factor: 1% path ~ 10 units

            local new_dist = py_subj_dist + dolly_offset
            if new_dist < 1.0 do new_dist = 1.0

            local new_focal = py_ref_focal * new_dist / py_subj_dist

            with animate on
            (
                at time t py_path_ctrl.percent = cur_pct
                at time t py_cam.lens = new_focal
            )
        )
    )
    """)

    rt.py_cam = rt.py_path_ctrl = rt.undefined
    rt.py_subj_dist = rt.py_ref_focal = rt.undefined
    rt.py_pct_start = rt.py_pct_range = rt.undefined
    rt.py_f_start   = rt.py_f_total   = rt.undefined
    rt.redrawViews()
