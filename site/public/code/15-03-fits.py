"""ISO 286 fits from the standard tolerance formulas, and a tolerance stack-up: worst case against root-sum-square against Monte Carlo."""
import math
import numpy as np

# ISO 286 size steps up to 120 mm; the formulas use the geometric mean of each step
STEPS = [3, 6, 10, 18, 30, 50, 80, 120]


def mean_size(d):
    lo = 0
    for hi in STEPS:
        if d <= hi:
            return math.sqrt(max(lo, 1) * hi)
        lo = hi
    raise ValueError("size above 120 mm not covered")


def tol_unit(d):
    D = mean_size(d)
    return 0.45 * D ** (1 / 3) + 0.001 * D  # micrometres


def IT(grade, d):
    k = {5: 7, 6: 10, 7: 16, 8: 25, 9: 40}[grade]
    return round(k * tol_unit(d))


def shaft_limits(letter, grade, d):
    """Upper and lower deviations of a shaft (micrometres) from the ISO fundamental-deviation formulas."""
    D, t = mean_size(d), IT(grade, d)
    if letter == "g":
        es = -round(2.5 * D ** 0.34); return es, es - t
    if letter == "f":
        es = -round(5.5 * D ** 0.41); return es, es - t
    if letter == "h":
        return 0, -t
    if letter == "k":
        ei = round(0.6 * D ** (1 / 3)); return ei + t, ei
    if letter == "n":
        ei = round(5 * D ** 0.34); return ei + t, ei
    raise ValueError(letter)


def fit(hole_grade, letter, shaft_grade, d):
    """Basic-hole fit: hole H (lower deviation 0). Returns (max clearance, min clearance) in micrometres; negative = interference."""
    H = IT(hole_grade, d)
    es, ei = shaft_limits(letter, shaft_grade, d)
    return H - ei, 0 - es


def stack(nominals, tols, signs):
    nom = sum(s * n for s, n in zip(signs, nominals))
    wc = sum(tols)
    rss = math.sqrt(sum(t * t for t in tols))
    return nom, wc, rss


if __name__ == "__main__":
    d = 25
    print(f"IT6 = {IT(6, d)} um, IT7 = {IT(7, d)} um for a {d} mm diameter")
    assert (IT(6, d), IT(7, d), IT(8, d)) == (13, 21, 33)  # the ISO 286 table values for 18-30 mm
    for letter in "gkn":
        cmax, cmin = fit(7, letter, 6, d)
        kind = "clearance" if cmin >= 0 else ("interference" if cmax <= 0 else "transition")
        print(f"25 H7/{letter}6: clearance from {cmin:+d} to {cmax:+d} um -> {kind}")
    assert shaft_limits("g", 6, d) == (-7, -20) and shaft_limits("k", 6, d) == (15, 2) and shaft_limits("n", 6, d) == (28, 15)
    assert fit(7, "g", 6, d) == (41, 7)
    # bike hub: housing between locknuts minus bearing, spacer, bearing gives the axial play
    nominals, tols, signs = [50.30, 15.00, 20.00, 15.00], [0.10, 0.05, 0.08, 0.05], [1, -1, -1, -1]
    nom, wc, rss = stack(nominals, tols, signs)
    print(f"gap {nom:.2f} mm, worst case +-{wc:.3f}, RSS +-{rss:.4f}")
    assert rss <= wc
    rng = np.random.default_rng(3)
    N = 1_000_000
    parts = [rng.normal(n, t / 3, N) for n, t in zip(nominals, tols)]  # each tolerance is 3 sigma
    gap = sum(s * x for s, x in zip(signs, parts))
    out = np.mean(np.abs(gap - nom) > rss)
    print(f"Monte Carlo: gap sigma {gap.std():.5f} (RSS/3 = {rss/3:.5f}), outside RSS band {100*out:.3f}%, outside worst case {100*np.mean(np.abs(gap-nom) > wc):.5f}%")
    assert abs(gap.std() - rss / 3) < 1e-3 and abs(out - 0.0027) < 0.0005
