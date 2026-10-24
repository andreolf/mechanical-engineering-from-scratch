"""Shear force and bending moment diagrams by integrating dV/dx = -q and dM/dx = V along the beam."""
import numpy as np


def vm_simply_supported(L, points=(), q=0.0, n=6001):
    """Pin at 0, roller at L. Point loads (a, P) downward, uniform load q downward. Returns x, V, M."""
    x = np.linspace(0, L, n)
    Rb = (sum(P * a for a, P in points) + q * L * L / 2) / L
    Ra = sum(P for _, P in points) + q * L - Rb
    # equilibrium of the part to the left of a cut at x
    V = Ra - q * x - sum(P * (x > a) for a, P in points)
    M = Ra * x - q * x**2 / 2 - sum(P * np.maximum(x - a, 0) for a, P in points)
    return x, V, M, Ra, Rb


def vm_cantilever(L, P_tip=0.0, q=0.0, n=6001):
    """Clamped at x = 0, free at L. Closed form from equilibrium of the part to the right of x."""
    x = np.linspace(0, L, n)
    V = P_tip + q * (L - x)
    M = -P_tip * (L - x) - q * (L - x) ** 2 / 2
    return x, V, M


if __name__ == "__main__":
    L, P = 6.0, 30.0
    x, V, M, Ra, Rb = vm_simply_supported(L, points=[(L / 2, P)])
    print(f"central point load: Ra = {Ra:.1f}, Rb = {Rb:.1f} kN, M_max = {M.max():.4f} kN m (PL/4 = {P * L / 4:.1f})")
    assert abs(M.max() - P * L / 4) < 1e-6 and abs(M[-1]) < 1e-6        # M returns to zero at the roller
    q = 8.0
    x, V, M, Ra, Rb = vm_simply_supported(L, q=q)
    print(f"uniform load: M_max = {M.max():.4f} kN m at x = {x[M.argmax()]:.3f} m (qL^2/8 = {q * L * L / 8:.1f})")
    assert abs(M.max() - q * L * L / 8) < 1e-6
    # the slope of M is V (dM/dx = V) and the slope of V is -q: check both by finite differences
    assert np.allclose(np.gradient(M, x, edge_order=2), V, atol=1e-8) and np.allclose(np.gradient(V, x, edge_order=2), -q, atol=1e-8)
    # and integrating V from 0 gives M back (trapezoid rule)
    Mi = np.concatenate([[0.0], np.cumsum((V[1:] + V[:-1]) / 2 * np.diff(x))])
    assert np.allclose(Mi, M, atol=1e-9)
    # footbridge: 20 kN at 2 m plus 5 kN/m: where is the largest moment? where V crosses zero
    x, V, M, Ra, Rb = vm_simply_supported(L, points=[(2.0, 20.0)], q=5.0)
    k = M.argmax()
    print(f"mixed loads: Ra = {Ra:.4f}, Rb = {Rb:.4f} kN, M_max = {M[k]:.4f} kN m at x = {x[k]:.4f} m (V changes sign there)")
    assert abs(Rb - (20 * 2 + 5 * 18) / 6) < 1e-12 and V[k - 2] > 0 > V[k + 2]
    # cantilever balcony: 2 kN/m plus 1.5 kN at the tip, 1.8 m long
    x, V, M = vm_cantilever(1.8, P_tip=1.5, q=2.0)
    print(f"cantilever: root shear {V[0]:.2f} kN, root moment {M[0]:.3f} kN m")
    assert abs(M[0] + (1.5 * 1.8 + 2 * 1.8 ** 2 / 2)) < 1e-12
