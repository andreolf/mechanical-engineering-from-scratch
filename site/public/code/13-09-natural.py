"""Natural convection on a vertical plate: the laminar similarity solution by two-parameter Newton shooting, against the Churchill-Chu correlations."""
import math
import numpy as np


def rhs(y, Pr):
    F, F1, F2, T, T1 = y
    return np.array([F1, F2, -3 * F * F2 + 2 * F1 * F1 - T, T1, -3 * Pr * F * T1])


def integrate(s, Pr, eta_end, n=3000):
    y = np.array([0.0, 0.0, s[0], 1.0, s[1]]); h = eta_end / n
    for _ in range(n):
        k1 = rhs(y, Pr); k2 = rhs(y + h / 2 * k1, Pr); k3 = rhs(y + h / 2 * k2, Pr); k4 = rhs(y + h * k3, Pr)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return y


def ostrach(Pr, eta_end=10.0):
    """F''' + 3FF'' - 2F'^2 + theta = 0, theta'' + 3 Pr F theta' = 0; F = F' = 0, theta = 1 at the wall; F' = theta = 0 far away.
    Newton on the unknown wall values (F''(0), theta'(0))."""
    s = np.array([0.68, -0.50])
    for _ in range(50):
        r = integrate(s, Pr, eta_end)[[1, 3]]
        J = np.zeros((2, 2))
        for j in range(2):
            ds = np.zeros(2); ds[j] = 1e-7
            J[:, j] = (integrate(s + ds, Pr, eta_end)[[1, 3]] - r) / 1e-7
        step = np.linalg.solve(J, -r); s = s + step
        if np.abs(step).max() < 1e-11: break
    return s


def churchill_chu(Ra, Pr):
    return (0.825 + 0.387 * Ra ** (1 / 6) / (1 + (0.492 / Pr) ** (9 / 16)) ** (8 / 27)) ** 2


def churchill_chu_laminar(Ra, Pr):
    return 0.68 + 0.670 * Ra ** 0.25 / (1 + (0.492 / Pr) ** (9 / 16)) ** (4 / 9)


if __name__ == "__main__":
    s72 = ostrach(0.72)
    print(f"Pr = 0.72: F''(0) = {s72[0]:.4f}, -theta'(0) = {-s72[1]:.4f} (Ostrach 1953 tabulates 0.6760 and 0.5046)")
    assert abs(s72[0] - 0.6760) < 5e-4 and abs(-s72[1] - 0.5046) < 5e-4
    Pr = 0.71
    s = ostrach(Pr)
    print(f"Pr = {Pr}: F''(0) = {s[0]:.4f}, -theta'(0) = {-s[1]:.4f}")
    # average Nu_L = (4/3)(Gr_L/4)^(1/4)(-theta'(0)) = C Ra^(1/4) with C below
    C = 4 / 3 * 0.25 ** 0.25 * (-s[1]) / Pr ** 0.25
    Ccc = 0.670 / (1 + (0.492 / Pr) ** (9 / 16)) ** (4 / 9)
    print(f"similarity: Nu_L = {C:.4f} Ra^1/4; Churchill-Chu laminar coefficient {Ccc:.4f}")
    assert abs(C - Ccc) < 0.01 * C
    # a 0.6 m radiator panel at 60 C in a 20 C room; air properties at the 40 C film temperature
    g, nu, k, L, dT = 9.81, 1.70e-5, 0.0271, 0.6, 40.0
    beta, alpha = 1 / 313.15, 1.70e-5 / Pr
    Ra = g * beta * dT * L ** 3 / (nu * alpha)
    Nu = churchill_chu_laminar(Ra, Pr)
    print(f"radiator: Ra = {Ra:.4e} (laminar); Nu = {Nu:.3f}, h = {Nu*k/L:.4f} W/(m^2 K), {Nu*k/L*dT*L:.2f} W per metre of width per face")
    assert Ra < 1e9
    # a 3 m sun-baked wall, 25 K above the air, is past transition
    Ra3 = g * beta * 25 * 3 ** 3 / (nu * alpha)
    Nu3 = churchill_chu(Ra3, Pr)
    print(f"3 m wall: Ra = {Ra3:.4e} (turbulent); Churchill-Chu Nu = {Nu3:.2f}, h = {Nu3*k/3:.4f}; simple 0.10 Ra^1/3 gives {0.10*Ra3**(1/3):.2f}")
    assert Ra3 > 1e9 and abs(Nu3 - 0.10 * Ra3 ** (1 / 3)) < 0.15 * Nu3
