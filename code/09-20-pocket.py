"""CNC pocketing: generate a zigzag-plus-contour toolpath and G-code for a rectangular pocket, then check by simulation that it clears every point without gouging the walls."""
import math
import numpy as np

W, H, DEPTH = 40.0, 25.0, 6.0      # pocket size and depth, mm (corner at the origin)
D_TOOL = 8.0                        # flat end mill diameter
STEPOVER, STEPDOWN = 0.5 * D_TOOL, 2.0
FEED, PLUNGE = 600.0, 150.0         # mm/min


def layer_path():
    """Tool-centre path for one depth: zigzag inside the finishing contour, then the contour itself."""
    r = D_TOOL / 2
    x0, x1, y0, y1 = r, W - r, r, H - r
    pts, y, k = [], y0, 0
    while y < y1 - 1e-9:
        pts += [(x0, y), (x1, y)] if k % 2 == 0 else [(x1, y), (x0, y)]
        y = min(y + STEPOVER, y1); k += 1
    pts += [(x0, y1), (x1, y1)] if k % 2 == 0 else [(x1, y1), (x0, y1)]
    pts += [(x0, y1), (x0, y0), (x1, y0), (x1, y1), (x0, y1)]    # finishing contour
    return pts


def gcode():
    lines = ["G21 G90 G17", "G0 Z5", f"G0 X{D_TOOL/2:.3f} Y{D_TOOL/2:.3f}", "M3 S8000"]
    nlayers = math.ceil(DEPTH / STEPDOWN)
    for i in range(1, nlayers + 1):
        z = -min(i * STEPDOWN, DEPTH)
        path = layer_path()
        lines.append(f"G0 X{path[0][0]:.3f} Y{path[0][1]:.3f}")
        lines.append(f"G1 Z{z:.3f} F{PLUNGE:.0f}")
        lines += [f"G1 X{x:.3f} Y{y:.3f} F{FEED:.0f}" for x, y in path[1:]]
    lines += ["G0 Z5", "M5", "M30"]
    return lines


def simulate(path, res=0.1):
    """Mark every grid point within the tool radius of the path; return the fraction of the pocket cleared and the deepest wall intrusion."""
    xs = np.arange(res / 2, W, res); ys = np.arange(res / 2, H, res); X, Y = np.meshgrid(xs, ys)
    cut = np.zeros_like(X, dtype=bool); r = D_TOOL / 2
    for (ax, ay), (bx, by) in zip(path[:-1], path[1:]):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / L2, 0, 1) if L2 > 0 else 0
        cut |= (X - ax - t * dx) ** 2 + (Y - ay - t * dy) ** 2 <= r * r + 1e-9
    gouge = max(max(r - min(x, W - x, y, H - y) for x, y in path), 0.0)
    return cut.mean(), gouge


if __name__ == "__main__":
    path = layer_path()
    L = sum(math.dist(a, b) for a, b in zip(path[:-1], path[1:]))
    frac, gouge = simulate(path)
    print(f"one layer: {len(path)} points, {L:.1f} mm of cutting; cleared {frac*100:.3f} % of the pocket area, wall intrusion {gouge:.3f} mm")
    assert gouge < 1e-9
    # corners of a rectangular pocket cut with a round tool keep a radius = tool radius: uncut area is 4 (r^2 - pi r^2 / 4)
    r = D_TOOL / 2; corner = 4 * (r * r - math.pi * r * r / 4) / (W * H)
    print(f"expected uncut corner fraction {corner*100:.3f} %")
    assert abs((1 - frac) - corner) < 0.002
    g = gcode()
    nlay = math.ceil(DEPTH / STEPDOWN)
    t_min = nlay * (L / FEED + STEPDOWN / PLUNGE)
    print(f"{len(g)} G-code lines, {nlay} layers, about {t_min:.2f} min of feed motion")
    print("\n".join(g[:9]))
