"""Torricelli's law and draining tanks: v = sqrt(2 g h), quasi-steady, with RK4 against the closed form."""
import math

G = 9.81


def drain_time_cylinder(A, a, h0, Cd=0.61):
    """Closed form for a constant-area tank: t = (A / (Cd a)) sqrt(2 h0 / g)."""
    return A / (Cd * a) * math.sqrt(2 * h0 / G)


def simulate(area_of_h, a, h0, Cd=0.61, dt=0.05):
    """Integrate A(h) dh/dt = -Cd a sqrt(2 g h) with RK4 until the tank is empty; returns the time."""
    f = lambda h: -Cd * a * math.sqrt(2 * G * max(h, 0.0)) / area_of_h(max(h, 1e-9))
    h, t = h0, 0.0
    while h > 1e-6:
        k1 = f(h); k2 = f(h + dt / 2 * k1); k3 = f(h + dt / 2 * k2); k4 = f(h + dt * k3)
        h_new = h + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if h_new <= 1e-6:                          # last sliver: dh/dt ~ sqrt(h), so the remaining time is about 2 h / |dh/dt|
            t += 2 * h / (-f(h))
            break
        h, t = h_new, t + dt
    return t


if __name__ == "__main__":
    # a rain-water tank: 1.2 m diameter, 1.5 m of water, 25 mm outlet hole
    A, a, h0 = math.pi * 1.2 ** 2 / 4, math.pi * 0.025 ** 2 / 4, 1.5
    print(f"outflow speed at the start: {math.sqrt(2*G*h0):.3f} m/s; flow {0.61*a*math.sqrt(2*G*h0)*1000:.3f} L/s")
    t_exact = drain_time_cylinder(A, a, h0)
    t_num = simulate(lambda h: A, a, h0, dt=0.01)
    print(f"cylinder drains in {t_exact:.1f} s ({t_exact/60:.2f} min); RK4 {t_num:.1f} s")
    assert abs(t_num - t_exact) / t_exact < 2e-3
    print(f"half the water leaves in {drain_time_cylinder(A, a, h0) - drain_time_cylinder(A, a, h0/2):.1f} s; the rest takes {drain_time_cylinder(A, a, h0/2):.1f} s")
    # an inverted cone (funnel-shaped tank) of the same top radius and height: A(h) = pi (R h / H)^2
    R, H = 0.6, 1.5
    t_cone = simulate(lambda h: math.pi * (R * h / H) ** 2, a, H, dt=0.01)
    t_cone_exact = 2 / 5 * math.pi * R * R / (0.61 * a * math.sqrt(2 * G)) * math.sqrt(H)     # integral of h^1.5 dh
    print(f"cone drains in {t_cone:.1f} s (exact {t_cone_exact:.1f} s): it holds a third of the water and empties in {t_cone/t_exact:.2f} of the time")
    assert abs(t_cone - t_cone_exact) / t_cone_exact < 5e-3
