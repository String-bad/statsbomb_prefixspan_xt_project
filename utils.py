import math
from typing import Tuple


def pitch_to_grid(x: float, y: float, nx: int, ny: int) -> Tuple[int, int]:
    '''
    Map StatsBomb 120x80 coordinates to an (nx, ny) grid (0-indexed).
    Out-of-range gets clipped into the pitch.
    '''
    x = min(max(x, 0.0), 120.0)
    y = min(max(y, 0.0), 80.0)
    gx = min(int(x / (120.0 / nx)), nx - 1)
    gy = min(int(y / (80.0 / ny)), ny - 1)
    return gx, gy


def cell_id(gx: int, gy: int, nx: int) -> int:
    return gy * nx + gx


def dist_dir(x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))  # -180..180, 0 to the right
    return d, ang


def length_bin(d: float) -> str:
    if d < 15: return "S"
    if d < 30: return "M"
    return "L"


def angle_bin(ang: float) -> str:
    # forward/back/lateral by angle
    if -45 <= ang <= 45: return "F"  # forward
    if ang >= 135 or ang <= -135: return "B"  # back
    return "L"  # lateral


def in_opposition_box(x: float, y: float, attacking_dir: int = 1) -> bool:
    '''
    Rough penalty box check.
    Attacking direction +x (1) by default; for -x, mirror.
    '''
    thresh = 102.0
    if attacking_dir == -1:
        x = 120.0 - x
    return x >= thresh and 18 <= y <= 62


def token_for_pass(pass_dict, x0, y0, x1, y1) -> str:
    d, ang = dist_dir(x0, y0, x1, y1)
    L = length_bin(d)
    A = angle_bin(ang)
    typ = ""
    try:
        ptype = pass_dict.get("type", {})
        pname = ptype.get("name", "") if isinstance(ptype, dict) else ""
        if pass_dict.get("cross") or pname == "Cross":
            typ = "X"  # cross
        elif pname == "Through Ball":
            typ = "T"
        elif pname == "Cut Back":
            typ = "C"
        else:
            if L == "L" and abs(y1 - y0) > 30:
                typ = "W"  # switch of play
    except Exception:
        pass
    return f"P{L}{A}{typ}"  # e.g., PSF, PMB, PLX...


def token_for_carry(x0, y0, x1, y1) -> str:
    d, ang = dist_dir(x0, y0, x1, y1)
    L = length_bin(d)
    A = angle_bin(ang)
    return f"K{L}{A}"  # e.g., KSF, KMB, KLL
