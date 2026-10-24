"""Insulating a pipe or a wire: cylindrical conduction resistance, and the critical radius where heat loss peaks."""
import math
import numpy as np


def loss_per_metre(r1, r2, k, h, dT):
    """Conduction through the insulation shell in series with convection from its outer surface."""
    R = math.log(r2 / r1) / (2 * math.pi * k) + 1 / (2 * math.pi * r2 * h)
    return dT / R


def loss_sphere(r1, r2, k, h, dT):
    R = (1 / r1 - 1 / r2) / (4 * math.pi * k) + 1 / (4 * math.pi * r2 ** 2 * h)
    return dT / R


if __name__ == "__main__":
    # a 2 mm-radius copper wire coated in PVC (k = 0.19), still air h = 10 W/(m^2 K), wire 40 K above the air
    r1, k, h, dT = 0.002, 0.19, 10.0, 40.0
    r2s = np.linspace(r1, 0.08, 7801)                          # 0.01 mm steps
    Q = np.array([loss_per_metre(r1, r, k, h, dT) for r in r2s])
    rq = r2s[Q.argmax()]
    print(f"bare wire: {loss_per_metre(r1, r1, k, h, dT):.4f} W/m; numerical peak {Q.max():.4f} W/m at r2 = {rq*1000:.2f} mm; k/h = {k/h*1000:.2f} mm")
    assert abs(rq - k / h) < 2e-4                                  # critical radius r_c = k / h
    # refine with the golden-section search to show it is exact
    a, b = r1, 0.08; g = (math.sqrt(5) - 1) / 2
    for _ in range(200):
        c, d = b - g * (b - a), a + g * (b - a)
        if loss_per_metre(r1, c, k, h, dT) > loss_per_metre(r1, d, k, h, dT): b = d
        else: a = c
    print(f"golden-section maximum at {(a+b)/2*1000:.6f} mm")
    assert abs((a + b) / 2 - k / h) < 1e-9
    # a 15 mm copper hot-water pipe (r1 = 7.5 mm) with foam (k = 0.04): r_c = 4 mm < r1, so insulation always helps
    r1p, kp = 0.0075, 0.04
    for t in (0, 0.005, 0.013, 0.025):
        print(f"  pipe with {t*1000:4.0f} mm foam: {loss_per_metre(r1p, r1p + t, kp, h, 50.0):.3f} W/m")
    # sphere: critical radius 2 k / h
    rs = np.linspace(0.001, 0.2, 199001)
    Qs = np.array([loss_sphere(0.001, r, k, h, dT) for r in rs])
    print(f"sphere: peak at {rs[Qs.argmax()]*1000:.2f} mm, 2k/h = {2*k/h*1000:.2f} mm")
    assert abs(rs[Qs.argmax()] - 2 * k / h) < 2e-6
