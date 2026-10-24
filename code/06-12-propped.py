"""Indeterminate beams by superposition: a propped cantilever (R = 3qL/8) and a two-span continuous beam (5qL/4)."""
import numpy as np


def cumtrapz(f, x):
    return np.concatenate([[0.0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(x))])


def cantilever_w(x, M, EI):
    return cumtrapz(cumtrapz(M / EI, x), x)


if __name__ == "__main__":
    EI, L, q = 210e3 * 1.8456e7, 4000.0, 5.0       # N mm^2, mm, N/mm
    # superposition at the propped end: cantilever under q drops q L^4 / 8EI, the prop R lifts R L^3 / 3EI
    R = (q * L**4 / (8 * EI)) / (L**3 / (3 * EI))
    print(f"propped cantilever: prop reaction {R / 1e3:.4f} kN (3qL/8 = {3 * q * L / 8 / 1e3:.4f}), wall reaction {(q * L - R) / 1e3:.4f} kN")
    assert abs(R - 3 * q * L / 8) < 1e-9
    # check numerically: with that prop force the tip deflection of the cantilever is zero
    x = np.linspace(0, L, 8001)
    M = -q * (L - x) ** 2 / 2 + R * (L - x)
    w = cantilever_w(x, M, EI)
    print(f"  tip deflection with the prop: {w[-1]:.2e} mm; without it: {cantilever_w(x, -q * (L - x) ** 2 / 2, EI)[-1]:.4f} mm")
    assert abs(w[-1]) < 1e-6
    # moment redistribution: wall moment -qL^2/8, largest sagging 9qL^2/128 at 5L/8 from the wall
    print(f"  wall moment {M[0] / 1e6:.4f} kN m (-qL^2/8 = {-q * L**2 / 8 / 1e6:.4f}); max sagging {M.max() / 1e6:.4f} kN m (9qL^2/128 = {9 * q * L**2 / 128 / 1e6:.4f}) at x = {x[M.argmax()]:.0f} mm")
    assert abs(M[0] + q * L**2 / 8) < 1e-6 and abs(M.max() - 9 * q * L**2 / 128) < 1e-3
    # two equal spans L on three supports: remove the middle support, compute the gap, push it back with R
    gap = 5 * q * (2 * L) ** 4 / (384 * EI)
    Rm = gap / ((2 * L) ** 3 / (48 * EI))
    print(f"two-span beam: middle reaction {Rm / 1e3:.4f} kN (5qL/4 = {5 * q * L / 4 / 1e3:.4f}), ends {(2 * q * L - Rm) / 2 / 1e3:.4f} kN each (3qL/8)")
    assert abs(Rm - 5 * q * L / 4) < 1e-9
