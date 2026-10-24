"""Flywheel energy storage: E = I w^2 / 2 and the thin-rim hoop stress sigma = rho v^2."""
import math
import numpy as np


def rim_stress_by_equilibrium(rho, R, t, w, n=200001):
    """Cut a thin rim (radius R, cross-section area A = t * 1) in half: the centrifugal pull on the half ring
    must be carried by the two cut faces: 2 sigma A = integral rho A R w^2 R sin(th) dth = 2 rho A R^2 w^2."""
    th = np.linspace(0, np.pi, n)
    A = t * 1.0
    F = np.trapezoid(rho * A * R * w**2 * np.sin(th) * R, th)
    return F / (2 * A)


def burst_speed(sigma_allow, rho, R):
    """Thin rim: sigma = rho v^2, so v_max = sqrt(sigma / rho) regardless of R; w_max = v_max / R."""
    v = math.sqrt(sigma_allow / rho)
    return v, v / R


if __name__ == "__main__":
    rho_steel, s_steel = 7850.0, 800e6          # high-strength steel, usable stress 800 MPa
    rho_cf, s_cf = 1600.0, 1500e6               # carbon-fibre rim, usable hoop stress 1.5 GPa
    for R in (0.2, 0.5, 1.0):
        v, w = burst_speed(s_steel, rho_steel, R)
        s_num = rim_stress_by_equilibrium(rho_steel, R, 0.01, w)
        print(f"steel rim R = {R} m: limit rim speed {v:.1f} m/s, {w * 60 / (2 * math.pi):8.0f} rpm; stress check {s_num / 1e6:.2f} MPa")
        assert abs(s_num - s_steel) < 1e-6 * s_steel
    # energy per unit mass of a thin rim at its limit: e = v^2 / 2 = sigma / (2 rho), again independent of R
    for name, rho, s in (("steel", rho_steel, s_steel), ("carbon fibre", rho_cf, s_cf)):
        e = s / (2 * rho)
        print(f"{name:12s}: specific energy at the stress limit {e / 1e3:.1f} kJ/kg = {e / 3600:.1f} Wh/kg")
    # a carbon-fibre rim for a bus: 60 kg, mean radius 0.25 m, run between 50 % and 100 % of top speed
    m, R = 60.0, 0.25
    v, w = burst_speed(s_cf / 1.5, rho_cf, R)               # safety factor 1.5 on stress
    I = m * R**2
    E_full = 0.5 * I * w**2
    print(f"bus flywheel: top speed {w * 60 / (2 * math.pi):.0f} rpm, rim {v:.0f} m/s, stored {E_full / 3.6e6:.3f} kWh; usable between 50 % and 100 % speed: {0.75 * E_full / 3.6e6:.3f} kWh")
    # stress grows with the square of speed: 10 % overspeed means 21 % more stress
    print(f"10 % overspeed raises rim stress by {(1.1**2 - 1) * 100:.0f} %")
