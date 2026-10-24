"""Welding heat flow: Rosenthal's moving point source on a thick plate, the weld pool size, and the 800 to 500 C cooling time that sets the weld's hardness."""
import math
import numpy as np

K, RHO, CP = 40.0, 7850.0, 600.0     # steel, W/(m K), kg/m^3, J/(kg K)
ALPHA = K / (RHO * CP)
TM = 1510.0


def T(xi, y, z, q, v, T0=20.0):
    """Temperature in the frame moving with the arc (xi along the travel direction, positive ahead)."""
    r = math.sqrt(xi * xi + y * y + z * z)
    return T0 + q / (2 * math.pi * K * r) * math.exp(-v * (xi + r) / (2 * ALPHA))


def pool_length(q, v, T0=20.0):
    """Melt-pool extent behind and ahead of the arc on the centreline (bisection on T = TM)."""
    def find(sign):
        lo, hi = 1e-7, 0.2
        for _ in range(100):
            m = (lo + hi) / 2
            if T(sign * m, 0, 0, q, v, T0) > TM: lo = m
            else: hi = m
        return (lo + hi) / 2
    return find(-1), find(1)


def t85(q, v, T0=20.0):
    """Thick-plate cooling time from 800 to 500 C on the weld centreline."""
    return q / v / (2 * math.pi * K) * (1 / (500 - T0) - 1 / (800 - T0))


if __name__ == "__main__":
    q, v = 0.8 * 25 * 200, 0.005          # arc efficiency 0.8, 25 V, 200 A; 5 mm/s
    print(f"net heat input {q:.0f} W, {q/v/1e6:.2f} kJ/mm of weld")
    back, ahead = pool_length(q, v)
    print(f"melt pool on the surface: {back*1000:.2f} mm behind the arc, {ahead*1000:.3f} mm ahead")
    assert abs(T(-back, 0, 0, q, v) - TM) < 1e-3
    # behind the arc on the centreline the solution reduces to q / (2 pi k |xi|): check
    assert abs(T(-0.03, 0, 0, q, v) - 20 - q / (2 * math.pi * K * 0.03)) < 1e-9
    # cooling time: compare the formula with the temperature history at a point on the centreline far behind
    xs = -np.linspace(1e-4, 0.5, 400001); Ts = 20 + q / (2 * math.pi * K * (-xs))
    t800 = -xs[np.argmin(abs(Ts - 800))] / v; t500 = -xs[np.argmin(abs(Ts - 500))] / v
    print(f"t8/5 = {t85(q, v):.2f} s (from the centreline history {t500 - t800:.2f} s)")
    assert abs((t500 - t800) - t85(q, v)) < 0.01
    print(f"preheat to 150 C: t8/5 = {t85(q, v, 150):.2f} s; double speed: {t85(q, 2*v):.2f} s")
