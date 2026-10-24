"""Closed-form damped oscillator versus a fourth-order Runge-Kutta integration."""
import math


def closed_form(t, x0, wn, z):
    if z < 1:
        wd = wn * math.sqrt(1 - z * z)
        return x0 * math.exp(-z * wn * t) * (math.cos(wd * t) + z * wn / wd * math.sin(wd * t))
    if z == 1:
        return x0 * (1 + wn * t) * math.exp(-wn * t)
    r = wn * math.sqrt(z * z - 1)
    s1, s2 = -z * wn + r, -z * wn - r
    return x0 / (s2 - s1) * (s2 * math.exp(s1 * t) - s1 * math.exp(s2 * t))


def rk4(x0, wn, z, T, dt):
    f = lambda x, v: (v, -2 * z * wn * v - wn * wn * x)
    x, v = x0, 0.0
    out = [(0.0, x)]
    for i in range(round(T / dt)):
        k1 = f(x, v)
        k2 = f(x + dt / 2 * k1[0], v + dt / 2 * k1[1])
        k3 = f(x + dt / 2 * k2[0], v + dt / 2 * k2[1])
        k4 = f(x + dt * k3[0], v + dt * k3[1])
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        v += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        out.append(((i + 1) * dt, x))
    return out


if __name__ == "__main__":
    m, k, c = 300.0, 20_000.0, 2000.0
    wn, z = math.sqrt(k / m), c / (2 * math.sqrt(k * m))
    print(f"wn = {wn:.3f} rad/s, zeta = {z:.3f}")
    assert abs(wn - 8.16497) < 1e-4 and abs(z - 0.408248) < 1e-5
    for zeta in (0.0, z, 1.0, 2.5):
        err = max(abs(x - closed_form(t, 0.05, wn, zeta)) for t, x in rk4(0.05, wn, zeta, 3.0, 1e-3))
        print(f"zeta={zeta:.3f}: max |RK4 - closed form| = {err:.1e} m")
        assert err < 1e-6                                     # the lesson's test
    ratio = math.exp(-z * math.pi / math.sqrt(1 - z * z))
    assert abs(ratio - 0.24538) < 1e-4
