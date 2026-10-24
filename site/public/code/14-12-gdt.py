"""GD&T basics in numbers: square versus cylindrical position zones, bonus tolerance at MMC, flatness by minimum zone, and a dimension checklist on a generated SVG drawing."""
import math
import os
import re
import tempfile
import numpy as np


def position_error(dx, dy):
    """Diameter of the position tolerance zone a measured hole needs: 2 * radial deviation."""
    return 2 * np.hypot(dx, dy)


def flatness_ls(P):
    A = np.c_[P[:, 0], P[:, 1], np.ones(len(P))]
    coef = np.linalg.lstsq(A, P[:, 2], rcond=None)[0]
    d = P[:, 2] - A @ coef
    return d.max() - d.min(), coef


def flatness_min_zone(P, coef, iters=4000, seed=0):
    """Minimum-zone flatness: the narrowest gap between two parallel planes containing all points. Search plane slopes by
    a shrinking random search starting from the least-squares plane (the zone width is convex in the slopes)."""
    rng = np.random.default_rng(seed)
    width = lambda a, b: np.ptp(P[:, 2] - a * P[:, 0] - b * P[:, 1])
    a, b = coef[0], coef[1]; best = width(a, b); step = 1e-3
    for _ in range(iters):
        ta, tb = a + rng.normal(0, step), b + rng.normal(0, step)
        w = width(ta, tb)
        if w < best: a, b, best = ta, tb, w
        else: step *= 0.995
        step = max(step, 1e-9)
    return best


def dropout_svg(path, P):
    """A minimal annotated drawing (front view) of the dropout from lesson 14.09, as SVG text."""
    R, L = P["R"], P["L"]; s = 4  # 4 px per mm
    dims = [("A", "datum A: back face"), ("B", "datum B: slot centre plane"), ("C", "datum C: axle centre")]
    notes = [f"SLOT {P['axle_d']:.2f} +0.10/+0.00", f"2x \u00d8{P['bolt_d']:.1f} THRU \u2295 \u00d80.10 \u24c2 A B C",
             f"\u00d8{P['hanger_d']:.1f} THRU \u2295 \u00d80.20 A B C", f"{L:.1f} \u00b10.05 (axle to bolt line)",
             f"{P['bolt_gap']:.1f} BASIC (bolt spacing)", f"R{R:.1f}", f"THK {P['t']:.1f} \u23e5 0.05", "MATERIAL 6061-T6", "UNLESS NOTED \u00b10.2 ISO 2768-m",
             "FIRST ANGLE PROJECTION"]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{(2*R+80)*s:.0f}" height="{(L+2*R+60)*s:.0f}">\n')
        fh.write(f'<rect x="{40*s}" y="{30*s}" width="{2*R*s}" height="{(L+2*R)*s}" rx="{R*s}" fill="none" stroke="black"/>\n')
        for i, t in enumerate(notes + [d[1] for d in dims]):
            fh.write(f'<text x="5" y="{12 + 14*i}" font-size="11">{t}</text>\n')
        fh.write("</svg>\n")


REQUIRED = [r"SLOT 12\.00 \+0\.10/\+0\.00", r"2x \u00d85\.2 THRU \u2295 \u00d80\.10 \u24c2 A B C", r"\u00d810\.0 THRU \u2295", r"45\.0 \u00b10\.05",
            r"14\.0 BASIC", r"R16\.0", r"THK 6\.0 \u23e5", r"MATERIAL", r"ISO 2768", r"FIRST ANGLE", r"datum A", r"datum B", r"datum C"]


if __name__ == "__main__":
    # 1. square (+-0.1 mm in x and y) versus cylindrical zone through its corners (diameter 0.2 sqrt 2)
    t = 0.1
    sq_area, cyl_d = (2 * t) ** 2, 2 * t * math.sqrt(2)
    cyl_area = math.pi * (cyl_d / 2) ** 2
    print(f"square zone {sq_area:.4f} mm^2; cylindrical zone diameter {cyl_d:.4f} mm, area {cyl_area:.4f} mm^2 ({100*(cyl_area/sq_area-1):.1f}% more)")
    assert abs(cyl_area / sq_area - math.pi / 2) < 1e-12
    # Monte Carlo: hole positions from a CNC with sigma = 0.045 mm per axis
    rng = np.random.default_rng(14)
    dx, dy = rng.normal(0, 0.045, 200000), rng.normal(0, 0.045, 200000)
    ok_sq = np.mean((np.abs(dx) <= t) & (np.abs(dy) <= t)); ok_cyl = np.mean(position_error(dx, dy) <= cyl_d)
    exact_sq = math.erf(t / (0.045 * math.sqrt(2))) ** 2; exact_cyl = 1 - math.exp(-(cyl_d / 2) ** 2 / (2 * 0.045 ** 2))
    print(f"pass rate: square {100*ok_sq:.2f}% (exact {100*exact_sq:.2f}%), cylindrical {100*ok_cyl:.2f}% (exact {100*exact_cyl:.2f}%)")
    assert abs(ok_sq - exact_sq) < 3e-3 and abs(ok_cyl - exact_cyl) < 3e-3 and ok_cyl > ok_sq
    # 2. bonus tolerance at MMC: a 5.2 +0.1/0 hole with position 0.10 at MMC
    for size in (5.20, 5.25, 5.30):
        print(f"  hole measured {size:.2f} mm: allowed position tolerance {0.10 + (size - 5.20):.2f} mm")
    # 3. flatness of a dropout face from 25 probe points (a slight twist plus probe noise)
    g = np.linspace(-10, 10, 5); X, Y = np.meshgrid(g, g)
    Z = 0.002 * X + 0.001 * Y + 0.0004 * X * Y / 10 + np.random.default_rng(5).normal(0, 0.003, X.shape)
    pts = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    ls, coef = flatness_ls(pts)
    mz = flatness_min_zone(pts, coef)
    print(f"flatness: least-squares band {1000*ls:.2f} um, minimum zone {1000*mz:.2f} um (spec 50 um: {'pass' if mz <= 0.05 else 'fail'})")
    assert mz <= ls + 1e-12 and mz < 0.05
    # 4. drawing checklist
    P = dict(axle_d=12.0, R=16.0, L=45.0, bolt_d=5.2, bolt_gap=14.0, hanger_d=10.0, t=6.0)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "dropout.svg"); dropout_svg(path, P)
        text = open(path, encoding="utf-8").read()
    missing = [r for r in REQUIRED if not re.search(r, text)]
    print(f"drawing checklist: {len(REQUIRED) - len(missing)} of {len(REQUIRED)} required items present")
    assert not missing
    # the checker catches a drawing where someone forgot the bolt spacing
    broken = text.replace("14.0 BASIC", "")
    assert [r for r in REQUIRED if not re.search(r, broken)] == [r"14\.0 BASIC"]
