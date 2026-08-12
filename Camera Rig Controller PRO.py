#
# Camera Rig Controller - PRO
# Entry point for 3ds Max
#
import sys
import os

# Ensure the package directory is on sys.path
_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

# Force reload of all camera_rig modules so changes take effect without restarting Max
_to_remove = [k for k in sys.modules if k == 'camera_rig' or k.startswith('camera_rig.')]
for _k in _to_remove:
    del sys.modules[_k]

from camera_rig.ui.main_window import run_camera_rig_tool

run_camera_rig_tool()
