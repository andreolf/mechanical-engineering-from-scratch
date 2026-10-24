"""Train run between two stations: closed-form time versus an event-driven simulation."""
import math


def run_time(D, vmax, a, b):
    s1, s3 = vmax**2 / (2 * a), vmax**2 / (2 * b)
    if s1 + s3 <= D:
        return D / vmax + vmax / 2 * (1 / a + 1 / b), vmax
    vp = math.sqrt(2 * D * a * b / (a + b))
    return vp * (1 / a + 1 / b), vp


def simulate(D, vmax, a, b, dt=0.5):
    t = x = v = 0.0
    while True:
        brake_dist = v * v / (2 * b)
        if D - x <= brake_dist + 1e-12:           # braking phase: finish analytically
            return t + v / b
        if v < vmax:                              # accelerating
            # time until line speed, or until the braking curve is hit, whichever first
            t_v = (vmax - v) / a
            # solve x + v*tau + a*tau^2/2 + (v + a*tau)^2/(2b) = D for tau
            A = a / 2 + a * a / (2 * b)
            B = v + a * v / b
            C = x + v * v / (2 * b) - D
            t_b = (-B + math.sqrt(B * B - 4 * A * C)) / (2 * A)
            tau = min(dt, t_v, t_b)
            x += v * tau + a * tau * tau / 2
            v = min(vmax, v + a * tau)
        else:                                     # cruising until the braking point
            tau = min(dt, (D - brake_dist - x) / v)
            x += v * tau
        t += tau


if __name__ == "__main__":
    v = 125 / 3.6
    T, vp = run_time(8000, v, 0.7, 0.9)
    Ts = simulate(8000, v, 0.7, 0.9)
    print(f"8 km at 125 km/h: formula {T:.6f} s, simulation {Ts:.6f} s")
    assert abs(T - Ts) < 1e-6 and abs(T - 274.4917) < 1e-3
    T2, vp2 = run_time(1000, v, 0.7, 0.9)                 # too short to reach line speed
    assert vp2 < v and abs(T2 - simulate(1000, v, 0.7, 0.9)) < 1e-6
    T3, _ = run_time(8000, 160 / 3.6, 0.7, 0.9)
    print(f"160 km/h saves {T - T3:.1f} s")
    assert abs((T - T3) - 38.054) < 1e-2
