"""Turbulent pipe friction: solve the Colebrook equation, compare with Haaland, and use Darcy-Weisbach for head loss."""
import math

G = 9.81


def colebrook(Re, rel_rough, tol=1e-14):
    """Darcy friction factor. Laminar below Re = 2300; otherwise fixed-point iteration on x = 1/sqrt(f)."""
    if Re < 2300:
        return 64 / Re
    x = 1 / math.sqrt(haaland(Re, rel_rough))
    for _ in range(100):
        x_new = -2 * math.log10(rel_rough / 3.7 + 2.51 * x / Re)
        if abs(x_new - x) < tol: break
        x = x_new
    return 1 / x_new ** 2


def haaland(Re, rel_rough):
    return (-1.8 * math.log10((rel_rough / 3.7) ** 1.11 + 6.9 / Re)) ** -2


def head_loss(Q, D, L, rough, nu=1.0e-6):
    V = Q / (math.pi * D * D / 4); Re = V * D / nu
    f = colebrook(Re, rough / D)
    return f * L / D * V * V / (2 * G), f, Re, V


if __name__ == "__main__":
    for Re in (500, 1000, 2000):
        assert colebrook(Re, 1e-3) == 64 / Re                     # laminar limit, roughness doesn't matter
    print("laminar: f = 64/Re for Re = 500, 1000, 2000 ->", [round(colebrook(R, 1e-3), 4) for R in (500, 1000, 2000)])
    for Re in (1e4, 1e5, 1e6, 1e8):
        for e in (0.0, 1e-4, 1e-2):
            f = colebrook(Re, e)
            x = 1 / math.sqrt(f)
            assert abs(x + 2 * math.log10(e / 3.7 + 2.51 * x / Re)) < 1e-12
        print(f"Re = {Re:.0e}: smooth {colebrook(Re, 0):.5f}, e/D = 1e-4 {colebrook(Re, 1e-4):.5f}, e/D = 0.01 {colebrook(Re, 1e-2):.5f} (Haaland {haaland(Re, 1e-2):.5f})")
    # a 1 km cast-iron main (D = 200 mm, roughness 0.26 mm) carrying 50 L/s
    hf, f, Re, V = head_loss(0.05, 0.2, 1000, 0.26e-3)
    print(f"water main: V = {V:.3f} m/s, Re = {Re:.3e}, f = {f:.5f}, head loss {hf:.3f} m ({1000*G*hf/1e5:.3f} bar)")
    # fully rough limit: f independent of Re
    print(f"fully rough e/D = 0.0013: f = {colebrook(1e9, 0.0013):.5f}, von Karman (2 log10(3.7 D/e))^-2 = {(2*math.log10(3.7/0.0013))**-2:.5f}")
