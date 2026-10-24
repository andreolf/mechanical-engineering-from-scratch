"""Isotropic Hooke's law in Voigt form: 6x6 stiffness from E and nu, Lame constants, and a virtual tensile test."""
import numpy as np


def stiffness(E, nu):
    """Voigt order (xx, yy, zz, yz, xz, xy) with engineering shear strains gamma = 2 eps."""
    lam = E * nu / ((1 + nu) * (1 - 2 * nu)); mu = E / (2 * (1 + nu))
    C = np.zeros((6, 6))
    C[:3, :3] = lam
    C[:3, :3] += 2 * mu * np.eye(3)
    C[3:, 3:] = mu * np.eye(3)
    return C, lam, mu


MATERIALS = {"steel": (210e3, 0.30), "aluminium": (70e3, 0.33), "bamboo (along the culm, idealised isotropic)": (18e3, 0.30)}

if __name__ == "__main__":
    for name, (E, nu) in MATERIALS.items():
        C, lam, mu = stiffness(E, nu)
        K = E / (3 * (1 - 2 * nu))
        # virtual tensile test: apply sigma_xx = 100 MPa only, solve for the strains with the compliance C^-1
        sig = np.array([100.0, 0, 0, 0, 0, 0])
        eps = np.linalg.solve(C, sig)
        E_meas, nu_meas = sig[0] / eps[0], -eps[1] / eps[0]
        print(f"{name:45s} lambda {lam / 1e3:7.3f} GPa, G {mu / 1e3:7.3f} GPa, K {K / 1e3:7.3f} GPa | test: E {E_meas / 1e3:.3f} GPa, nu {nu_meas:.4f}")
        assert abs(E_meas - E) < 1e-6 * E and abs(nu_meas - nu) < 1e-12
        assert abs(eps[1] - eps[2]) < 1e-15 and np.allclose(eps[3:], 0)
    # pure shear: tau = G gamma; hydrostatic pressure: volume change = -p / K
    C, lam, mu = stiffness(210e3, 0.3)
    eps = np.linalg.solve(C, np.array([0, 0, 0, 0, 0, 50.0]))
    assert abs(eps[5] - 50 / mu) < 1e-15
    eps = np.linalg.solve(C, -np.array([100.0, 100, 100, 0, 0, 0]))
    print(f"steel under 100 MPa hydrostatic pressure: volume strain {eps[:3].sum():.4e} (= -p/K = {-100 / (210e3 / (3 * 0.4)):.4e})")
    assert abs(eps[:3].sum() + 100 / (210e3 / (3 * (1 - 0.6)))) < 1e-15
    # a 300 mm steel bar under 100 MPa: stretches 0.143 mm and its 20 mm diameter shrinks by 2.9 micrometres
    e = 100 / 210e3
    print(f"300 mm bar, 20 mm diameter at 100 MPa: +{300 * e:.4f} mm long, {-20 * 0.3 * e * 1000:.3f} micrometres in diameter")
