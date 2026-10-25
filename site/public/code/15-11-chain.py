"""Chain and belt drives: the polygonal (chordal) speed fluctuation of a sprocket, simulated pin by pin, and belt tensions from the capstan equation with centrifugal tension."""
import math
import numpy as np


def pitch_radius(p, N):
    return p / (2 * math.sin(math.pi / N))


def simulate_chain_speed(p, N, omega=1.0, samples=200001):
    """Sprocket turning at omega. The straight top span leaves from whichever pin is nearest the top; the chain
    moves with that pin's horizontal velocity. Sampled over two tooth periods, velocity by central differences."""
    R = pitch_radius(p, N)
    t = np.linspace(0, 2 * (2 * math.pi / N) / omega, samples)
    h = 1e-7
    pins = 2 * math.pi * np.arange(N) / N
    ang = omega * t[:, None] + pins[None, :]                       # pin angles from the top
    wrapped = (ang + math.pi) % (2 * math.pi) - math.pi
    j = np.argmin(np.abs(wrapped), axis=1)                          # the pin at the top carries the span
    a0 = wrapped[np.arange(len(t)), j]
    v = (R * np.sin(a0 + omega * h) - R * np.sin(a0 - omega * h)) / (2 * h)
    return v.min(), v.max()


def capstan(T2, mu, wrap):
    return T2 * math.exp(mu * wrap)


if __name__ == "__main__":
    p = 12.7  # bicycle chain pitch, mm
    prev = None
    for N in (11, 14, 18, 25, 32, 42):
        vmin, vmax = simulate_chain_speed(p, N)
        R = pitch_radius(p, N)
        fluct = 1 - vmin / vmax
        print(f"{N:2d} teeth: pitch radius {R:.3f} mm, speed {vmin:.4f} to {vmax:.4f} (x omega), fluctuation {100*fluct:.3f}% (theory {100*(1-math.cos(math.pi/N)):.3f}%)")
        assert abs(vmax / R - 1) < 1e-6 and abs(fluct - (1 - math.cos(math.pi / N))) < 1e-4
        if prev is not None:
            assert fluct < prev
        prev = fluct
    # flat belt on a scooter-sized pulley: 2 kW at 12 m/s, wrap 160 degrees, mu = 0.35, belt 0.12 kg/m
    P, v, mu, wrap, mass = 2000.0, 12.0, 0.35, math.radians(160), 0.12
    Tc = mass * v**2
    ratio = math.exp(mu * wrap)
    dT = P / v                         # T1 - T2 carried by friction
    T2 = dT / (ratio - 1) + Tc         # capstan acts on the tensions above the centrifugal part
    T1 = T2 + dT
    print(f"e^(mu theta) = {ratio:.4f}; centrifugal {Tc:.2f} N; tight side {T1:.1f} N, slack side {T2:.1f} N; initial tension {(T1+T2)/2:.1f} N")
    assert abs((T1 - Tc) / (T2 - Tc) - ratio) < 1e-12
    # V-belt: the wedge multiplies the friction by 1/sin(half angle)
    mu_v = mu / math.sin(math.radians(20))
    print(f"V-belt with a 40 degree groove: effective mu {mu_v:.4f}, e^(mu' theta) = {math.exp(mu_v*wrap):.2f}")
