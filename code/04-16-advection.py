"""A pollutant pulse carried down a river: first-order upwind (monotone, diffusive) versus central differencing (oscillates)."""
import numpy as np

U, LEN = 0.5, 2000.0          # river speed m/s, reach length m


def pulse(x, x0=300.0, w=100.0):
    return np.where(np.abs(x - x0) <= w / 2, 1.0, 0.0)     # a 100 m slug of dye, concentration 1


def run(scheme, n, cfl, t_end):
    dx = LEN / n; dt = cfl * dx / U; steps = round(t_end / dt); c = U * dt / dx
    x = (np.arange(n) + 0.5) * dx
    q = pulse(x)
    for _ in range(steps):
        if scheme == "upwind":
            q = q - c * (q - np.roll(q, 1))
        elif scheme == "central":      # forward Euler in time with a centred difference: unconditionally unstable
            q = q - 0.5 * c * (np.roll(q, -1) - np.roll(q, 1))
        elif scheme == "lax-wendroff":
            q = q - 0.5 * c * (np.roll(q, -1) - np.roll(q, 1)) + 0.5 * c * c * (np.roll(q, -1) - 2 * q + np.roll(q, 1))
    return x, q, steps * dt


if __name__ == "__main__":
    n, cfl, t_end = 400, 0.8, 2000.0            # 5 m cells; the pulse travels 1000 m
    for s in ("upwind", "lax-wendroff", "central"):
        x, q, t = run(s, n, cfl, t_end)
        print(f"{s:13s}: max {q.max():.4g}, min {q.min():.4g}" + (f", total mass {q.sum() * LEN / n:.2f} (initial 100.00)" if abs(q).max() < 10 else ": blown up"))
    x, q, _ = run("upwind", n, cfl, t_end)
    assert q.min() >= -1e-12 and q.max() <= 1 + 1e-12        # monotone: no new extrema
    assert abs(q.sum() * LEN / n - 100) < 1e-6                 # conservative
    centre = (q * x).sum() / q.sum()
    print(f"upwind pulse centre at {centre:.1f} m (exact 1300.0 m)")
    assert abs(centre - 1300) < 1e-6
    # modified equation: upwind behaves like advection plus diffusion with D_num = U dx (1 - c) / 2
    dx = LEN / n; Dnum = U * dx * (1 - cfl) / 2
    var = (q * (x - centre) ** 2).sum() / q.sum()
    var_pred = 100.0**2 / 12 + 2 * Dnum * t_end
    print(f"numerical diffusivity {Dnum:.3f} m^2/s: pulse variance {var:.0f} m^2, predicted {var_pred:.0f} m^2")
    assert abs(var / var_pred - 1) < 0.02
    x, qc, _ = run("central", n, cfl, 400.0)
    assert qc.min() < -0.05                                     # central oscillates (and soon blows up)
    x, ql, _ = run("lax-wendroff", n, cfl, t_end)
    assert ql.min() < -0.01 and ql.max() > 1.0                  # second order but not monotone: over- and undershoots
