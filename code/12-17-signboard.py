"""Wind load on a signboard: dynamic pressure, a simplified gust factor, force, and the bending stress in its post.
Simplification, clearly labelled: peak pressure = (1 + 7 I_v) x mean pressure with I_v = 1 / ln(z / z0), in the spirit of
EN 1991-1-4. A real design follows the code in full, including the terrain, orography and the national annex."""
import math


def dynamic_pressure(V, rho=1.20):
    return 0.5 * rho * V * V


def peak_pressure(V_mean, z, z0=0.3, rho=1.20):
    Iv = 1 / math.log(z / z0)
    return (1 + 7 * Iv) * dynamic_pressure(V_mean, rho), Iv


def sign_load(V_mean, b, h, z_centre, Cf=1.8, z0=0.3):
    qp, Iv = peak_pressure(V_mean, z_centre, z0)
    return Cf * qp * b * h, qp, Iv


def tube_section_modulus(D, t):
    d = D - 2 * t
    return math.pi * (D ** 4 - d ** 4) / (32 * D)


if __name__ == "__main__":
    # a 3 m x 1.5 m shop sign in Denpasar on one steel post, centre 4 m up, mean wind 22 m/s at that height
    b, h, zc, V = 3.0, 1.5, 4.0, 22.0
    F, qp, Iv = sign_load(V, b, h, zc)
    print(f"mean dynamic pressure {dynamic_pressure(V):.1f} Pa; turbulence intensity {Iv:.4f}; peak pressure {qp:.1f} Pa")
    print(f"force on the sign (C_f = 1.8): {F/1000:.3f} kN")
    M = F * zc
    W = tube_section_modulus(0.1683, 0.0071)                  # 168.3 x 7.1 mm circular hollow section
    print(f"base moment {M/1000:.2f} kN m; post W = {W*1e6:.1f} cm^3; bending stress {M/W/1e6:.1f} MPa (S355 yields at 355)")
    # load scales with v^2
    F2, _, _ = sign_load(2 * V, b, h, zc)
    print(f"doubling the wind speed multiplies the load by {F2/F:.6f}")
    assert abs(F2 / F - 4) < 1e-12
    for Vx in (15, 22, 30, 40):
        Fx, _, _ = sign_load(Vx, b, h, zc)
        print(f"  {Vx} m/s: {Fx/1000:6.2f} kN, stress {Fx*zc/W/1e6:6.1f} MPa")
