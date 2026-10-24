"""The second law: Carnot efficiency, and a numerical check that no cycle working between two temperature limits beats it."""
import math
import numpy as np


def carnot(Tc, Th):
    return 1 - Tc / Th


def cycle_efficiency(T, s):
    """Efficiency of a reversible cycle drawn as a closed polygon in the T-s plane (traversed clockwise).
    Heat in = integral of T ds where ds > 0; net work = enclosed area."""
    T = np.append(T, T[0]); s = np.append(s, s[0])
    dq = (T[1:] + T[:-1]) / 2 * np.diff(s)
    q_in = dq[dq > 0].sum(); q_out = -dq[dq < 0].sum()
    return (q_in - q_out) / q_in


if __name__ == "__main__":
    Tc, Th = 300.0, 900.0
    print(f"Carnot between {Tc:.0f} and {Th:.0f} K: {carnot(Tc, Th):.4f}")
    # the Carnot cycle itself as a rectangle in T-s
    rect = cycle_efficiency(np.array([Th, Th, Tc, Tc]), np.array([0.0, 1.0, 1.0, 0.0]))
    assert abs(rect - carnot(Tc, Th)) < 1e-12
    # random reversible cycles confined between Tc and Th: none exceeds Carnot
    rng = np.random.default_rng(0); best = 0.0
    for _ in range(20000):
        n = rng.integers(3, 12)
        ang = np.sort(rng.uniform(0, 2 * np.pi, n))[::-1]        # clockwise
        rad = rng.uniform(0.3, 1.0, n)
        s = 1 + rad * np.cos(ang)
        T = (Tc + Th) / 2 + (Th - Tc) / 2 * rad * np.sin(ang)
        eta = cycle_efficiency(T, s)
        best = max(best, eta)
        assert eta <= carnot(T.min(), T.max()) + 1e-12
    print(f"20 000 random cycles: best efficiency {best:.4f} (limit {carnot(Tc, Th):.4f})")
    # real examples
    for name, a, b in (("coal plant, 565 C steam, 25 C river", 298.15, 838.15), ("car engine, 2300 K peak, 300 K air", 300.0, 2300.0), ("geothermal, 150 C", 298.15, 423.15)):
        print(f"  {name}: Carnot limit {carnot(a, b)*100:.1f} %")
