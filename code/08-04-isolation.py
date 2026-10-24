"""Base excitation: transmissibility of a mountain-bike suspension, checked by time simulation."""
import math
import numpy as np


def transmissibility(r, zeta):
    """|X / Y| for a mass on a spring and damper whose base moves as Y sin(w t)."""
    return np.sqrt((1 + (2 * zeta * r)**2) / ((1 - r**2)**2 + (2 * zeta * r)**2))


def simulate_base(m, c, k, y, yd, t_end, dt):
    """RK4 on m x'' = -c (x' - y') - k (x - y) for a prescribed base motion y(t)."""
    f = lambda t, s: np.array([s[1], (-c * (s[1] - yd(t)) - k * (s[0] - y(t))) / m])
    s = np.zeros(2); t = 0.0; xs = [0.0]
    for _ in range(int(round(t_end / dt))):
        k1 = f(t, s); k2 = f(t + dt/2, s + dt/2*k1); k3 = f(t + dt/2, s + dt/2*k2); k4 = f(t + dt, s + dt*k3)
        s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4); t += dt; xs.append(s[0])
    return np.arange(len(xs)) * dt, np.array(xs)


if __name__ == "__main__":
    m, k, zeta = 80.0, 25e3, 0.3               # rider and frame on the suspension
    wn = math.sqrt(k / m); c = 2 * zeta * math.sqrt(k * m)
    print(f"f_n = {wn/(2*math.pi):.3f} Hz, c = {c:.0f} N s/m")
    # the crossover at r = sqrt 2 holds for every damping ratio
    for z in (0.05, 0.3, 0.7):
        assert abs(transmissibility(math.sqrt(2), z) - 1) < 1e-12
        r = np.linspace(1.4143, 10, 2000); assert np.all(transmissibility(r, z) < 1)
    # cobbles 0.25 m apart, 10 mm high, ridden at 2 and 5 m/s
    for v in (2.0, 5.0):
        w = 2 * math.pi * v / 0.25; Y = 0.005
        Tr = transmissibility(w / wn, zeta)
        t, x = simulate_base(m, c, k, lambda t: Y * math.sin(w * t), lambda t: Y * w * math.cos(w * t), 6.0, 2e-4)
        Xs = (x[t > 4].max() - x[t > 4].min()) / 2
        print(f"{v} m/s: cobble frequency {w/(2*math.pi):.1f} Hz, r = {w/wn:.3f}, transmissibility {Tr:.4f} (simulated {Xs/Y:.4f})")
        assert abs(Xs / Y / Tr - 1) < 5e-3
    # more damping helps at resonance and hurts above sqrt 2
    for z in (0.1, 0.3, 0.6):
        print(f"zeta {z}: T at resonance {transmissibility(1.0, z):.3f}, at r = 3 {transmissibility(3.0, z):.4f}")
    # a single 30 mm half-sine bump 0.3 m long
    for v in (1.0, 3.0, 8.0):
        L, H = 0.3, 0.03; tb = L / v
        y = lambda t: H * math.sin(math.pi * t / tb) if 0 <= t <= tb else 0.0
        yd = lambda t: H * math.pi / tb * math.cos(math.pi * t / tb) if 0 <= t <= tb else 0.0
        t, x = simulate_base(m, c, k, y, yd, 2.0, 1e-4)
        print(f"bump at {v} m/s: rider rises {x.max()*1000:.1f} mm (bump is 30 mm)")
