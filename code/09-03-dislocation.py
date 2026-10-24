"""Defects and dislocations: Frenkel's ideal shear strength, and a Frenkel-Kontorova chain showing why a dislocation
moves at a tiny fraction of the stress needed for rigid slip."""
import math
import numpy as np


def ideal_shear_strength(G, b=1.0, a=1.0):
    """Frenkel: tau(x) = (G b / (2 pi a)) sin(2 pi x / b), so tau_max = G b / (2 pi a)."""
    return G * b / (2 * math.pi * a)


def relax(x, k, V0, F, a=1.0, steps=20000, dt=None, pinned=False):
    """Overdamped dynamics of a chain on a sinusoidal substrate under a uniform push F per atom.
    Energy: sum k/2 (x[i+1] - x[i] - a)^2 + V0/2 (1 - cos(2 pi x/a)) - F x. Free ends, or both end atoms held."""
    dt = dt or 0.4 / (k + 2 * math.pi**2 * V0)            # stable explicit step
    x = x.copy()
    for _ in range(steps):
        s = np.diff(x) - a
        f = F - V0 * math.pi / a * np.sin(2 * math.pi * x / a)
        f[:-1] += k * s; f[1:] -= k * s
        if pinned: f[0] = f[-1] = 0.0
        x += dt * f
    return x


def kink_centre(x):
    """Weighted position of the compressed bonds (spacing below 1), or None if there are none left."""
    w = np.clip(1.0 - np.diff(x), 0, None)
    return None if w.sum() < 0.3 else float(np.sum(np.arange(len(w)) * w) / w.sum())


def moves(x0, k, V0, F):
    """True if the push makes the chain slip: the kink travels more than 5 sites (or leaves),
    or, for a perfect chain, the atoms advance by more than half a spacing."""
    pinned = kink_centre(x0) is not None
    x = relax(x0, k, V0, F, pinned=pinned)
    c0, c1 = kink_centre(x0), kink_centre(x)
    if c0 is None:
        return np.mean(x - x0) > 0.5
    return c1 is None or abs(c1 - c0) > 5


def threshold(x0, k, V0, hi, n=12):
    lo = 0.0
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if moves(x0, k, V0, mid): hi = mid
        else: lo = mid
    return hi


def kinked(N, k, V0):
    """One extra atom squeezed into the middle: the 1D analogue of an edge dislocation, relaxed at zero load
    with the end atoms held (otherwise the kink simply escapes through a free end)."""
    i = np.arange(N + 1, dtype=float)                       # N + 1 atoms over N lattice sites
    x = i - (2 / math.pi) * np.arctan(np.exp((i - N / 2) / 2.0))  # displacement goes smoothly from 0 to -1 (sine-Gordon kink)
    x[-1] = N - 1.0
    return relax(x, k, V0, 0.0, pinned=True)


if __name__ == "__main__":
    G = 48e9                                    # copper
    tau_ideal = ideal_shear_strength(G)
    print(f"copper: G = {G/1e9:.0f} GPa, ideal shear strength G/(2 pi) = {tau_ideal/1e9:.2f} GPa; measured critical resolved shear stress of a pure single crystal ~ 0.5 MPa, ratio {tau_ideal/0.5e6:.0f}")
    assert tau_ideal / 0.5e6 > 1e3
    k, V0, N = 4.0, 0.2, 60                     # chain in units of the lattice spacing a = 1
    F_rigid = V0 * math.pi                      # largest substrate force per atom: a perfect chain slips only above this
    perfect = np.arange(N, dtype=float)
    assert not moves(perfect, k, V0, 0.95 * F_rigid) and moves(perfect, k, V0, 1.05 * F_rigid)
    xk = kinked(N, k, V0)
    print(f"relaxed kink: centred at site {kink_centre(xk):.1f}, tightest spacing {np.diff(xk).min():.3f}")
    F_kink = threshold(xk, k, V0, F_rigid, n=16)
    print(f"chain k = {k}, V0 = {V0}: rigid slip needs F = {F_rigid:.4f} per atom; the kink moves at F = {F_kink:.5f}, {F_rigid/F_kink:.0f} times less")
    assert F_kink < F_rigid / 20
    for k2 in (2.0, 1.0):
        F2 = threshold(kinked(N, k2, V0), k2, V0, F_rigid, n=16)
        print(f"softer springs k = {k2} (a narrower dislocation): the kink needs F = {F2:.5f}, {F_rigid/F2:.1f} times less than rigid slip")
        assert F2 > F_kink
