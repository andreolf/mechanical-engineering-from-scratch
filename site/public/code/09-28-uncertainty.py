"""Measurement uncertainty: a GUM budget for a micrometer reading, propagation through a formula checked by Monte Carlo, and the Abbe error."""
import math
import numpy as np


def combine(*u):
    return math.sqrt(sum(x * x for x in u))


if __name__ == "__main__":
    # ten readings of a nominal 25 mm steel shaft (mm)
    r = np.array([25.004, 25.006, 25.003, 25.005, 25.004, 25.007, 25.005, 25.004, 25.006, 25.005])
    mean, s = r.mean(), r.std(ddof=1)
    u_rep = s / math.sqrt(len(r))                 # type A
    u_res = 0.001 / math.sqrt(12)                 # rectangular, 1 um resolution
    u_cal = 0.002 / 2                             # certificate: 2 um at k = 2
    u_th = 25 * 11.5e-6 * 2 / math.sqrt(3)        # +-2 C from 20 C, rectangular, no compensation
    uc = combine(u_rep, u_res, u_cal, u_th)
    print(f"mean {mean:.4f} mm, s = {s*1000:.3f} um")
    for name, u in (("repeatability", u_rep), ("resolution", u_res), ("calibration", u_cal), ("temperature", u_th)):
        print(f"  {name:13s} {u*1000:.3f} um ({u*u/uc/uc*100:.0f} % of variance)")
    print(f"combined {uc*1000:.3f} um; expanded (k = 2): {mean:.4f} +- {2*uc*1000:.1f} um")
    # density of a cylinder rho = 4 m / (pi d^2 h): sensitivity coefficients vs Monte Carlo
    m, um = 0.1250, 0.0001          # kg
    d, ud = 0.0200, 0.00001         # m
    h, uh = 0.0510, 0.00002
    rho = 4 * m / (math.pi * d * d * h)
    rel = math.sqrt((um / m) ** 2 + (2 * ud / d) ** 2 + (uh / h) ** 2)
    rng = np.random.default_rng(7); N = 1_000_000
    sm = rng.normal(m, um, N); sd = rng.normal(d, ud, N); sh = rng.normal(h, uh, N)
    mc = 4 * sm / (math.pi * sd**2 * sh)
    print(f"density {rho:.1f} kg/m^3, u = {rho*rel:.2f} by propagation, {mc.std():.2f} by Monte Carlo")
    assert abs(mc.std() / (rho * rel) - 1) < 0.01
    # Abbe: scale 30 mm away from the measuring line, carriage pitches by 50 microradians
    print(f"Abbe error: 30 mm offset x 50 urad = {30e-3*50e-6*1e6:.2f} um")
