"""Fit a cooling time constant by linear regression on ln(T - T_ambient)."""
import math
import random


def fit_line(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def fit_tau(ts, Ts, Ta):
    a, b = fit_line(ts, [math.log(T - Ta) for T in Ts])
    return -1.0 / b, Ta + math.exp(a)


if __name__ == "__main__":
    rng = random.Random(7)
    Ta, T0, tau = 22.0, 85.0, 19.78
    ts = [0.5 * k for k in range(0, 61)]                     # 30 minutes, every 30 s
    Ts = [Ta + (T0 - Ta) * math.exp(-t / tau) + rng.gauss(0, 0.15) for t in ts]
    tau_fit, T0_fit = fit_tau(ts, Ts, Ta)
    print(f"fitted tau = {tau_fit:.2f} min (true {tau}), T0 = {T0_fit:.2f} C")
    assert abs(tau_fit / tau - 1) < 0.02                     # the lesson's test
    tau_c = 10 / math.log(63 / 38)
    assert abs(tau_c - 19.7805) < 1e-4 and abs(tau_c * math.log(63 / 28) - 16.0406) < 1e-4
    assert abs(math.exp(1.5) * math.exp(0.7) - math.exp(2.2)) < 1e-12
