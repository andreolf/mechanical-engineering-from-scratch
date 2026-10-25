"""Disc brakes and clutches: torque under uniform pressure and under uniform wear, by integrating the pressure over the friction face, for a hydraulic bicycle disc brake."""
import math
import numpy as np


def torque_numeric(F, mu, ri, ro, law, n=20000):
    """Integrate dT = mu p r dA over an annulus (or any sector: the angle cancels). law: 'pressure' or 'wear'."""
    r = ri + (ro - ri) * (np.arange(n) + 0.5) / n
    dr = (ro - ri) / n
    shape = np.ones_like(r) if law == "pressure" else 1 / r  # uniform wear: p r = const
    p = F * shape / np.sum(shape * 2 * math.pi * r * dr)        # scale so the pressure integrates to F
    return float(np.sum(mu * p * r * 2 * math.pi * r * dr))


def torque_uniform_pressure(F, mu, ri, ro):
    return 2 / 3 * mu * F * (ro**3 - ri**3) / (ro**2 - ri**2)


def torque_uniform_wear(F, mu, ri, ro):
    return mu * F * (ro + ri) / 2


if __name__ == "__main__":
    # 160 mm rotor, pads from 62 to 78 mm radius; lever 100 N with a 4:1 lever, 10 mm master piston, 2 x 22 mm pistons per side
    lever, ratio, d_master, d_caliper, mu = 100.0, 4.0, 10.0, 22.0, 0.40
    p = lever * ratio / (math.pi * d_master**2 / 4)                 # MPa
    F = p * 2 * math.pi * d_caliper**2 / 4                          # clamp force on each pad, N
    ri, ro = 62.0, 78.0
    Tw = 2 * torque_uniform_wear(F, mu, ri, ro)                     # two friction faces
    Tp = 2 * torque_uniform_pressure(F, mu, ri, ro)
    Tw_n = 2 * torque_numeric(F, mu, ri, ro, "wear")
    Tp_n = 2 * torque_numeric(F, mu, ri, ro, "pressure")
    print(f"line pressure {p:.3f} MPa, clamp force {F:.1f} N per side")
    print(f"brake torque: uniform wear {Tw/1000:.3f} N m (numeric {Tw_n/1000:.3f}), uniform pressure {Tp/1000:.3f} N m (numeric {Tp_n/1000:.3f})")
    assert abs(Tw_n / Tw - 1) < 1e-6 and abs(Tp_n / Tp - 1) < 1e-6
    assert Tw <= Tp  # the worn-in (uniform wear) estimate is always the lower, safer one
    for ri2 in (10.0, 40.0, 70.0):
        assert torque_uniform_wear(1, 1, ri2, ro) <= torque_uniform_pressure(1, 1, ri2, ro)
    R_wheel, m = 0.35, 90.0
    Fx = Tw / 1000 / R_wheel
    print(f"tyre braking force {Fx:.0f} N, deceleration {Fx/m:.2f} m/s^2 for 90 kg with this one brake")
    # stopping from 40 km/h: the rotor absorbs the kinetic energy
    E = 0.5 * m * (40 / 3.6) ** 2
    print(f"energy to stop from 40 km/h: {E/1000:.2f} kJ")
