"""Rotating unbalance: response of a washing-machine drum on its suspension."""
import math
import numpy as np


def amplitude(M, m, e, k, zeta, w):
    """Steady amplitude of M x'' + c x' + k x = m e w^2 cos(w t)."""
    wn = math.sqrt(k / M); r = w / wn
    return m * e / M * r**2 / math.sqrt((1 - r**2)**2 + (2 * zeta * r)**2)


def simulate(M, m, e, k, zeta, w, cycles=80, per=100):
    c = 2 * zeta * math.sqrt(k * M); dt = 2 * math.pi / w / per
    f = lambda t, s: np.array([s[1], (m * e * w**2 * math.cos(w * t) - c * s[1] - k * s[0]) / M])
    s = np.zeros(2); t = 0.0; xs = []
    for i in range(cycles * per):
        k1 = f(t, s); k2 = f(t + dt/2, s + dt/2*k1); k3 = f(t + dt/2, s + dt/2*k2); k4 = f(t + dt, s + dt*k3)
        s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4); t += dt
        if i >= (cycles - 5) * per: xs.append(s[0])
    return (max(xs) - min(xs)) / 2


if __name__ == "__main__":
    M, m, e, k, zeta = 40.0, 0.5, 0.25, 40e3, 0.1     # drum assembly (incl. laundry), unbalanced lump, suspension
    wn = math.sqrt(k / M)
    print(f"suspension resonance {wn:.2f} rad/s = {wn*30/math.pi:.0f} rpm; m e / M = {m*e/M*1000:.3f} mm")
    for rpm in (150, 302, 600, 1400):
        w = rpm * math.pi / 30; X = amplitude(M, m, e, k, zeta, w)
        line = f"{rpm:5d} rpm: amplitude {X*1000:.3f} mm"
        if rpm in (150, 600, 1400):
            Xs = simulate(M, m, e, k, zeta, w); line += f" (simulated {Xs*1000:.3f})"; assert abs(Xs / X - 1) < 5e-3
        # force through spring and damper into the floor
        r = w / wn; FT = k * X * math.sqrt(1 + (2 * zeta * r)**2)
        print(line + f", force to the floor {FT:.0f} N (the lump itself pulls with {m*e*w*w:.0f} N)")
    w = 1400 * math.pi / 30
    assert abs(amplitude(M, m, e, k, zeta, w) / (m * e / M) - 1) < 0.06
    hi = amplitude(M, m, e, k, zeta, 1e5)
    print(f"very high speed: {hi*1000:.4f} mm -> m e / M; the drum spins about the combined centre of mass")
    assert abs(hi / (m * e / M) - 1) < 1e-6
