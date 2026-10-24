"""One-dimensional collisions with a coefficient of restitution."""
import numpy as np


def collide(m1, v1, m2, v2, e):
    """Velocities after impact. Momentum is conserved; e sets the separation speed: v2' - v1' = -e (v2 - v1)."""
    p = m1 * v1 + m2 * v2
    v1n = (p - m2 * e * (v1 - v2)) / (m1 + m2)
    v2n = (p + m1 * e * (v1 - v2)) / (m1 + m2)
    return v1n, v2n


def ke(m, v):
    return 0.5 * m * v * v


if __name__ == "__main__":
    # two lab carts: 0.5 kg at 2 m/s hits 1.0 kg at rest
    m1, v1, m2, v2 = 0.5, 2.0, 1.0, 0.0
    for e in (1.0, 0.6, 0.0):
        a, b = collide(m1, v1, m2, v2, e)
        dp = (m1 * a + m2 * b) - (m1 * v1 + m2 * v2)
        loss = ke(m1, v1) + ke(m2, v2) - ke(m1, a) - ke(m2, b)
        print(f"e = {e:.1f}: v1' = {a:+.4f}, v2' = {b:+.4f} m/s, momentum change {dp:+.1e}, energy lost {loss:.4f} J")
        assert abs(dp) < 1e-12
    # energy loss formula: (1 - e^2) * reduced mass * closing speed^2 / 2
    mu = m1 * m2 / (m1 + m2)
    a, b = collide(m1, v1, m2, v2, 0.6)
    assert abs((ke(m1, v1) - ke(m1, a) - ke(m2, b)) - 0.5 * (1 - 0.36) * mu * 4) < 1e-12
    # random checks of momentum conservation
    rng = np.random.default_rng(0)
    worst = 0.0
    for _ in range(10000):
        m1, m2 = rng.uniform(0.1, 10, 2); v1, v2 = rng.uniform(-5, 5, 2); e = rng.uniform(0, 1)
        a, b = collide(m1, v1, m2, v2, e)
        worst = max(worst, abs(m1 * a + m2 * b - m1 * v1 - m2 * v2) / (abs(m1 * v1) + abs(m2 * v2)))
    print(f"10000 random collisions: worst relative momentum error {worst:.1e}")
    assert worst < 1e-12
    # a bouncing ball: each bounce keeps a fraction e of the speed, so rebound height scales with e^2
    e, h0 = 0.8, 1.0
    print("bouncing ball heights (m):", [round(h0 * e ** (2 * k), 4) for k in range(5)])
    # Newton's cradle: equal masses, e = 1, exchange velocities
    print("equal masses, e = 1:", collide(1.0, 1.0, 1.0, 0.0, 1.0))
