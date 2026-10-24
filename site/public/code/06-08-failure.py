"""Yield criteria: von Mises (distortion energy) and Tresca (maximum shear), with safety factors."""
import math
import numpy as np


def principal(sig):
    return np.sort(np.linalg.eigvalsh(np.asarray(sig, float)))[::-1]


def von_mises(sig):
    s1, s2, s3 = principal(sig)
    return math.sqrt(((s1 - s2) ** 2 + (s2 - s3) ** 2 + (s3 - s1) ** 2) / 2)


def tresca(sig):
    s = principal(sig)
    return s[0] - s[2]                           # twice the maximum shear stress


def distortion_energy(sig, E, nu):
    """Strain energy density minus its volumetric part."""
    sig = np.asarray(sig, float); G = E / (2 * (1 + nu))
    dev = sig - np.trace(sig) / 3 * np.eye(3)
    return (dev * dev).sum() / (4 * G)


if __name__ == "__main__":
    fy, E, nu = 355.0, 210e3, 0.3               # S355 structural steel
    # pure shear: von Mises yields at fy / sqrt(3), Tresca at fy / 2
    for name, f, limit in (("von Mises", von_mises, fy / math.sqrt(3)), ("Tresca", tresca, fy / 2)):
        tau = limit; sig = [[0, tau, 0], [tau, 0, 0], [0, 0, 0]]
        print(f"pure shear, {name}: yields at tau = {tau:.4f} MPa (equivalent stress {f(sig):.4f})")
        assert abs(f(sig) - fy) < 1e-9
    # a shaft surface: 120 MPa bending stress plus 70 MPa torsional shear
    sig = [[120, 70, 0], [70, 0, 0], [0, 0, 0]]
    vm, tr = von_mises(sig), tresca(sig)
    print(f"shaft: von Mises {vm:.4f} MPa (sqrt(s^2 + 3 t^2) = {math.sqrt(120**2 + 3 * 70**2):.4f}), Tresca {tr:.4f} MPa (sqrt(s^2 + 4 t^2) = {math.sqrt(120**2 + 4 * 70**2):.4f})")
    print(f"  safety factors against yield: {fy / vm:.3f} (von Mises), {fy / tr:.3f} (Tresca)")
    assert abs(vm - math.sqrt(120**2 + 3 * 70**2)) < 1e-9 and tr >= vm
    # von Mises = equal distortion energy: compare with a uniaxial bar at the same equivalent stress
    assert abs(distortion_energy(sig, E, nu) - distortion_energy(np.diag([vm, 0, 0]), E, nu)) < 1e-12
    # hydrostatic stress never yields under either criterion
    assert von_mises(np.diag([-500.0, -500.0, -500.0])) < 1e-9 and tresca(np.diag([-500.0, -500.0, -500.0])) < 1e-9
    print("hydrostatic pressure of 500 MPa: equivalent stress 0 (no distortion, no yield)")
