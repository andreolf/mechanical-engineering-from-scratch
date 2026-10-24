"""Bamboo: why a hollow culm with fibres crowded at the outside beats a solid rod of the same mass in bending."""
import math
import numpy as np

EF, EM = 40e9, 2e9          # bamboo fibre bundles and parenchyma matrix (along the culm), Pa


def tube_I(D, t):
    return math.pi / 64 * (D**4 - (D - 2 * t)**4)


def graded_EI(D, t, v_in, v_out, n=2000):
    """Bending stiffness of a thin-walled culm with fibre fraction varying linearly from v_in (inside) to v_out (outside).
    Integrates E(r) r^2 over the ring: I-contribution of a ring of radius r and width dr is pi r^3 dr."""
    ro, ri = D / 2, D / 2 - t
    r = np.linspace(ri, ro, n); v = v_in + (v_out - v_in) * (r - ri) / t
    E = v * EF + (1 - v) * EM
    f = E * math.pi * r**3
    EI = float(np.sum((f[1:] + f[:-1]) / 2 * np.diff(r)))
    g = v * 2 * math.pi * r
    vbar = float(np.sum((g[1:] + g[:-1]) / 2 * np.diff(r))) / (math.pi * (ro**2 - ri**2))
    return EI, vbar


if __name__ == "__main__":
    D, t = 0.100, 0.010
    A = math.pi / 4 * (D**2 - (D - 2 * t)**2); d_solid = math.sqrt(4 * A / math.pi)
    I_tube, I_solid = tube_I(D, t), math.pi * d_solid**4 / 64
    print(f"culm 100 x 10 mm: A = {A*1e6:.0f} mm^2, I = {I_tube*1e12/1e6:.3f}e6 mm^4")
    print(f"solid rod of the same area: d = {d_solid*1e3:.1f} mm, I = {I_solid*1e12/1e6:.4f}e6 mm^4; tube is {I_tube/I_solid:.2f} times stiffer")
    assert abs(I_tube / I_solid - (D**2 + (D - 2 * t)**2) / d_solid**2) < 1e-9
    EIg, vbar = graded_EI(D, t, 0.15, 0.60)
    EIu, _ = graded_EI(D, t, vbar, vbar)
    print(f"graded fibres (15 % inside to 60 % outside, mean {vbar*100:.1f} %): EI = {EIg/1e3:.1f} kN m^2")
    print(f"same fibres spread evenly: EI = {EIu/1e3:.1f} kN m^2; grading adds {(EIg/EIu-1)*100:.1f} %")
    assert abs(EIu - (vbar * EF + (1 - vbar) * EM) * I_tube) < 1e-6 * EIu and EIg > EIu
    # wood across the grain: the same fibres in the wrong direction
    E_along, E_across = 12e9, 0.8e9
    print(f"spruce: E along the grain {E_along/1e9:.0f} GPa, across {E_across/1e9:.1f} GPa, ratio {E_along/E_across:.0f}")
