"""Viewport framing — aspect ratio, safe frame, and composition guide overlays."""
from pymxs import runtime as rt


# ── Aspect Ratio Presets ─────────────────────────────────────────────────────

ASPECT_PRESETS = {
    "2.39:1 (Anamorphic Scope)":       (2390, 1000),
    "2.35:1 (Anamorphic Classic)":     (2350, 1000),
    "1.85:1 (Flat / US Widescreen)":   (1850, 1000),
    "1.78:1 (16:9 HD)":                (1920, 1080),
    "1.66:1 (European Widescreen)":    (1660, 1000),
    "1.43:1 (IMAX)":                   (1430, 1000),
    "1.33:1 (4:3 Classic / Academy)":  (1440, 1080),
    "1:1 (Square / Instagram)":        (1080, 1080),
    "9:16 (Vertical / Mobile)":        (1080, 1920),
    "1.618:1 (Golden Ratio — φ)":      (1618, 1000),
    "1.272:1 (Golden Root — √φ)":      (1272, 1000),
    "2.058:1 (Golden Square — φ²)":    (2058, 1000),
}

CINEMA_PRESETS = [k for k in ASPECT_PRESETS if "Golden" not in k]
GOLDEN_PRESETS = [k for k in ASPECT_PRESETS if "Golden" in k]

# Default colors (R, G, B) per guide key
GUIDE_DEFAULTS = {
    'thirds':   (255, 220,   0),   # yellow
    'golden':   (255, 140,   0),   # orange
    'center':   (  0, 200, 220),   # cyan
    'diag':     (220,  50,  50),   # red
    'triangle': (  0, 220, 130),   # teal
    'spiral':   (255, 255, 255),   # white
}


# ── Core functions ────────────────────────────────────────────────────────────

def set_safe_frame(enabled: bool):
    val = "true" if enabled else "false"
    rt.execute(f'displaySafeFrames = {val}')
    rt.redrawViews()


def set_aspect_ratio(width: int, height: int):
    rt.renderWidth  = width
    rt.renderHeight = height
    rt.redrawViews()


def get_current_aspect() -> str:
    w = int(rt.renderWidth)
    h = int(rt.renderHeight)
    if h == 0:
        return "N/A"
    return f"{w / h:.2f}:1  ({w}×{h})"


# ── Composition Guide Overlay ─────────────────────────────────────────────────
#
# Technique from ImageCompHelper v2.55 by Warren Wnuk (TheFactionCGI):
# compute render-area fieldX/fieldY/offsetX/offsetY, then use gw.wPolyline
# in screen-pixel space.  registerRedrawViewsCallback fires every redraw.


def _build_mxs_callback() -> str:
    """MXS callback string: helper functions + main CameraRigDrawGuides fn."""
    return r"""
-- ── Golden Spiral helper ──────────────────────────────────────────────────
fn CameraRigSpiral fX fY oX oY col =
(
    local phi    = 1.61803398875
    local spW    = 0.0   -- spiral width  (renamed: gW conflicts with gw global)
    local spH    = 0.0   -- spiral height (renamed: gH is fine but kept consistent)
    if (fX / fY) >= phi then ( spW = fY * phi; spH = fY )
    else ( spW = fX; spH = fX / phi )

    local x1 = oX + (fX - spW) * 0.5
    local y1 = oY + (fY - spH) * 0.5
    local x2 = x1 + spW
    local y2 = y1 + spH

    gw.setColor #line col
    gw.wPolyline #([x1,y1,0],[x2,y1,0],[x2,y2,0],[x1,y2,0]) true

    local sideLen = 0.0
    local arcCX   = 0.0
    local arcCY   = 0.0
    local angA    = 0.0
    local angB    = 0.0
    local pts     = #()

    for step = 0 to 7 do
    (
        local ori = mod step 4
        case ori of
        (
            0: (sideLen=y2-y1; arcCX=x2-sideLen; arcCY=y1;          angA=0.0;   angB=90.0;
                gw.wPolyline #([arcCX,y1,0],[arcCX,y2,0]) true; x2=arcCX)
            1: (sideLen=x2-x1; arcCX=x2;          arcCY=y2-sideLen; angA=90.0;  angB=180.0;
                gw.wPolyline #([x1,arcCY,0],[x2,arcCY,0]) true; y2=arcCY)
            2: (sideLen=y2-y1; arcCX=x1+sideLen;  arcCY=y2;         angA=180.0; angB=270.0;
                gw.wPolyline #([arcCX,y1,0],[arcCX,y2,0]) true; x1=arcCX)
            3: (sideLen=x2-x1; arcCX=x1;           arcCY=y1+sideLen;angA=270.0; angB=360.0;
                gw.wPolyline #([x1,arcCY,0],[x2,arcCY,0]) true; y1=arcCY)
        )
        pts = #()
        for j = 0 to 16 do
        (
            local ang = angA + (j as float) * (angB - angA) / 16.0
            append pts [arcCX + sideLen * cos(ang), arcCY + sideLen * sin(ang), 0]
        )
        if pts.count > 1 do gw.wPolyline pts false
    )
)

-- ── Golden Triangle helper ─────────────────────────────────────────────────
fn CameraRigTriangle fX fY oX oY col =
(
    -- Based on ImageCompHelper by Warren Wnuk (TheFactionCGI)
    gw.setColor #line col
    local c1    = sqrt(fX^2.0 + fY^2.0)
    local h1    = (fY * fX) / c1
    local c2    = sqrt(abs(fX^2.0 - h1^2.0))
    local ratio = c2 / c1

    -- Diagonal 1: bottom-left → top-right
    local d1a = [oX,      fY+oY, 0]
    local d1b = [fX+oX,   oY,    0]
    gw.wPolyline #(d1a, d1b) true
    local pt1 = d1a + (d1b - d1a) * ratio
    local pt2 = d1a + (d1b - d1a) * (1.0 - ratio)
    gw.wPolyline #([fX+oX, fY+oY, 0], pt1) false
    gw.wPolyline #([oX,    oY,    0], pt2) false

    -- Diagonal 2: top-left → bottom-right (mirrored)
    local d2a = [oX,    oY,    0]
    local d2b = [fX+oX, fY+oY, 0]
    gw.wPolyline #(d2a, d2b) true
    local pt3 = d2a + (d2b - d2a) * ratio
    local pt4 = d2a + (d2b - d2a) * (1.0 - ratio)
    gw.wPolyline #([fX+oX, oY,    0], pt3) false
    gw.wPolyline #([oX,    fY+oY, 0], pt4) false
)

-- ── Main callback ──────────────────────────────────────────────────────────
fn CameraRigDrawGuides =
(
    -- Compute render area within viewport (letterbox / pillarbox)
    -- Technique: ImageCompHelper v2.55, Warren Wnuk
    local winX   = gw.getWinSizeX() as float
    local winY   = gw.getWinSizeY() as float
    local winAsp = winX / winY
    local renAsp = renderWidth as float / renderHeight as float
    local fieldX = 0.0; local fieldY = 0.0
    local offsetX = 0.0; local offsetY = 0.0

    if winAsp > renAsp then
    (
        local factor = winY / renderHeight
        fieldY  = winY; fieldX  = factor * renderWidth
        offsetX = (winX - fieldX) / 2.0 + 1; offsetY = 0.0
    ) else (
        local factor = winX / renderWidth
        fieldX  = winX; fieldY  = factor * renderHeight
        offsetX = 0.0; offsetY = (winY - fieldY) / 2.0 + 1
    )

    -- Rule of Thirds
    if py_guide_thirds do
    (
        gw.setColor #line py_col_thirds
        local b3 = fieldX / 3.0; local h3 = fieldY / 3.0
        gw.wPolyline #([b3+offsetX,   offsetY, 0], [b3+offsetX,   fieldY+offsetY-1, 0]) true
        gw.wPolyline #([2*b3+offsetX, offsetY, 0], [2*b3+offsetX, fieldY+offsetY-1, 0]) true
        gw.wPolyline #([offsetX, h3+offsetY,   0], [fieldX+offsetX-1, h3+offsetY,   0]) true
        gw.wPolyline #([offsetX, 2*h3+offsetY, 0], [fieldX+offsetX-1, 2*h3+offsetY, 0]) true
    )

    -- Golden Ratio Lines
    if py_guide_golden do
    (
        gw.setColor #line py_col_golden
        local gldX = fieldX / 1.618; local gldY = fieldY / 1.618
        gw.wPolyline #([gldX+offsetX,         offsetY, 0], [gldX+offsetX,         fieldY+offsetY-1, 0]) true
        gw.wPolyline #([fieldX-gldX+offsetX,  offsetY, 0], [fieldX-gldX+offsetX,  fieldY+offsetY-1, 0]) true
        gw.wPolyline #([offsetX, gldY+offsetY,         0], [fieldX+offsetX-1, gldY+offsetY,         0]) true
        gw.wPolyline #([offsetX, fieldY-gldY+offsetY,  0], [fieldX+offsetX-1, fieldY-gldY+offsetY,  0]) true
    )

    -- Center Cross
    if py_guide_center do
    (
        gw.setColor #line py_col_center
        gw.wPolyline #([fieldX/2+offsetX, offsetY,          0], [fieldX/2+offsetX, fieldY+offsetY-1, 0]) true
        gw.wPolyline #([offsetX,          fieldY/2+offsetY, 0], [fieldX+offsetX-1, fieldY/2+offsetY, 0]) true
    )

    -- Diagonals
    if py_guide_diag do
    (
        gw.setColor #line py_col_diag
        gw.wPolyline #([offsetX,        offsetY,        0], [fieldX+offsetX, fieldY+offsetY, 0]) true
        gw.wPolyline #([offsetX,        fieldY+offsetY, 0], [fieldX+offsetX, offsetY,        0]) true
    )

    -- Golden Triangle
    if py_guide_triangle do
        CameraRigTriangle fieldX fieldY offsetX offsetY py_col_triangle

    -- Golden Spiral
    if py_guide_spiral do
        CameraRigSpiral fieldX fieldY offsetX offsetY py_col_spiral

    gw.enlargeUpdateRect #whole
    gw.updateScreen()
)
"""


def install_overlay():
    """Register the MXS redraw callback with per-guide color globals."""
    # Set all globals unconditionally on (re)install
    for key, (r, g, b) in GUIDE_DEFAULTS.items():
        setattr(rt, f'py_col_{key}', rt.color(r, g, b))

    for var in ('py_guide_thirds', 'py_guide_golden', 'py_guide_center',
                'py_guide_diag', 'py_guide_triangle', 'py_guide_spiral'):
        if getattr(rt, var, None) is None:
            setattr(rt, var, False)

    rt.execute(_build_mxs_callback())
    rt.execute("""
    (
        try(unregisterRedrawViewsCallback CameraRigDrawGuides)catch(donothing)
        try(unregisterRedrawViewsCallback CameraRigSpiral)catch(donothing)
        try(unregisterRedrawViewsCallback CameraRigTriangle)catch(donothing)
        registerRedrawViewsCallback CameraRigDrawGuides
    )
    """)


def uninstall_overlay():
    """Unregister the MXS redraw callback."""
    rt.execute('try(unregisterRedrawViewsCallback CameraRigDrawGuides)catch(donothing)')
    rt.redrawViews()


def set_guide(thirds=None, golden=None, center=None, diag=None,
              triangle=None, spiral=None):
    """Enable/disable individual guides. Pass None to leave unchanged."""
    if thirds   is not None: rt.py_guide_thirds   = thirds
    if golden   is not None: rt.py_guide_golden   = golden
    if center   is not None: rt.py_guide_center   = center
    if diag     is not None: rt.py_guide_diag     = diag
    if triangle is not None: rt.py_guide_triangle = triangle
    if spiral   is not None: rt.py_guide_spiral   = spiral
    rt.redrawViews()


def set_guide_color(guide_key: str, r: int, g: int, b: int):
    """Set color for a specific guide.
    guide_key: 'thirds' | 'golden' | 'center' | 'diag' | 'triangle' | 'spiral'
    """
    setattr(rt, f'py_col_{guide_key}', rt.color(r, g, b))
    rt.redrawViews()


def any_guide_active() -> bool:
    return any(
        bool(getattr(rt, f'py_guide_{k}', False))
        for k in ('thirds', 'golden', 'center', 'diag', 'triangle', 'spiral')
    )
