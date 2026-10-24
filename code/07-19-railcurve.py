"""Trains in curves: cant (superelevation), balance speed and cant deficiency."""
import math


GAUGE = 1.435          # m, standard gauge
S = 1.5                # m, distance between rail-head centre lines used for cant


def lateral_accel_in_plane(v, R, cant_mm, g=9.81):
    """Acceleration felt by passengers along the (tilted) floor: v^2/R cos(phi) - g sin(phi), phi = asin(cant / S)."""
    phi = math.asin(cant_mm / 1000 / S)
    return v**2 / R * math.cos(phi) - g * math.sin(phi), phi


def balance_speed(R, cant_mm, g=9.81):
    phi = math.asin(cant_mm / 1000 / S)
    return math.sqrt(g * R * math.tan(phi))


def cant_deficiency(v, R, cant_mm, g=9.81):
    """Extra cant (mm) that would be needed to balance speed v: S v^2 / (g R) - applied cant (small-angle form)."""
    return S * 1000 * v**2 / (g * R) - cant_mm


if __name__ == "__main__":
    R, cant = 1200.0, 150.0                                       # a 1200 m curve with 150 mm cant
    vb = balance_speed(R, cant)
    a, phi = lateral_accel_in_plane(vb, R, cant)
    print(f"R = {R:.0f} m, cant {cant:.0f} mm (tilt {math.degrees(phi):.3f} deg): balance speed {vb:.3f} m/s = {vb * 3.6:.1f} km/h")
    print(f"  at balance speed the sideways acceleration on the floor is {a:.1e} m/s^2: no lateral force on wheels or passengers")
    assert abs(a) < 1e-12
    for kmh in (80, 120, 160, 200):
        v = kmh / 3.6
        a, _ = lateral_accel_in_plane(v, R, cant)
        print(f"  {kmh:3d} km/h: uncompensated lateral acceleration {a:+.3f} m/s^2, cant deficiency {cant_deficiency(v, R, cant):+.0f} mm")
    # a typical limit: 1.0 m/s^2 uncompensated (about 150 mm deficiency); tilting trains allow about 2.0
    for lim, name in ((1.0, "conventional"), (2.0, "tilting")):
        lo, hi = vb, 150.0
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if lateral_accel_in_plane(mid, R, cant)[0] < lim else (lo, mid)
        print(f"  {name} train limit {lim} m/s^2: {lo * 3.6:.1f} km/h")
