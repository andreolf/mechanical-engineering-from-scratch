"""Stability of equilibrium from potential energy: an inverted bar on a hinge with a rotational spring."""
import math
import numpy as np


def V(theta, k, P, L):
    """Spring energy k theta^2 / 2 plus the load's potential P L cos(theta) (it drops as the bar leans)."""
    return 0.5 * k * theta**2 + P * L * math.cos(theta)


def dV(theta, k, P, L):
    return k * theta - P * L * math.sin(theta)


def d2V(theta, k, P, L):
    return k - P * L * math.cos(theta)


def equilibria(k, P, L):
    """theta = 0 always; a leaning pair where k theta = P L sin(theta) when P L > k (bisection on (0, pi))."""
    eq = [0.0]
    if P * L > k:
        lo, hi = 1e-9, math.pi - 1e-9
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if dV(mid, k, P, L) < 0: lo = mid
            else: hi = mid
        eq += [lo, -lo]
    return eq


if __name__ == "__main__":
    k, L = 20.0, 2.0              # kN m/rad, m: critical load k / L = 10 kN
    print(f"critical load P_cr = k / L = {k / L:.1f} kN")
    for P in (8.0, 12.0):
        for th in equilibria(k, P, L):
            c = d2V(th, k, P, L)
            # second derivative by finite differences agrees with the formula
            h = 1e-4; c_num = (V(th + h, k, P, L) - 2 * V(th, k, P, L) + V(th - h, k, P, L)) / h**2
            assert abs(c - c_num) < 1e-4 and abs(dV(th, k, P, L)) < 1e-9
            # stable iff d2V > 0: a small push makes the energy rise
            pushed = V(th + 0.01, k, P, L) - V(th, k, P, L)
            assert (c > 0) == (pushed > 0)
            print(f"P = {P:4.1f} kN, theta = {math.degrees(th):8.4f} deg: V'' = {c:8.4f} -> {'stable' if c > 0 else 'unstable'}")
    # above P_cr the upright position is unstable and the bar settles at the leaning angle
    assert d2V(0, k, 12, L) < 0 and d2V(equilibria(k, 12, L)[1], k, 12, L) > 0
