"""Gear tooth strength: Lewis bending stress with the Barth velocity factor, and Hertz contact stress from the AGMA geometry factor checked against two contacting cylinders."""
import math
import numpy as np

# Lewis form factor Y for 20 degree full-depth teeth (tooth count: Y), as tabulated in Shigley
LEWIS = [(12, .245), (13, .261), (14, .277), (15, .290), (16, .296), (17, .303), (18, .309), (19, .314), (20, .322),
         (21, .328), (22, .331), (24, .337), (26, .346), (28, .353), (30, .359), (34, .371), (38, .384), (43, .397),
         (50, .409), (60, .422), (75, .435), (100, .447), (150, .460), (300, .472), (400, .480)]


def lewis_Y(z):
    zs, ys = zip(*LEWIS)
    return float(np.interp(z, zs, ys))


def barth_Kv(V):
    """Velocity factor for cut or milled teeth, V pitch-line speed in m/s."""
    return (6.1 + V) / 6.1


def lewis_stress(Wt, F, m, z, V):
    return barth_Kv(V) * Wt / (F * m * lewis_Y(z))


def elastic_coefficient(E1, nu1, E2, nu2):
    return math.sqrt(1 / (math.pi * ((1 - nu1**2) / E1 + (1 - nu2**2) / E2)))


def contact_stress(Wt, F, d1, z1, z2, phi, Cp, Kv=1.0):
    """AGMA form: sigma_c = Cp sqrt(Kv Wt / (F d1 I)), I = cos(phi) sin(phi)/2 * mG/(mG + 1)."""
    mG = z2 / z1
    I = math.cos(phi) * math.sin(phi) / 2 * mG / (mG + 1)
    return Cp * math.sqrt(Kv * Wt / (F * d1 * I))


def hertz_cylinders(Wt, F, d1, d2, phi, E, nu, Kv=1.0):
    """Two cylinders of radii equal to the involute curvatures at the pitch point, pressed by the normal tooth load."""
    rho1, rho2 = d1 / 2 * math.sin(phi), d2 / 2 * math.sin(phi)
    Rstar = 1 / (1 / rho1 + 1 / rho2)
    Estar = E / (2 * (1 - nu**2))
    w = Kv * Wt / math.cos(phi) / F
    return math.sqrt(w * Estar / (math.pi * Rstar))


if __name__ == "__main__":
    z1, z2, phi, F, E, nu = 18, 45, math.radians(20), 20.0, 207e3, 0.30
    P, n1 = 3000.0, 1500.0  # 3 kW at 1500 rpm on the pinion
    T = P / (2 * math.pi * n1 / 60) * 1000  # N mm
    Cp = elastic_coefficient(E, nu, E, nu)
    print(f"pinion torque {T/1000:.3f} N m, elastic coefficient {Cp:.1f} sqrt(MPa)")
    prev = None
    for m in (1.5, 2.0, 2.5, 3.0, 4.0):
        d1, d2 = m * z1, m * z2
        V = math.pi * d1 / 1000 * n1 / 60
        Wt = 2 * T / d1
        sb = lewis_stress(Wt, F, m, z1, V)
        sc = contact_stress(Wt, F, d1, z1, z2, phi, Cp, barth_Kv(V))
        sh = hertz_cylinders(Wt, F, d1, d2, phi, E, nu, barth_Kv(V))
        print(f"m = {m}: V = {V:.3f} m/s, Wt = {Wt:.1f} N, Kv = {barth_Kv(V):.4f}, bending {sb:.1f} MPa, contact {sc:.1f} MPa")
        assert abs(sc / sh - 1) < 1e-12  # the AGMA geometry factor is Hertz for cylinders at the pitch point
        if prev:
            assert sb < prev[0] and sc < prev[1]  # stresses fall as the module grows
        prev = (sb, sc)
