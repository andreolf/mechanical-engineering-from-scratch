"""Thin-walled torsion: Bredt-Batho for closed sections against the open (slit) section."""
import math


def closed_J(Am, perimeter_over_t):
    """J = 4 Am^2 / (closed integral ds / t); shear flow q = T / (2 Am)."""
    return 4 * Am**2 / perimeter_over_t


def open_J(segments):
    """Sum of b t^3 / 3 over the thin walls (b = length, t = thickness)."""
    return sum(b * t**3 / 3 for b, t in segments)


if __name__ == "__main__":
    G = 26e3                                   # MPa, aluminium
    # a bike down tube: 35 mm outside diameter, 1.2 mm wall
    D, t = 35.0, 1.2
    rm = (D - t) / 2; Am = math.pi * rm**2; s = 2 * math.pi * rm
    Jc = closed_J(Am, s / t)
    Jexact = math.pi * (D**4 - (D - 2 * t) ** 4) / 32
    Jo = open_J([(s, t)])
    print(f"bike tube: Bredt J = {Jc:.1f} mm^4, exact thick-wall J = {Jexact:.1f} mm^4 ({(Jc / Jexact - 1) * 100:+.2f} %)")
    print(f"  slit along its length: J = {Jo:.2f} mm^4, closed / open = {Jc / Jo:.1f} (3 (rm/t)^2 = {3 * (rm / t) ** 2:.1f})")
    assert abs(Jc / Jexact - 1) < 0.01 and abs(Jc / Jo - 3 * (rm / t) ** 2) < 1e-9
    # stresses under 60 N m of twist
    T = 60e3
    tau_c = T / (2 * Am * t)                   # Bredt: q = T / (2 Am), tau = q / t
    tau_o = T * t / Jo                         # open section: tau_max = T t / J
    print(f"  60 N m: closed tube tau = {tau_c:.2f} MPa; slit tube tau = {tau_o:.1f} MPa ({tau_o / tau_c:.0f} times higher)")
    # a rectangular box beam 120 x 60 mm with 3 mm walls
    b, h, tw = 120.0, 60.0, 3.0
    Am = (b - tw) * (h - tw); per = 2 * ((b - tw) + (h - tw)) / tw
    Jb = closed_J(Am, per)
    print(f"box 120 x 60 x 3: J = {Jb:.4e} mm^4, tau at 1 kN m = {1e6 / (2 * Am * tw):.3f} MPa")
