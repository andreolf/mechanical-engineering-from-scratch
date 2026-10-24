"""Hardening mechanisms: fit Hall-Petch to grain-size data, plus Orowan precipitation strengthening."""
import math
import numpy as np

if __name__ == "__main__":
    s0, k = 70.0, 0.74                                    # MPa, MPa m^0.5 (a mild steel)
    d = np.array([5, 8, 12, 20, 35, 60, 100, 200]) * 1e-6  # grain sizes, m
    rng = np.random.default_rng(7)
    sy = s0 + k / np.sqrt(d) + rng.normal(0, 4.0, d.size)  # measured yield with 4 MPa scatter
    A = np.column_stack([np.ones_like(d), d**-0.5])
    (s0_fit, k_fit), res, *_ = np.linalg.lstsq(A, sy, rcond=None)
    resid = sy - A @ np.array([s0_fit, k_fit]); se = math.sqrt(resid @ resid / (len(d) - 2))
    cov = se**2 * np.linalg.inv(A.T @ A)
    print("grain size (um) and yield (MPa):", ", ".join(f"{x*1e6:.0f}: {y:.1f}" for x, y in zip(d, sy)))
    print(f"fit: sigma_0 = {s0_fit:.2f} +- {math.sqrt(cov[0,0]):.2f} MPa, k = {k_fit:.4f} +- {math.sqrt(cov[1,1]):.4f} MPa m^0.5 (input 70, 0.74)")
    assert abs(k_fit / k - 1) < 0.05 and abs(k_fit - k) < 3 * math.sqrt(cov[1, 1])
    for dd in (50e-6, 10e-6, 1e-6):
        print(f"d = {dd*1e6:.0f} um: predicted yield {s0_fit + k_fit/math.sqrt(dd):.0f} MPa")
    # Orowan: dislocations bow between precipitates spaced L apart, tau = G b / L; tensile with Taylor factor M = 3.06
    G, b, M = 26e9, 0.286e-9, 3.06
    for L in (1000e-9, 300e-9, 100e-9, 30e-9):
        print(f"aluminium, precipitate spacing {L*1e9:.0f} nm: Orowan shear {G*b/L/1e6:.1f} MPa, tensile increase {M*G*b/L/1e6:.0f} MPa")
