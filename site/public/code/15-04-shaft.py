"""Shaft diameter from combined bending and torsion with the DE-Goodman fatigue criterion, including the Marin factors and the size factor iteration."""
import math
import numpy as np


def moment_diagram(L, loads, n=3001):
    """Simply supported shaft of length L with point loads [(x, F)]: reactions and bending moment along x."""
    R2 = sum(F * a for a, F in loads) / L
    R1 = sum(F for _, F in loads) - R2
    x = np.linspace(0, L, n)
    M = R1 * x - sum(F * np.clip(x - a, 0, None) for a, F in loads)
    return R1, R2, x, M


def endurance_limit(Sut, d, ka_a=4.51, ka_b=-0.265, kc=1.0, kd=1.0, ke=1.0):
    """Marin: machined surface, rotating bending size factor kb, MPa and mm."""
    Se_prime = 0.5 * Sut if Sut <= 1400 else 700.0
    ka = ka_a * Sut ** ka_b
    kb = 1.24 * d ** -0.107 if d <= 51 else 1.51 * d ** -0.157
    return ka * kb * kc * kd * ke * Se_prime


def de_goodman_d(n, Sut, Ma, Tm, Kf, Kfs, Mm=0.0, Ta=0.0):
    """Diameter (mm) for safety factor n; moments in N mm, stresses in MPa. Iterates the size factor."""
    d = 25.0
    for _ in range(100):
        Se = endurance_limit(Sut, d)
        A = math.sqrt(4 * (Kf * Ma) ** 2 + 3 * (Kfs * Ta) ** 2)
        B = math.sqrt(4 * (Kf * Mm) ** 2 + 3 * (Kfs * Tm) ** 2)
        d_new = (16 * n / math.pi * (A / Se + B / Sut)) ** (1 / 3)
        if abs(d_new - d) < 1e-10:
            break
        d = d_new
    return d


def goodman_n(d, Sut, Ma, Tm, Kf, Kfs):
    """Back-check: von Mises alternating and mean stresses, then 1/n = sa/Se + sm/Sut."""
    sa = 32 * Kf * Ma / (math.pi * d ** 3)
    tm = 16 * Kfs * Tm / (math.pi * d ** 3)
    sm = math.sqrt(3) * tm
    return 1 / (sa / endurance_limit(Sut, d) + sm / Sut)


if __name__ == "__main__":
    # gearbox countershaft: bearings 300 mm apart, gear force 2000 N at 100 mm, pulley pull 1200 N at 220 mm
    L, loads = 300.0, [(100.0, 2000.0), (220.0, 1200.0)]
    R1, R2, x, M = moment_diagram(L, loads)
    i = int(np.argmax(np.abs(M)))
    Mmax = M[i]
    print(f"reactions {R1:.1f} N and {R2:.1f} N; maximum moment {Mmax/1000:.2f} N m at x = {x[i]:.0f} mm")
    assert abs(R1 + R2 - 3200) < 1e-9 and abs(Mmax - R1 * 100) < 1e-6
    Sut, T, Kf, Kfs = 630.0, 150e3, 1.7, 1.5  # 1045 cold-drawn steel, 150 N m steady torque, shoulder fillet
    ds = []
    for n in (1.5, 2.0, 2.5, 3.0):
        d = de_goodman_d(n, Sut, Mmax, T, Kf, Kfs)
        ds.append(d)
        print(f"n = {n}: d = {d:.2f} mm (Se = {endurance_limit(Sut, d):.1f} MPa), back-check n = {goodman_n(d, Sut, Mmax, T, Kf, Kfs):.4f}")
        assert abs(goodman_n(d, Sut, Mmax, T, Kf, Kfs) - n) < 1e-6
    assert all(b > a for a, b in zip(ds, ds[1:]))  # a larger safety factor needs a larger diameter
