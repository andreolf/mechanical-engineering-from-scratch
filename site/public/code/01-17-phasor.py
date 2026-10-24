"""Phasor arithmetic for same-frequency oscillations, checked sample by sample."""
import cmath
import math


def phasor(amplitude, phase_deg):
    return amplitude * cmath.exp(1j * math.radians(phase_deg))


def signal(ph, w, t):
    return (ph * cmath.exp(1j * w * t)).real    # A cos(w t + phi)


def amp_phase(ph):
    return abs(ph), math.degrees(cmath.phase(ph))


if __name__ == "__main__":
    w = 2 * math.pi * 50
    p1, p2 = phasor(2.0, 0), phasor(1.5, 60)
    total = p1 + p2
    A, phi = amp_phase(total)
    print(f"sum: {A:.4f} mm at {phi:.2f} deg")
    assert abs(A - 3.0414) < 1e-4 and abs(phi - 25.285) < 1e-3
    # the lesson's test: phasor sum equals the sum of time signals at every sample
    for k in range(1000):
        t = k * 1e-5
        assert abs(signal(total, w, t) - (signal(p1, w, t) + signal(p2, w, t))) < 1e-12
    # 3 cos(wt) + 4 sin(wt): sin is cos lagging 90 degrees
    A2, phi2 = amp_phase(phasor(3, 0) + phasor(4, -90))
    assert abs(A2 - 5) < 1e-12 and abs(phi2 + 53.130) < 1e-3
    # derivative: velocity phasor is i*w times displacement phasor
    v = 1j * w * total
    t, h = 1.234e-3, 1e-8
    num = (signal(total, w, t + h) - signal(total, w, t - h)) / (2 * h)
    assert abs(num - signal(v, w, t)) < 1e-4 * abs(v)
