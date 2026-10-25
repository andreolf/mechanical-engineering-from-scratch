"""Helical compression spring: rate k = G d^4/(8 D^3 n) checked against the strain energy of a real helix (torsion plus bending of the wire), Wahl-corrected stress and a coil-count study."""
import math
import numpy as np


def rate(G, d, D, n):
    return G * d**4 / (8 * D**3 * n)


def wahl(C):
    return (4 * C - 1) / (4 * C - 4) + 0.615 / C


def shear_stress(F, D, d):
    return wahl(D / d) * 8 * F * D / (math.pi * d**3)


def helix_rate(G, E, d, D, n, pitch, m=20000):
    """Axial load F on the helix axis. At each wire section the moment of F has a torsion part (about the wire
    tangent) and a bending part. Strain energy U = int(Mt^2/(2GJ) + Mb^2/(2EI)) ds, deflection = 2U/F."""
    R = D / 2
    J = math.pi * d**4 / 32; I = J / 2
    th = np.linspace(0, 2 * math.pi * n, m + 1)
    pos = np.column_stack([R * np.cos(th), R * np.sin(th), pitch * th / (2 * math.pi)])
    tang = np.column_stack([-R * np.sin(th), R * np.cos(th), np.full_like(th, pitch / (2 * math.pi))])
    ds_dth = np.linalg.norm(tang[0])
    tang /= ds_dth
    F = 1.0
    force = np.array([0.0, 0.0, F])
    # moment at the section from the load applied on the axis (0, 0, z_end): M = (r_axis - r) x F
    r = np.column_stack([-pos[:, 0], -pos[:, 1], np.zeros(len(th))])
    M = np.cross(r, force)
    Mt = (M * tang).sum(1)
    Mb2 = (M**2).sum(1) - Mt**2
    e = Mt**2 / (2 * G * J) + Mb2 / (2 * E * I)
    U = float(np.sum(0.5 * (e[1:] + e[:-1])) * (th[1] - th[0]) * ds_dth)
    return F / (2 * U / F)


if __name__ == "__main__":
    # scooter front suspension spring: oil-tempered wire d = 5 mm, mean diameter 40 mm, 8 active coils
    G, E, d, D = 79.3e3, 203.4e3, 5.0, 40.0
    for n in (6, 8, 10, 12):
        pitch = d + 0.6 * d  # open coils
        k = rate(G, d, D, n)
        kh = helix_rate(G, E, d, D, n, pitch)
        print(f"n = {n:2d}: k = {k:.4f} N/mm, helix strain energy {kh:.4f} N/mm ({100*(kh/k-1):+.3f}%)")
        assert abs(kh / k - 1) < 0.005
    k8 = rate(G, d, D, 8)
    assert abs(rate(G, d, D, 16) - k8 / 2) < 1e-12   # doubling the coils halves the rate
    F = 600.0
    C = D / d
    tau = shear_stress(F, D, d)
    Sut = 1855 / d**0.187     # oil-tempered wire, MPa
    Ssy = 0.50 * Sut
    print(f"C = {C:.1f}, Wahl factor {wahl(C):.4f}, deflection {F/k8:.1f} mm, shear stress {tau:.1f} MPa; Sut {Sut:.0f} MPa, Ssy {Ssy:.0f} MPa, factor {Ssy/tau:.2f}")
    assert tau < Ssy
