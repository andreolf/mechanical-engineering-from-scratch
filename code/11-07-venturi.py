"""Bernoulli and the venturi meter: flow rate from a pressure difference, checked against a numerical integration of the 1D Euler equation."""
import math
import numpy as np

RHO = 998.0


def venturi_Q(dp, D, d, Cd=0.98):
    """Volume flow (m^3/s) from the pressure drop between inlet (D) and throat (d)."""
    A2, beta = math.pi * d * d / 4, d / D
    return Cd * A2 * math.sqrt(2 * dp / (RHO * (1 - beta ** 4)))


def euler_1d(Q, x, D_of_x, p0):
    """March rho u du/dx = -dp/dx along a duct of varying diameter (inviscid, steady, 1D)."""
    A = np.pi * D_of_x(x) ** 2 / 4; u = Q / A
    dudx = np.gradient(u, x)
    dpdx = -RHO * u * dudx
    p = p0 + np.concatenate([[0], np.cumsum((dpdx[1:] + dpdx[:-1]) / 2 * np.diff(x))])
    return u, p


if __name__ == "__main__":
    D, d = 0.100, 0.050
    dp = (13546 - RHO) * 9.81 * 0.150                       # mercury manometer reading 150 mm
    Q = venturi_Q(dp, D, d)
    print(f"manometer 150 mm Hg -> dp = {dp/1000:.3f} kPa -> Q = {Q*1000:.3f} L/s (ideal {venturi_Q(dp, D, d, 1.0)*1000:.3f} L/s)")
    # inviscid check: integrate Euler along a smooth contraction and compare with Bernoulli
    x = np.linspace(0, 0.3, 30001)
    Dx = lambda x: D - (D - d) * 0.5 * (1 - np.cos(np.pi * np.clip(x / 0.3, 0, 1)))
    Qi = venturi_Q(dp, D, d, 1.0)
    u, p = euler_1d(Qi, x, Dx, 200e3)
    bern = 200e3 + 0.5 * RHO * (u[0] ** 2 - u ** 2)
    print(f"Euler integration: pressure drop {(p[0]-p[-1])/1000:.4f} kPa; Bernoulli {(bern[0]-bern[-1])/1000:.4f} kPa; manometer {dp/1000:.4f} kPa")
    assert np.max(np.abs(p - bern)) < 5.0 and abs((p[0] - p[-1]) - dp) < 5.0
    print(f"inlet speed {u[0]:.3f} m/s, throat speed {u[-1]:.3f} m/s")
