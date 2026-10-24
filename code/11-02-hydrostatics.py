"""Hydrostatics: dp/dz = -rho g integrated for water and for the atmosphere, plus a U-tube manometer."""
import numpy as np

G = 9.81


def integrate(rho_of, p0, z):
    """March dp/dz = -rho(p, z) g upward with a midpoint (RK2) step from p0 at z[0]."""
    p = [p0]
    for i in range(len(z) - 1):
        dz = z[i + 1] - z[i]
        pm = p[-1] - rho_of(p[-1], z[i]) * G * dz / 2
        p.append(p[-1] - rho_of(pm, z[i] + dz / 2) * G * dz)
    return np.array(p)


def manometer(h, rho_m, rho_f):
    """Pressure difference across a U-tube with manometer fluid rho_m reading h, under fluid rho_f."""
    return (rho_m - rho_f) * G * h


if __name__ == "__main__":
    # water: gauge pressure at 10 m depth (z measured upward from the bottom)
    z = np.linspace(0, 10, 101)
    p = integrate(lambda p, z: 1000.0, 1000 * G * 10, z)
    print(f"gauge pressure at 10 m depth: {p[0]/1000:.2f} kPa; at the surface {p[-1]:.2e} Pa")
    assert abs(p[0] - 98.1e3) < 1 and abs(p[-1]) < 1e-6
    # atmosphere with the standard 6.5 K/km lapse rate, from Zurich (408 m) to Jungfraujoch (3454 m)
    R = 287.05
    T = lambda z: 288.15 - 0.0065 * z
    z = np.linspace(0, 3454, 3455)
    p = integrate(lambda p, zz: p / (R * T(zz)), 101325.0, z)
    isa = 101325 * (T(z) / 288.15) ** (G / (R * 0.0065))
    assert np.max(np.abs(p - isa)) < 1.0
    print(f"standard atmosphere: Zurich 408 m {p[408]/100:.1f} hPa, Jungfraujoch 3454 m {p[-1]/100:.1f} hPa")
    t_boil = 1730.63 / (8.07131 - np.log10(p[-1] / 133.322)) - 233.426          # Antoine equation for water
    print(f"water boils at {t_boil:.1f} C on the Jungfraujoch")
    # manometer: mercury reading 120 mm across an orifice in a water pipe
    dp = manometer(0.120, 13546, 998)
    print(f"mercury manometer, 120 mm reading under water: {dp/1000:.3f} kPa")
