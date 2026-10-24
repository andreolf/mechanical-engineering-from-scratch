"""Steady 1D conduction through a wall: a finite-difference solve of d/dx(k dT/dx) = 0, checked against Fourier's law."""
import numpy as np


def solve_wall(L, T_left, T_right, k_of_x, n=201):
    """Conservative FD: cell faces carry flux -k_face (T[i+1] - T[i]) / dx. Returns x, T and the flux at every face."""
    x = np.linspace(0, L, n); dx = x[1]
    kf = k_of_x((x[:-1] + x[1:]) / 2)                        # conductivity at the faces between nodes
    A = np.zeros((n, n)); b = np.zeros(n)
    A[0, 0] = A[-1, -1] = 1.0; b[0], b[-1] = T_left, T_right
    for i in range(1, n - 1):
        A[i, i - 1] = kf[i - 1]; A[i, i] = -(kf[i - 1] + kf[i]); A[i, i + 1] = kf[i]
    T = np.linalg.solve(A, b)
    q = -kf * np.diff(T) / dx
    return x, T, q


if __name__ == "__main__":
    # a 20 cm concrete wall of a Bali house: 34 C outside in the afternoon sun, 26 C in the air-conditioned room
    L, k = 0.20, 1.4
    x, T, q = solve_wall(L, 34.0, 26.0, lambda s: np.full_like(s, k))
    print(f"heat flux {q.mean():.4f} W/m^2 (Fourier k dT/L = {k*8/L:.4f}); spread along the wall {np.ptp(q):.1e}")
    lin = 34.0 + (26.0 - 34.0) * x / L
    print(f"largest departure from a straight line: {np.abs(T - lin).max():.1e} K; mid-wall {T[100]:.4f} C")
    assert np.abs(T - lin).max() < 1e-10 and np.ptp(q) < 1e-9          # homogeneous wall: linear profile, constant flux
    print(f"through 12 m^2 of wall: {q.mean()*12:.1f} W into the room")
    # a wall whose conductivity varies (damp outer half): the flux is still constant, the profile is not straight
    x, T, q = solve_wall(L, 34.0, 26.0, lambda s: np.where(s < 0.1, 2.0, 1.0))
    R = 0.1 / 2.0 + 0.1 / 1.0
    print(f"two-zone wall: flux {q.mean():.4f} W/m^2 = dT / sum(L/k) = {8/R:.4f}; temperature at the joint {T[100]:.4f} C")
    assert np.ptp(q) < 1e-9 and abs(q.mean() - 8 / R) < 1e-9
