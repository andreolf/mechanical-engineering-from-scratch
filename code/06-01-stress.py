"""Cauchy stress: the traction on any plane is t = sigma n; split it into normal and shear parts."""
import numpy as np


def traction(sigma, n):
    n = np.asarray(n, float); n = n / np.linalg.norm(n)
    t = sigma @ n
    sn = t @ n                                   # normal stress (tension positive)
    tau = np.linalg.norm(t - sn * n)             # shear stress magnitude in the plane
    return t, sn, tau


if __name__ == "__main__":
    # a stress state in a bike frame lug (MPa); symmetric, as moment balance on a small cube demands
    S = np.array([[80.0, 30.0, 0.0], [30.0, -20.0, 0.0], [0.0, 0.0, 10.0]])
    assert np.allclose(S, S.T)
    n = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)
    t, sn, tau = traction(S, n)
    print(f"plane n = (1,1,1)/sqrt3: traction {np.round(t, 4)} MPa, normal {sn:.4f} MPa, shear {tau:.4f} MPa")
    assert abs(np.linalg.norm(t) ** 2 - sn**2 - tau**2) < 1e-9
    # Cauchy's tetrahedron: the slanted face (area A, normal n) and the three coordinate faces (areas A n_i, outward -e_i)
    A = 1.0
    F = t * A + sum(S @ (-np.eye(3)[i]) * A * n[i] for i in range(3))
    print(f"tetrahedron force balance: {np.round(F, 12)}")
    assert np.allclose(F, 0)
    # on the coordinate planes the traction components are just the columns of sigma
    for i in range(3):
        assert np.allclose(traction(S, np.eye(3)[i])[0], S[:, i])
    # 2D: a tube under 60 MPa axial stress and 25 MPa torsional shear, planes rotated by phi
    S2 = np.array([[60.0, 25.0], [25.0, 0.0]])
    for deg in (0, 30, 45, 90):
        ph = np.radians(deg); n2 = np.array([np.cos(ph), np.sin(ph)])
        t2 = S2 @ n2; print(f"  plane at {deg:2d} deg: normal {t2 @ n2:8.4f} MPa, shear {t2 @ np.array([-n2[1], n2[0]]):8.4f} MPa")
    # the largest normal stress over all planes is the largest eigenvalue
    phis = np.linspace(0, np.pi, 100001)
    sn_all = 60 * np.cos(phis) ** 2 + 2 * 25 * np.sin(phis) * np.cos(phis)
    print(f"max normal stress over all planes {sn_all.max():.4f} MPa, largest eigenvalue {np.linalg.eigvalsh(S2).max():.4f}")
    assert abs(sn_all.max() - np.linalg.eigvalsh(S2).max()) < 1e-6
