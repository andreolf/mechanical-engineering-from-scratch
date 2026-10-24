"""Composites: rule of mixtures bounds, off-axis stiffness of a unidirectional ply, and a quasi-isotropic laminate from classical lamination theory."""
import math
import numpy as np


def voigt(Ef, Em, Vf):
    return Vf * Ef + (1 - Vf) * Em          # loading along the fibres: equal strain


def reuss(Ef, Em, Vf):
    return 1 / (Vf / Ef + (1 - Vf) / Em)    # loading across the fibres: equal stress


def ply(Ef=230e9, Em=3.5e9, Gf=15e9, Gm=1.3e9, nuf=0.2, num=0.35, Vf=0.6):
    E1 = voigt(Ef, Em, Vf); E2 = reuss(Ef, Em, Vf); G12 = reuss(Gf, Gm, Vf); nu12 = Vf * nuf + (1 - Vf) * num
    return E1, E2, G12, nu12


def Q(E1, E2, G12, nu12):
    """Reduced stiffness of a ply in its own axes (plane stress)."""
    nu21 = nu12 * E2 / E1; d = 1 - nu12 * nu21
    return np.array([[E1 / d, nu12 * E2 / d, 0], [nu12 * E2 / d, E2 / d, 0], [0, 0, G12]])


def Qbar(Qm, th):
    """Rotate the ply stiffness by angle th (rad) with the strain transformation (engineering shear)."""
    c, s = math.cos(th), math.sin(th)
    T = np.array([[c * c, s * s, 2 * c * s], [s * s, c * c, -2 * c * s], [-c * s, c * s, c * c - s * s]])
    R = np.diag([1, 1, 2.0])
    return np.linalg.inv(T) @ Qm @ R @ T @ np.linalg.inv(R)


def Ex_offaxis(E1, E2, G12, nu12, th):
    c, s = math.cos(th), math.sin(th)
    return 1 / (c**4 / E1 + (1 / G12 - 2 * nu12 / E1) * s * s * c * c + s**4 / E2)


def laminate_Ex(angles_deg, props, t_ply=0.125e-3, load_deg=0.0):
    """Effective in-plane modulus of a symmetric laminate along direction load_deg."""
    Qm = Q(*props); A = sum(Qbar(Qm, math.radians(a)) * t_ply for a in angles_deg); h = t_ply * len(angles_deg)
    Ar = Qbar(A / h, math.radians(-load_deg)) if load_deg else A / h
    return 1 / np.linalg.inv(Ar)[0, 0]


if __name__ == "__main__":
    E1, E2, G12, nu12 = ply()
    print(f"carbon/epoxy ply, 60 % fibre: E1 = {E1/1e9:.1f} GPa, E2 = {E2/1e9:.2f} GPa, G12 = {G12/1e9:.2f} GPa, nu12 = {nu12:.2f}")
    for d in (0, 5, 15, 30, 45, 90):
        print(f"  load at {d:2d} deg to the fibres: E = {Ex_offaxis(E1, E2, G12, nu12, math.radians(d))/1e9:.1f} GPa")
    # the matrix rotation agrees with the closed-form off-axis modulus
    for d in (10, 37, 60):
        Ex = 1 / np.linalg.inv(Qbar(Q(E1, E2, G12, nu12), math.radians(d)))[0, 0]
        assert abs(Ex - Ex_offaxis(E1, E2, G12, nu12, math.radians(d))) < 1e-6 * Ex
    qi = [0, 45, -45, 90, 90, -45, 45, 0]
    Eqi = [laminate_Ex(qi, (E1, E2, G12, nu12), load_deg=a) for a in (0, 22.5, 45, 70)]
    print("quasi-isotropic [0/45/-45/90]s: E = " + ", ".join(f"{e/1e9:.2f}" for e in Eqi) + " GPa at 0, 22.5, 45, 70 deg")
    assert max(Eqi) - min(Eqi) < 1e-6 * Eqi[0]
    rho = 0.6 * 1800 + 0.4 * 1200
    print(f"density {rho:.0f} kg/m^3; specific stiffness {Eqi[0]/rho/1e6:.1f} vs aluminium {70e9/2700/1e6:.1f} MJ/kg")
    assert reuss(230e9, 3.5e9, 0.6) < voigt(230e9, 3.5e9, 0.6)
