"""Casting: Chvorinov's rule t = B (V/A)^2 with B from mould properties, solidification times of simple shapes, and sizing a riser that freezes last."""
import math


def mould_constant(rho_metal=7300.0, L=300e3, Tm=1500.0, T0=25.0, k=0.52, rho_m=1600.0, c_m=1170.0):
    """B in s/m^2 for a metal freezing against a semi-infinite sand mould (Chvorinov's derivation)."""
    return math.pi / 4 * (rho_metal * L / (Tm - T0)) ** 2 / (k * rho_m * c_m)


def modulus_box(a, b, c):
    return a * b * c / (2 * (a * b + b * c + a * c))


def modulus_cylinder(D, H):
    return (math.pi * D**2 / 4 * H) / (math.pi * D * H + 2 * math.pi * D**2 / 4)


if __name__ == "__main__":
    B = mould_constant()
    print(f"steel in green sand: B = {B:.3e} s/m^2 = {B*1e-4/60:.2f} min/cm^2")
    shapes = {"plate 200x100x20 mm": modulus_box(0.2, 0.1, 0.02), "cube 100 mm": modulus_box(0.1, 0.1, 0.1),
              "sphere 100 mm": 0.1 / 6, "bar 300x40x40 mm": modulus_box(0.3, 0.04, 0.04)}
    for name, M in shapes.items():
        print(f"  {name}: V/A = {M*1000:.2f} mm, freezes in {B*M*M/60:.1f} min")
    # a cube and a sphere of the same diameter have the same modulus D/6
    assert abs(modulus_box(0.1, 0.1, 0.1) - 0.1 / 6) < 1e-15
    # riser for the plate: cylinder H = D with modulus 1.2 times the casting's
    Mc = shapes["plate 200x100x20 mm"]
    lo, hi = 1e-3, 0.5
    for _ in range(80):
        mid = (lo + hi) / 2
        if modulus_cylinder(mid, mid) < 1.2 * Mc: lo = mid
        else: hi = mid
    D = (lo + hi) / 2
    print(f"riser (H = D) for the plate: D = {D*1000:.1f} mm, freezes in {B*modulus_cylinder(D, D)**2/60:.1f} min vs plate {B*Mc**2/60:.1f} min")
    assert abs(D - 6 * 1.2 * Mc) < 1e-9          # H = D cylinder has modulus D/6
    print(f"riser volume {math.pi*D**3/4*1e6:.0f} cm^3 vs plate {0.2*0.1*0.02*1e6:.0f} cm^3")
