"""A parametric bike dropout: a feature tree of 2D booleans driven by a parameter table, rebuilt over a parameter sweep with design-rule checks."""
import csv
import io
import math
import numpy as np

PARAMS_CSV = """name,value,unit,comment
axle_d,12.0,mm,thru-axle diameter (10 for quick release)
R,16.0,mm,outer radius of the plate around the axle
L,45.0,mm,distance from the axle to the frame mount
bolt_d,5.2,mm,clearance for M5 frame bolts
bolt_gap,14.0,mm,spacing of the two frame bolts
hanger_d,10.0,mm,derailleur hanger boss hole
t,6.0,mm,plate thickness
rho,2.70,g/cm3,aluminium 6061
t_min,4.0,mm,minimum wall anywhere
"""


def read_params(text):
    return {row["name"]: float(row["value"]) for row in csv.DictReader(io.StringIO(text))}


# 2D signed distances (negative inside)
def circle(c, r): return lambda x, y: np.hypot(x - c[0], y - c[1]) - r
def stadium(a, b, r):
    """All points within r of the segment ab."""
    a, b = np.array(a, float), np.array(b, float); d = b - a; L2 = d @ d
    def f(x, y):
        t = np.clip(((x - a[0]) * d[0] + (y - a[1]) * d[1]) / L2, 0, 1)
        return np.hypot(x - a[0] - t * d[0], y - a[1] - t * d[1]) - r
    return f
def cut(f, g): return lambda x, y: np.maximum(f(x, y), -g(x, y))


def build(P):
    """Feature tree: plate -> pocket the axle slot (open towards -y) -> two frame-bolt holes -> hanger hole."""
    mount = (0.0, P["L"])
    feats = [("plate", stadium((0, 0), mount, P["R"]))]
    feats.append(("slot", stadium((0, 0), (0, -P["R"] - 5), P["axle_d"] / 2)))    # runs out through the bottom edge
    b1, b2 = (-P["bolt_gap"] / 2, P["L"]), (P["bolt_gap"] / 2, P["L"])
    feats += [("bolt1", circle(b1, P["bolt_d"] / 2)), ("bolt2", circle(b2, P["bolt_d"] / 2))]
    hanger = (0.0, P["L"] / 2)
    feats.append(("hanger", circle(hanger, P["hanger_d"] / 2)))
    f = feats[0][1]
    for _, g in feats[1:]:
        f = cut(f, g)
    return f, dict(b1=b1, b2=b2, hanger=hanger, mount=mount)


def design_rules(P, geo):
    """Minimum ligaments: distances between hole edges and the outer edge, and between holes."""
    plate = stadium((0, 0), geo["mount"], P["R"])
    issues = []
    for name, c, d in (("bolt1", geo["b1"], P["bolt_d"]), ("bolt2", geo["b2"], P["bolt_d"]), ("hanger", geo["hanger"], P["hanger_d"])):
        wall = -plate(*c) - d / 2
        if wall < P["t_min"]: issues.append(f"{name} wall {wall:.2f} mm")
    # between the hanger hole and the slot (the slot is the segment from (0, 0) downwards, radius axle_d / 2)
    hx, hy = geo["hanger"]
    gap = (math.hypot(hx, hy) if hy > 0 else abs(hx)) - P["hanger_d"] / 2 - P["axle_d"] / 2
    if gap < P["t_min"]: issues.append(f"hanger to slot {gap:.2f} mm")
    if P["bolt_gap"] - P["bolt_d"] < P["t_min"]: issues.append("bolts too close")
    return issues


def area_grid(f, box, h=0.05):
    xs = np.arange(box[0] + h / 2, box[1], h); ys = np.arange(box[2] + h / 2, box[3], h)
    X, Y = np.meshgrid(xs, ys)
    return np.count_nonzero(f(X, Y) < 0) * h * h


def area_exact(P):
    R, L, s = P["R"], P["L"], P["axle_d"]
    plate = 2 * R * L + math.pi * R * R
    a = s / 2                                         # the slot runs from the axle down through the round bottom edge:
    slot = a * math.sqrt(R * R - a * a) + R * R * math.asin(a / R) + math.pi * a * a / 2   # integral of sqrt(R^2 - x^2) over |x| < a, plus the round end
    holes = 2 * math.pi * (P["bolt_d"] / 2) ** 2 + math.pi * (P["hanger_d"] / 2) ** 2
    return plate - slot - holes


if __name__ == "__main__":
    P = read_params(PARAMS_CSV)
    f, geo = build(P)
    box = (-P["R"] - 1, P["R"] + 1, -P["R"] - 1, P["L"] + P["R"] + 1)
    A, Ae = area_grid(f, box), area_exact(P)
    m = Ae * P["t"] / 1000 * P["rho"]
    print(f"dropout: area {A:.2f} mm^2 on a 0.05 mm grid, exact {Ae:.2f} mm^2; mass {m:.2f} g; rule issues {design_rules(P, geo)}")
    assert abs(A - Ae) < 0.003 * Ae and not design_rules(P, geo)
    # parameter sweep: every combination must rebuild and pass the rules, and the area must stay exact
    ok = 0
    for axle in (10.0, 12.0, 15.0):
        for R in (16.0, 18.0, 20.0):
            for L in (40.0, 45.0, 50.0):
                Q = dict(P, axle_d=axle, R=R, L=L)
                fq, gq = build(Q)
                bq = (-R - 1, R + 1, -R - 1, L + R + 1)
                Aq = area_grid(fq, bq, 0.1)
                assert abs(Aq - area_exact(Q)) < 0.006 * area_exact(Q), (axle, R, L)
                issues = design_rules(Q, gq)
                ok += not issues
                if issues: print(f"  axle {axle}, R {R}, L {L}: {issues}")
    print(f"sweep: 27 rebuilds, all areas match; {ok} pass the design rules")
    # a deliberately bad parameter set is caught
    bad = dict(P, R=12.0, bolt_gap=20.0)
    print(f"R = 12 mm with the bolts 20 mm apart: {design_rules(bad, build(bad)[1])}")
    assert design_rules(bad, build(bad)[1])
