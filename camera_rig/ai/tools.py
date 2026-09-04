"""Tool definitions for Claude API tool calling."""

CAMERA_RIG_TOOLS = [
    {
        "name": "get_camera_state",
        "description": "Read the current state of the rig and camera. Call this first to understand what's happening before making changes.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "move_dolly",
        "description": "Move the camera along the dolly track. 0% = start of track, 100% = end of track, 50% = center (default position).",
        "input_schema": {
            "type": "object",
            "properties": {
                "percent": {"type": "number", "description": "Position on track 0.0 to 100.0"}
            },
            "required": ["percent"]
        }
    },
    {
        "name": "crane_pitch",
        "description": "Tilt the crane arm up or down (X rotation). Positive = arm tilts up, negative = arm tilts down. Range: -90 to 90 degrees.",
        "input_schema": {
            "type": "object",
            "properties": {
                "angle": {"type": "number", "description": "Tilt angle in degrees (-90 to 90)"}
            },
            "required": ["angle"]
        }
    },
    {
        "name": "crane_yaw",
        "description": "Rotate the crane base left or right (Z rotation). Positive = counterclockwise, negative = clockwise. Range: -180 to 180 degrees.",
        "input_schema": {
            "type": "object",
            "properties": {
                "angle": {"type": "number", "description": "Rotation angle in degrees (-180 to 180)"}
            },
            "required": ["angle"]
        }
    },
    {
        "name": "crane_height",
        "description": "Set the crane arm height in scene units. This lifts or lowers the camera.",
        "input_schema": {
            "type": "object",
            "properties": {
                "z_value": {"type": "number", "description": "World Z height of crane arm in scene units"}
            },
            "required": ["z_value"]
        }
    },
    {
        "name": "pan_orbit",
        "description": "Pan the camera in orbit mode — rotates MASTER node so the camera sweeps left or right around its current position.",
        "input_schema": {
            "type": "object",
            "properties": {
                "angle": {"type": "number", "description": "Pan angle in degrees"}
            },
            "required": ["angle"]
        }
    },
    {
        "name": "tilt_orbit",
        "description": "Tilt the camera in orbit mode — rotates MASTER node so the camera sweeps up or down around its current position.",
        "input_schema": {
            "type": "object",
            "properties": {
                "angle": {"type": "number", "description": "Tilt angle in degrees"}
            },
            "required": ["angle"]
        }
    },
    {
        "name": "roll_camera",
        "description": "Apply a Dutch tilt (roll) to the camera. Positive = tilt right, negative = tilt left.",
        "input_schema": {
            "type": "object",
            "properties": {
                "angle": {"type": "number", "description": "Roll angle in degrees (-45 to 45)"}
            },
            "required": ["angle"]
        }
    },
    {
        "name": "set_focal_length",
        "description": "Set the camera focal length in millimeters. Lower = wider angle, higher = more telephoto. Common: 24mm wide, 35mm normal, 85mm portrait, 200mm telephoto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "focal_mm": {"type": "number", "description": "Focal length in mm (10 to 600)"}
            },
            "required": ["focal_mm"]
        }
    },
    {
        "name": "set_focus_distance",
        "description": "Set the depth of field focus distance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "distance": {"type": "number", "description": "Focus distance in scene units"}
            },
            "required": ["distance"]
        }
    },
    {
        "name": "set_dolly_keyframe",
        "description": "Set a keyframe for the dolly position at a specific frame. Use this to manually keyframe the dolly at multiple frames. Example: set 0% at frame 0, then 100% at frame 150.",
        "input_schema": {
            "type": "object",
            "properties": {
                "frame":   {"type": "integer", "description": "The frame number to set the keyframe at"},
                "percent": {"type": "number",  "description": "Dolly position at this frame (0-100)"}
            },
            "required": ["frame", "percent"]
        }
    },
    {
        "name": "bake_dolly_animation",
        "description": "Create a dolly animation with ease in/out. The dolly moves from start_percent to end_percent over the given frame range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "frame_start": {"type": "integer", "description": "Start frame"},
                "frame_end": {"type": "integer", "description": "End frame"},
                "percent_start": {"type": "number", "description": "Dolly position at start (0-100)"},
                "percent_end": {"type": "number", "description": "Dolly position at end (0-100)"},
                "ease_in": {"type": "boolean", "description": "Apply ease-in at start"},
                "ease_out": {"type": "boolean", "description": "Apply ease-out at end"}
            },
            "required": ["frame_start", "frame_end", "percent_start", "percent_end"]
        }
    },
    {
        "name": "create_orbit_track",
        "description": "Create a circular orbit track around a center point so the dolly can move in a circle around a subject.",
        "input_schema": {
            "type": "object",
            "properties": {
                "radius": {"type": "number", "description": "Orbit radius in scene units"},
                "center_x": {"type": "number", "description": "Center X (defaults to current target X)"},
                "center_y": {"type": "number", "description": "Center Y (defaults to current target Y)"}
            },
            "required": ["radius"]
        }
    },
    {
        "name": "reset_controls",
        "description": "Reset all direct controls (pan, tilt, truck, pedestal, roll) back to initial installed positions.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "reset_dolly",
        "description": "Reset the dolly to 0% and remove all dolly animation keyframes.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "reset_crane",
        "description": "Reset crane arm pitch, base rotation, and arm height back to default.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "reset_all",
        "description": "Reset everything — dolly, crane, all direct controls. Full rig reset.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "restore_straight_track",
        "description": "Remove the orbit/circle track and restore the original straight dolly track.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "set_follow_path",
        "description": "Enable or disable Follow Path on the dolly path constraint (camera aligns its direction to the track curve).",
        "input_schema": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "description": "true to enable follow, false to disable"},
                "bank":    {"type": "boolean", "description": "true to also enable banking on curves (optional)"},
                "bank_amount": {"type": "number", "description": "Bank amount 0.0-1.0 (optional, default 0.5)"}
            },
            "required": ["enabled"]
        }
    },
    {
        "name": "set_camera_shake",
        "description": "Enable or disable camera shake simulation on the pivot node.",
        "input_schema": {
            "type": "object",
            "properties": {
                "enabled":    {"type": "boolean", "description": "true to enable shake, false to remove"},
                "frequency":  {"type": "number",  "description": "Shake frequency (0.01-10, default 0.5)"},
                "strength_x": {"type": "number",  "description": "Horizontal shake strength (0-100, default 2)"},
                "strength_y": {"type": "number",  "description": "Vertical shake strength (0-100, default 2)"},
                "strength_z": {"type": "number",  "description": "Depth shake strength (0-50, default 1)"}
            },
            "required": ["enabled"]
        }
    },
    {
        "name": "set_composition_guide",
        "description": "Show or hide composition guide overlays on the camera viewport.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thirds":   {"type": "boolean", "description": "Show rule of thirds grid"},
                "golden":   {"type": "boolean", "description": "Show golden ratio lines"},
                "center":   {"type": "boolean", "description": "Show center cross"},
                "diagonal": {"type": "boolean", "description": "Show diagonal lines"},
                "triangle": {"type": "boolean", "description": "Show golden triangle"},
                "spiral":   {"type": "boolean", "description": "Show golden spiral"}
            },
            "required": []
        }
    },
    {
        "name": "set_safe_frame",
        "description": "Show or hide the safe frame overlay in the camera viewport.",
        "input_schema": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "description": "true to show safe frame, false to hide"}
            },
            "required": ["enabled"]
        }
    },
    {
        "name": "set_aspect_ratio",
        "description": "Set the render aspect ratio and show safe frame. Common presets: 2.39:1 anamorphic, 1.85:1 flat, 1.78:1 (16:9 HD), 1.33:1 (4:3).",
        "input_schema": {
            "type": "object",
            "properties": {
                "ratio": {"type": "string", "description": "Aspect ratio as string: '2.39', '1.85', '1.78', '1.33', '1.618' (golden ratio), or 'width:height' like '2390:1000'"}
            },
            "required": ["ratio"]
        }
    }
]


SYSTEM_PROMPT = """You are an AI assistant controlling a professional camera rig in Autodesk 3ds Max.

You can control:
- DOLLY: moves camera along a track (0-100%)
- CRANE ARM: tilts up/down (pitch)
- CRANE BASE: rotates left/right (yaw)
- CRANE HEIGHT: lifts camera up/down
- PAN ORBIT: sweeps camera left/right around itself
- TILT ORBIT: sweeps camera up/down around itself
- ROLL: Dutch tilt
- FOCAL LENGTH: zoom in/out
- FOCUS DISTANCE: depth of field
- DOLLY ANIMATION: bake camera movement over frames
- ORBIT TRACK: circular path around subject

CRITICAL LANGUAGE RULE — MUST FOLLOW:
- Detect the language of the user's LATEST message.
- If the latest message is in English → reply ONLY in English.
- If the latest message is in Farsi/Persian → reply ONLY in Farsi.
- Never mix languages. Match exactly what the user wrote.

IMPORTANT RULES:
1. Always call get_camera_state first if you need to know current values before adjusting.
2. After executing a tool, briefly confirm what you did in one sentence.
3. If a request is ambiguous (e.g. "move camera a bit"), make a reasonable small adjustment and describe what you did.
4. You can chain multiple tool calls to fulfill a complex request.
5. Do NOT make up values — if you don't know what value to use, call get_camera_state first.

Current rig state will be provided in each message."""
