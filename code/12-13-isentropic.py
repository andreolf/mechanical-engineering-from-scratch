"""Compressible flow basics: speed of sound, Mach number and the isentropic stagnation relations for air."""
import math

K, R = 1.4, 287.05
CP = K * R / (K - 1)


def sound_speed(T, k=K, Rg=R):
    return math.sqrt(k * Rg * T)


def stagnation_ratios(M, k=K):
    """T0/T, p0/p, rho0/rho for isentropic flow."""
    t = 1 + (k - 1) / 2 * M * M
    return t, t ** (k / (k - 1)), t ** (1 / (k - 1))


if __name__ == "__main__":
    # an airliner cruising at 11 km (T = 216.65 K, p = 22.632 kPa) at Mach 0.82
    T, p, M = 216.65, 22632.0, 0.82
    a = sound_speed(T); V = M * a
    tr, pr, rr = stagnation_ratios(M)
    T0 = T * tr
    print(f"a = {a:.3f} m/s, V = {V:.3f} m/s ({V*3.6:.1f} km/h)")
    print(f"T0/T = {tr:.5f}: T0 = {T0:.3f} K; p0/p = {pr:.5f}: p0 = {p*pr/1000:.3f} kPa")
    assert abs(CP * T + V * V / 2 - CP * T0) < 1e-6                   # T0/T = 1 + (k-1)/2 M^2 is just the energy equation
    # how wrong is incompressible Bernoulli? compare p0 - p with rho V^2 / 2
    for M in (0.1, 0.3, 0.5, 0.8):
        tr, pr, _ = stagnation_ratios(M)
        exact = pr - 1; bern = K / 2 * M * M                           # both divided by p
        print(f"M = {M}: (p0 - p)/p = {exact:.5f}, Bernoulli {bern:.5f}, error {100*(bern/exact - 1):+.2f} %")
        if M <= 0.3: assert abs(bern / exact - 1) < 0.025                # the usual incompressible limit
    # sound speed rises as sqrt(T): a hot day in Bali versus a cold Swiss winter
    print(f"sound speed at 32 C {sound_speed(305.15):.2f} m/s, at -10 C {sound_speed(263.15):.2f} m/s")
