"""Moment of inertia of a flywheel from its profile: I = integral of r^2 dm, plus the parallel-axis theorem."""
import math
import numpy as np


def inertia_from_profile(r, t, rho):
    """Axisymmetric wheel with thickness t(r) (m) at radius r (m): dm = rho t(r) 2 pi r dr, I = integral r^2 dm."""
    m = np.trapezoid(rho * t * 2 * math.pi * r, r)
    I = np.trapezoid(rho * t * 2 * math.pi * r**3, r)
    return m, I


if __name__ == "__main__":
    rho = 7850.0
    # check simple shapes against the formulas a CAD package would give
    r = np.linspace(0, 0.2, 200001)
    m, I = inertia_from_profile(r, np.full_like(r, 0.03), rho)
    print(f"solid disc 400 x 30 mm: m = {m:.4f} kg, I = {I:.6f} kg m^2 (m R^2 / 2 = {m * 0.2**2 / 2:.6f})")
    assert abs(I - m * 0.04 / 2) < 1e-9
    r = np.linspace(0.15, 0.2, 200001)
    m, I = inertia_from_profile(r, np.full_like(r, 0.03), rho)
    print(f"ring 300-400 mm: m = {m:.4f} kg, I = {I:.6f} (m (R1^2 + R2^2) / 2 = {m * (0.15**2 + 0.2**2) / 2:.6f})")
    assert abs(I - m * (0.15**2 + 0.2**2) / 2) < 1e-9
    # an engine flywheel: 20 mm web out to 160 mm, then a 60 mm wide rim to 200 mm, with a 60 mm hub (bore 30 mm)
    r = np.linspace(0.015, 0.2, 400001)
    t = np.where(r < 0.03, 0.06, np.where(r < 0.16, 0.02, 0.06))
    m, I = inertia_from_profile(r, t, rho)
    rim = np.where(r >= 0.16, t, 0)
    mr, Ir = inertia_from_profile(r, rim, rho)
    print(f"engine flywheel: m = {m:.3f} kg, I = {I:.5f} kg m^2; the rim is {100 * mr / m:.0f} % of the mass but {100 * Ir / I:.0f} % of the inertia")
    print(f"radius of gyration k = sqrt(I/m) = {math.sqrt(I / m) * 1000:.1f} mm")
    # parallel axis: a 0.5 kg bolt-on balance mass 150 mm off-axis, treated as a 20 mm diameter disc about its own axis
    mb, rb = 0.5, 0.15
    Ib = mb * 0.01**2 / 2 + mb * rb**2
    print(f"balance mass about the shaft: {Ib:.6f} kg m^2 (own axis only {mb * 0.01**2 / 2:.2e})")
    # energy stored at 3000 rpm
    w = 3000 * 2 * math.pi / 60
    print(f"kinetic energy at 3000 rpm: {0.5 * I * w**2 / 1e3:.2f} kJ")
