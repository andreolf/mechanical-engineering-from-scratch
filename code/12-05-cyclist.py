"""Power to ride a bicycle: aerodynamic drag with C_D A, rolling resistance, and the speed you get for a given power."""
import math

G = 9.81


def air_density(p=96_600.0, T=288.15):
    """Ideal gas; 96.6 kPa is a typical pressure at Zurich's altitude (408 m)."""
    return p / (287.05 * T)


def power(v, CdA, m=80.0, Crr=0.004, wind=0.0, eta=0.97, rho=None):
    """Rider power (W) at ground speed v (m/s) into a headwind `wind` (m/s) on the flat."""
    rho = air_density() if rho is None else rho
    va = v + wind
    aero = 0.5 * rho * CdA * va * abs(va) * v
    roll = Crr * m * G * v
    return (aero + roll) / eta, aero / eta, roll / eta


def speed_for_power(P, CdA, **kw):
    lo, hi = 0.0, 40.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if power(mid, CdA, **kw)[0] < P else (lo, mid)
    return (lo + hi) / 2


if __name__ == "__main__":
    rho = air_density()
    print(f"air density {rho:.4f} kg/m^3")
    positions = {"upright": 0.50, "hoods": 0.32, "drops": 0.28, "time trial": 0.22}
    for name, CdA in positions.items():
        v = speed_for_power(200, CdA)
        print(f"{name:10s} C_D A = {CdA:.2f} m^2: 200 W gives {v*3.6:.2f} km/h")
    # aerodynamic power alone scales with v^3 in still air
    a1 = power(8.0, 0.32)[1]; a2 = power(16.0, 0.32)[1]
    print(f"aero power at 8 m/s {a1:.2f} W, at 16 m/s {a2:.2f} W, ratio {a2/a1:.4f}")
    assert abs(a2 / a1 - 8) < 1e-12
    P, A, R = power(10.0, 0.32)
    print(f"36 km/h on the hoods: {P:.1f} W total, {A:.1f} W aero ({100*A/P:.0f} %), {R:.1f} W rolling")
    v = speed_for_power(200, 0.32, wind=5.0)
    print(f"into a 5 m/s Bise headwind, 200 W gives {v*3.6:.2f} km/h")
