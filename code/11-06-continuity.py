"""Conservation of mass: divergence of discrete velocity fields, and equal flow rate through every section of a contraction."""
import numpy as np


def divergence(u, v, dx, dy):
    """Central-difference divergence on the interior of a grid (arrays indexed [j, i] = [y, x])."""
    return (u[1:-1, 2:] - u[1:-1, :-2]) / (2 * dx) + (v[2:, 1:-1] - v[:-2, 1:-1]) / (2 * dy)


def net_outflow(u, v, x, y):
    """Line integral of u . n around the grid boundary (trapezoidal rule)."""
    tr = lambda f, s: float(np.sum((f[1:] + f[:-1]) / 2 * np.diff(s)))
    return tr(u[:, -1], y) - tr(u[:, 0], y) + tr(v[-1, :], x) - tr(v[0, :], x)


if __name__ == "__main__":
    x = np.linspace(-1, 1, 81); y = np.linspace(-1, 1, 81); X, Y = np.meshgrid(x, y); dx = x[1] - x[0]
    fields = {"stagnation u = x, v = -y": (X, -Y),
              "vortex u = -y, v = x": (-Y, X),
              "expanding u = x, v = y": (X, Y)}
    for name, (u, v) in fields.items():
        d = divergence(u, v, dx, dx)
        print(f"{name}: max |div u| = {np.abs(d).max():.2e}, net outflow through the square {net_outflow(u, v, x, y):.4f}")
    assert np.abs(divergence(X, -Y, dx, dx)).max() < 1e-12 and abs(net_outflow(X, -Y, x, y)) < 1e-12
    assert abs(net_outflow(X, Y, x, y) - 2 * 4) < 1e-9            # divergence 2 times area 4 (Gauss)
    # a water main contracting from 300 mm to 150 mm and back to 200 mm, 70 L/s
    Q = 0.070
    for D in (0.300, 0.150, 0.200):
        A = np.pi * D * D / 4; V = Q / A
        print(f"  D = {D*1000:.0f} mm: area {A*1e4:.2f} cm^2, mean speed {V:.3f} m/s, flow rate {A*V*1000:.1f} L/s")
        assert abs(A * V - Q) < 1e-15
    print(f"halving the diameter multiplies the speed by {(0.3/0.15)**2:.0f}")
