"""Atomic bonding and stiffness: from a Lennard-Jones pair potential to a bond stiffness and an estimate of Young's modulus."""
import math
import numpy as np


def lj(r, eps, sig):
    return 4 * eps * ((sig / r)**12 - (sig / r)**6)


def lj_force(r, eps, sig):
    """F = -dV/dr (positive = repulsive)."""
    return 24 * eps / r * (2 * (sig / r)**12 - (sig / r)**6)


def lj_stiffness_analytic(eps, sig):
    """V''(r0) at r0 = 2^(1/6) sigma: 72 eps / (2^(1/3) sigma^2)."""
    return 72 * eps / (2**(1 / 3) * sig**2)


if __name__ == "__main__":
    eps, sig = 1.65e-21, 3.40e-10          # argon
    r0 = 2**(1 / 6) * sig
    h = 1e-13
    S_fd = (lj(r0 + h, eps, sig) - 2 * lj(r0, eps, sig) + lj(r0 - h, eps, sig)) / h**2
    S = lj_stiffness_analytic(eps, sig)
    print(f"argon: r0 = {r0*1e9:.4f} nm, well depth {eps/1.602e-19*1000:.2f} meV")
    print(f"bond stiffness: analytic {S:.4f} N/m, finite-difference second derivative {S_fd:.4f} N/m")
    assert abs(S_fd / S - 1) < 1e-4
    # the force is zero at r0 and its slope there is -S
    assert abs(lj_force(r0, eps, sig)) < 1e-20
    slope = (lj_force(r0 + 1e-14, eps, sig) - lj_force(r0 - 1e-14, eps, sig)) / 2e-14
    assert abs(-slope / S - 1) < 1e-4
    # E ~ S / r0 (one bond per r0^2 area, stretching by strain * r0)
    print(f"E estimate S / r0 = {S/r0/1e9:.2f} GPa (solid argon is measured at roughly 1 to 3 GPa)")
    # largest attractive force: the theoretical tensile strength of a bond
    rs = np.linspace(r0, 2 * sig, 200001); F = lj_force(rs, eps, sig)
    i = np.argmin(F)
    print(f"maximum bond force {-F[i]*1e12:.3f} pN at r = {rs[i]/r0:.4f} r0 (strain {rs[i]/r0-1:.3f}); stress estimate {-F[i]/r0**2/1e6:.0f} MPa = E / {S/r0/(-F[i]/r0**2):.1f}")
    assert abs(rs[i] / r0 - (26 / 7)**(1 / 6) / 2**(1 / 6)) < 1e-5
    # asymmetry of the well: the mean separation grows with vibration energy, which is thermal expansion
    for Eth in (0.05, 0.2):
        lo = r0 - 1e-12; hi = r0 + 1e-12
        while lj(lo, eps, sig) < -eps * (1 - Eth): lo -= 1e-14
        while lj(hi, eps, sig) < -eps * (1 - Eth): hi += 1e-14
        print(f"vibrating at {Eth*100:.0f} % of the well depth: turning points {lo/r0:.4f} and {hi/r0:.4f} r0, midpoint {(lo+hi)/2/r0:.4f} r0")
    # a stiff metallic-type bond: S = 50 N/m at r0 = 0.25 nm
    print(f"metal-like bond, S = 50 N/m, r0 = 0.25 nm: E ~ {50/0.25e-9/1e9:.0f} GPa")
