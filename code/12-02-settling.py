"""Settling of sediment grains: Stokes' law and its limit, with a drag correlation for larger grains."""
import math

G = 9.81


def stokes_velocity(d, rho_p, rho, mu):
    """Terminal velocity from 6 pi mu R U = (rho_p - rho) g (4/3) pi R^3."""
    return (rho_p - rho) * G * d * d / (18 * mu)


def cd_schiller_naumann(Re):
    return 24 / Re * (1 + 0.15 * Re ** 0.687)


def terminal_velocity(d, rho_p, rho, mu):
    """Balance weight minus buoyancy against drag with C_D(Re), by fixed-point iteration from the Stokes value."""
    U = stokes_velocity(d, rho_p, rho, mu)
    for _ in range(200):
        Re = rho * U * d / mu
        U_new = math.sqrt(4 * (rho_p - rho) * G * d / (3 * rho * cd_schiller_naumann(Re)))
        if abs(U_new - U) < 1e-14: break
        U = 0.5 * (U + U_new)
    return U


if __name__ == "__main__":
    rho_p, rho, mu = 2650.0, 1000.0, 1.0e-3        # quartz in river water at 20 C
    for d_um in (2, 20, 60, 200, 1000):
        d = d_um * 1e-6
        Us, U = stokes_velocity(d, rho_p, rho, mu), terminal_velocity(d, rho_p, rho, mu)
        print(f"d = {d_um:5d} um: Stokes {Us*1000:10.4f} mm/s, with drag correlation {U*1000:9.4f} mm/s, Re = {rho*U*d/mu:.4g}")
        if rho * U * d / mu < 0.1:
            assert abs(U / Us - 1) < 0.02                                       # Stokes' law holds at low Re
    d = 20e-6; U = stokes_velocity(d, rho_p, rho, mu)
    print(f"20 um silt settles 3 m in {3/U/3600:.2f} h; a 2 um clay particle needs {3/stokes_velocity(2e-6, rho_p, rho, mu)/86400:.1f} days")
    # check the drag: 6 pi mu R U equals the submerged weight
    R = d / 2
    assert abs(6 * math.pi * mu * R * U - (rho_p - rho) * G * 4 / 3 * math.pi * R ** 3) < 1e-20
