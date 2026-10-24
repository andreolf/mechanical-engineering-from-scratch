"""Crystal structures: build SC, BCC, FCC and HCP lattices, count neighbours, and compute packing factors two ways."""
import math
import numpy as np

BASIS = {"SC": [(0, 0, 0)], "BCC": [(0, 0, 0), (.5, .5, .5)], "FCC": [(0, 0, 0), (.5, .5, 0), (.5, 0, .5), (0, .5, .5)]}
TOUCH = {"SC": 0.5, "BCC": math.sqrt(3) / 4, "FCC": math.sqrt(2) / 4}     # atomic radius / lattice constant


def cubic_points(kind, n=3):
    pts = [np.array(b) + (i, j, k) for i in range(-n, n + 1) for j in range(-n, n + 1) for k in range(-n, n + 1) for b in BASIS[kind]]
    return np.array(pts, float)


def hcp_points(n=3, a=1.0):
    c = a * math.sqrt(8 / 3)
    a1, a2, a3 = np.array([a, 0, 0]), np.array([a / 2, a * math.sqrt(3) / 2, 0]), np.array([0, 0, c])
    basis = [np.zeros(3), a1 / 3 + a2 / 3 + a3 / 2]
    return np.array([i * a1 + j * a2 + k * a3 + b for i in range(-n, n + 1) for j in range(-n, n + 1) for k in range(-n, n + 1) for b in basis]), a, c


def coordination(pts):
    d = np.linalg.norm(pts - pts[np.argmin(np.linalg.norm(pts, axis=1))], axis=1); d = d[d > 1e-9]
    return int(np.sum(d < d.min() * (1 + 1e-6))), d.min()


def packing_mc(kind, n_samples=400000, seed=1):
    """Fraction of random points in the unit cell that fall inside an atom (atoms of touching radius)."""
    rng = np.random.default_rng(seed); P = rng.random((n_samples, 3))
    centres = cubic_points(kind, 1); R = TOUCH[kind]
    inside = np.zeros(n_samples, bool)
    for c in centres:
        inside |= np.sum((P - c)**2, axis=1) < R * R
    return inside.mean()


if __name__ == "__main__":
    for kind in ("SC", "BCC", "FCC"):
        z, dmin = coordination(cubic_points(kind))
        n_atoms = len(BASIS[kind]); R = TOUCH[kind]
        apf = n_atoms * 4 / 3 * math.pi * R**3
        mc = packing_mc(kind)
        print(f"{kind}: {n_atoms} atoms per cell, coordination {z}, nearest neighbour {dmin:.4f} a, packing factor {apf:.4f} (Monte Carlo {mc:.4f})")
        assert abs(mc - apf) < 0.005 and abs(2 * R - dmin) < 1e-12
    assert abs(4 * 4 / 3 * math.pi * (math.sqrt(2) / 4)**3 - 0.7405) < 1e-4
    pts, a, c = hcp_points()
    z, dmin = coordination(pts)
    apf_hcp = 2 * 4 / 3 * math.pi * (a / 2)**3 / (a * a * math.sqrt(3) / 2 * c)
    print(f"HCP (ideal c/a = {c/a:.4f}): coordination {z}, packing factor {apf_hcp:.4f}")
    assert z == 12 and abs(apf_hcp - math.pi / math.sqrt(18)) < 1e-12
    # densities from lattice constants
    NA = 6.02214076e23
    for name, kind, A, a_nm in (("iron (BCC)", "BCC", 55.845, 0.28665), ("copper (FCC)", "FCC", 63.546, 0.36149), ("aluminium (FCC)", "FCC", 26.982, 0.40495)):
        rho = len(BASIS[kind]) * A / NA / (a_nm * 1e-7)**3
        print(f"{name}: a = {a_nm} nm gives density {rho:.3f} g/cm^3")
