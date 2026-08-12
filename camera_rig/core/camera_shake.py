"""Camera shake via Noise_Position controller layered on PIVOT node."""
from pymxs import runtime as rt


def install_shake(rig_nodes: dict, frequency: float = 0.5,
                  strength_x: float = 2.0, strength_y: float = 2.0,
                  strength_z: float = 1.0, seed: int = 42) -> bool:
    pivot = rig_nodes.get('pivot')
    if not (pivot and rt.isValidNode(pivot)):
        return False

    rt.py_pivot = pivot
    already = rt.execute('classOf py_pivot.pos.controller == Position_List')
    if already:
        return False

    rt.py_freq = frequency
    rt.py_sx   = float(strength_x)
    rt.py_sy   = float(strength_y)
    rt.py_sz   = float(strength_z)
    rt.py_seed = seed
    rt.execute("""
    (
        local old_ctrl = py_pivot.pos.controller
        local pos_list = Position_List()
        py_pivot.pos.controller = pos_list
        pos_list.available.controller = old_ctrl

        local noiseCtrl = Noise_Position()
        noiseCtrl.frequency = py_freq
        noiseCtrl.seed      = py_seed
        -- strength is a Point3; try both naming conventions
        try ( noiseCtrl.strength = [py_sx, py_sy, py_sz] ) catch (
            try ( noiseCtrl.X_Strength = py_sx ) catch ( donothing )
            try ( noiseCtrl.Y_Strength = py_sy ) catch ( donothing )
            try ( noiseCtrl.Z_Strength = py_sz ) catch ( donothing )
        )
        pos_list.available.controller = noiseCtrl
        pos_list.setActive pos_list.count
    )
    """)
    rt.py_pivot = rt.py_freq = rt.py_sx = rt.py_sy = rt.py_sz = rt.py_seed = rt.undefined
    rt.redrawViews()
    return True


def remove_shake(rig_nodes: dict):
    pivot = rig_nodes.get('pivot')
    if not (pivot and rt.isValidNode(pivot)):
        return
    rt.py_pivot = pivot
    rt.execute("""
    (
        if classOf py_pivot.pos.controller == Position_List do
        (
            local pl = py_pivot.pos.controller
            if pl.count >= 1 do
                py_pivot.pos.controller = pl[1].controller
        )
    )
    """)
    rt.py_pivot = rt.undefined
    rt.redrawViews()


def update_shake(rig_nodes: dict, frequency: float,
                 strength_x: float, strength_y: float, strength_z: float):
    pivot = rig_nodes.get('pivot')
    if not (pivot and rt.isValidNode(pivot)):
        return
    rt.py_pivot = pivot
    rt.py_freq  = frequency
    rt.py_sx    = float(strength_x)
    rt.py_sy    = float(strength_y)
    rt.py_sz    = float(strength_z)
    rt.execute("""
    (
        if classOf py_pivot.pos.controller == Position_List do
        (
            local pl = py_pivot.pos.controller
            for i = 1 to pl.count do
            (
                if classOf pl[i].controller == Noise_Position do
                (
                    local nc = pl[i].controller
                    nc.frequency = py_freq
                    try ( nc.strength = [py_sx, py_sy, py_sz] ) catch (
                        try ( nc.X_Strength = py_sx ) catch ( donothing )
                        try ( nc.Y_Strength = py_sy ) catch ( donothing )
                        try ( nc.Z_Strength = py_sz ) catch ( donothing )
                    )
                )
            )
        )
    )
    """)
    rt.py_pivot = rt.py_freq = rt.py_sx = rt.py_sy = rt.py_sz = rt.undefined
    rt.redrawViews()


def set_shake_seed(rig_nodes: dict, seed: int):
    pivot = rig_nodes.get('pivot')
    if not (pivot and rt.isValidNode(pivot)):
        return
    rt.py_pivot = pivot
    rt.py_seed  = seed
    rt.execute("""
    (
        if classOf py_pivot.pos.controller == Position_List do
        (
            local pl = py_pivot.pos.controller
            for i = 1 to pl.count do
            (
                if classOf pl[i].controller == Noise_Position do
                    pl[i].controller.seed = py_seed
            )
        )
    )
    """)
    rt.py_pivot = rt.py_seed = rt.undefined
    rt.redrawViews()


def is_shake_installed(rig_nodes: dict) -> bool:
    pivot = rig_nodes.get('pivot')
    if not (pivot and rt.isValidNode(pivot)):
        return False
    rt.py_pivot = pivot
    result = rt.execute('classOf py_pivot.pos.controller == Position_List')
    rt.py_pivot = rt.undefined
    return bool(result)
