"""A Butcher-tableau Runge-Kutta engine: Euler, Heun (RK2) and classical RK4, with measured orders on a pendulum."""
import math
import numpy as np

TABLEAUS = {
    "Euler": ([[0]], [1], [0]),
    "Heun": ([[0, 0], [1, 0]], [0.5, 0.5], [0, 1]),
    "midpoint": ([[0, 0], [0.5, 0]], [0, 1], [0, 0.5]),
    "RK4": ([[0, 0, 0, 0], [0.5, 0, 0, 0], [0, 0.5, 0, 0], [0, 0, 1, 0]], [1 / 6, 1 / 3, 1 / 3, 1 / 6], [0, 0.5, 0.5, 1]),
}


def rk_step(f, t, y, h, tableau):
    A, b, c = (np.array(m, float) for m in tableau)
    k = []
    for i in range(len(b)):
        yi = y + h * sum(A[i, j] * k[j] for j in range(i)) if i else y
        k.append(f(t + c[i] * h, yi))
    return y + h * sum(bi * ki for bi, ki in zip(b, k))


def solve(f, y0, t_end, n, tableau):
    h = t_end / n; y = np.array(y0, float)
    for i in range(n):
        y = rk_step(f, i * h, y, h, tableau)
    return y


def pendulum(t, y, g=9.81, L=1.0):
    return np.array([y[1], -g / L * math.sin(y[0])])


if __name__ == "__main__":
    y0 = [math.radians(60), 0.0]; T = 2.0
    ref = solve(pendulum, y0, T, 20000, TABLEAUS["RK4"])      # converged reference
    print(f"reference angle after {T} s: {math.degrees(ref[0]):.6f} deg")
    print(" method     n=50 error    n=100 error   observed order")
    orders = {}
    for name in ("Euler", "Heun", "midpoint", "RK4"):
        e = [abs(solve(pendulum, y0, T, n, TABLEAUS[name])[0] - ref[0]) for n in (50, 100, 200)]
        orders[name] = math.log2(e[1] / e[2])
        print(f" {name:9s} {e[0]:12.3e} {e[1]:13.3e} {orders[name]:12.2f}")
    assert abs(orders["Euler"] - 1) < 0.15 and abs(orders["Heun"] - 2) < 0.1 and abs(orders["RK4"] - 4) < 0.1
    # cost: RK4 with 50 steps (200 evaluations) beats Euler with 20000 steps
    e_rk4 = abs(solve(pendulum, y0, T, 50, TABLEAUS["RK4"])[0] - ref[0])
    e_eul = abs(solve(pendulum, y0, T, 20000, TABLEAUS["Euler"])[0] - ref[0])
    print(f"RK4, 200 evaluations: {e_rk4:.1e} rad; Euler, 20000 evaluations: {e_eul:.1e} rad")
    assert e_rk4 < e_eul
