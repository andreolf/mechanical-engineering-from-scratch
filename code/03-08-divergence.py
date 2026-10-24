"""Flux through surfaces, numerical divergence, and the divergence theorem."""
import math
import numpy as np


def divergence(F, p, h=1e-5):
    p = np.asarray(p, float)
    return sum((F(*(p + h * e))[i] - F(*(p - h * e))[i]) / (2 * h) for i, e in enumerate(np.eye(len(p))))


def flux_sphere(F, R, n=400):
    """Midpoint rule on (phi, theta) with dA = R^2 sin(phi) dphi dtheta."""
    hp, ht = math.pi / n, 2 * math.pi / n
    phi = hp * (np.arange(n) + 0.5); th = ht * (np.arange(n) + 0.5)
    P, T = np.meshgrid(phi, th)
    nx, ny, nz = np.sin(P) * np.cos(T), np.sin(P) * np.sin(T), np.cos(P)
    Fx, Fy, Fz = F(R * nx, R * ny, R * nz)
    return np.sum((Fx * nx + Fy * ny + Fz * nz) * R ** 2 * np.sin(P)) * hp * ht


if __name__ == "__main__":
    F = lambda x, y, z: (x, y, z)
    flux = flux_sphere(F, 2.0)
    print(f"flux of (x, y, z) out of a sphere of radius 2: {flux:.5f}, 32 pi = {32 * math.pi:.5f}")
    assert abs(flux - 32 * math.pi) < 1e-3 and abs(divergence(F, [0.3, -1, 2]) - 3) < 1e-8
    # a field with varying divergence: G = (x^3, y^3, z^3), div = 3 r^2, total = 3 * 4 pi R^5 / 5
    G = lambda x, y, z: (x ** 3, y ** 3, z ** 3)
    assert abs(flux_sphere(G, 1.5) - 12 * math.pi * 1.5 ** 5 / 5) < 1e-2
    # pipe flow rate: integrate the parabolic profile in polar coordinates
    R, umax = 0.01, 0.4
    r = np.linspace(0, R, 100001); u = umax * (1 - (r / R) ** 2)
    Q = 2 * math.pi * np.trapezoid(u * r, r)
    print(f"pipe flow Q = {Q*6e4:.3f} L/min, mean velocity {Q/(math.pi*R**2):.4f} m/s")
    assert abs(Q - math.pi / 2 * umax * R ** 2) < 1e-12
    # an incompressible 2D flow has zero divergence: stagnation flow u = (x, -y, 0)
    rng = np.random.default_rng(13)
    for p in rng.uniform(-1, 1, (20, 3)):
        assert abs(divergence(lambda x, y, z: (x, -y, 0 * z), p)) < 1e-8
