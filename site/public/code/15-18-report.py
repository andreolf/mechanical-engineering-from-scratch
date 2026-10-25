"""Design review: one script computes every check for a gearbox countershaft and writes a calculation report in Markdown; the report is then parsed back to prove it reproduces the numbers."""
import math
import re
import numpy as np


def design(T=150e3, n_rpm=600.0, F_gear=2000.0, F_pulley=1200.0, d=32.0, life_h=20000.0, C_bearing=19.5e3):
    """All the checks from Phase 15 for one shaft. Units: N, mm, MPa."""
    L, a1, a2 = 300.0, 100.0, 220.0
    R2 = (F_gear * a1 + F_pulley * a2) / L
    R1 = F_gear + F_pulley - R2
    M = max(R1 * a1, R2 * (L - a2))
    Sut, Kf, Kfs = 630.0, 1.7, 1.5
    Se = 4.51 * Sut ** -0.265 * 1.24 * d ** -0.107 * 0.5 * Sut
    sa = 32 * Kf * M / (math.pi * d**3)
    sm = math.sqrt(3) * 16 * Kfs * T / (math.pi * d**3)
    n_fatigue = 1 / (sa / Se + sm / Sut)
    # deep groove ball bearings at each end (C = 19.5 kN, about a 6206), life in hours at the shaft speed
    L10 = [(C_bearing / R) ** 3 * 1e6 / (n_rpm * 60) for R in (R1, R2)]
    # key 10 x 8 x 40 for the gear, 1018 cold-drawn steel (S_y = 370 MPa), design factor 2
    w, h, lk, Sy_key = 10.0, 8.0, 40.0, 370.0
    tau_key = 2 * T / (d * w * lk)
    crush = 4 * T / (d * h * lk)
    checks = [
        ("Peak bending moment", M / 1000, "N m", None, None),
        ("Endurance limit S_e", Se, "MPa", None, None),
        ("Fatigue safety factor (DE-Goodman)", n_fatigue, "-", 2.0, ">="),
        ("Bearing L10 life, left", L10[0], "h", life_h, ">="),
        ("Bearing L10 life, right", L10[1], "h", life_h, ">="),
        ("Key shear stress", tau_key, "MPa", 0.577 * Sy_key / 2, "<="),
        ("Key crushing stress", crush, "MPa", Sy_key / 2, "<="),
    ]
    return checks


def status(value, limit, sense):
    if limit is None:
        return "info"
    ok = value >= limit if sense == ">=" else value <= limit
    return "pass" if ok else "FAIL"


def report(checks, title="Countershaft design review"):
    lines = [f"# {title}", "", "| Check | Value | Unit | Limit | Status |", "|---|---|---|---|---|"]
    for name, val, unit, lim, sense in checks:
        lim_s = "" if lim is None else f"{sense} {lim:.2f}"
        lines.append(f"| {name} | {val:.2f} | {unit} | {lim_s} | {status(val, lim, sense)} |")
    fails = sum(status(v, l, s) == "FAIL" for _, v, _, l, s in checks)
    lines += ["", f"Result: {'all checks pass' if fails == 0 else f'{fails} check(s) fail'}."]
    return "\n".join(lines)


def parse(md):
    rows = re.findall(r"^\| ([^|]+?) \| ([-\d.]+) \| [^|]* \| [^|]* \| (\w+) \|$", md, re.M)
    return {name: (float(val), st) for name, val, st in rows}


if __name__ == "__main__":
    checks = design()
    md = report(checks)
    print(md)
    back = parse(md)
    assert len(back) == len(checks)
    for name, val, unit, lim, sense in checks:
        v, st = back[name]
        assert abs(v - val) <= 0.005 + 1e-9, name          # every number in the report matches the calculation
        assert st == status(val, lim, sense)
    # a weaker design must be flagged: a 28 mm shaft
    md2 = report(design(d=28.0), "28 mm variant")
    assert "FAIL" in md2 and "check(s) fail" in md2
    print("\n" + md2.splitlines()[-1].replace("Result", "28 mm variant"))
