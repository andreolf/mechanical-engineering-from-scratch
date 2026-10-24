"""Viscoelastic polymers: Maxwell relaxation, Kelvin-Voigt creep and the standard linear solid, integrated step by step and checked against exact solutions."""
import math


def maxwell_relax(E, eta, eps0, t_end, dt=0.01):
    """Spring and dashpot in series held at strain eps0: d(sigma)/dt = -E/eta * sigma."""
    s, t, out = E * eps0, 0.0, []
    while t < t_end - 1e-12:
        k1 = -E / eta * s; k2 = -E / eta * (s + 0.5 * dt * k1); k3 = -E / eta * (s + 0.5 * dt * k2); k4 = -E / eta * (s + dt * k3)
        s += dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += dt
        out.append((t, s))
    return out


def kv_creep(E, eta, sigma, t_end, dt=0.01):
    """Spring and dashpot in parallel under constant stress: eta d(eps)/dt = sigma - E eps."""
    e, t, out = 0.0, 0.0, []
    f = lambda e: (sigma - E * e) / eta
    while t < t_end - 1e-12:
        k1 = f(e); k2 = f(e + 0.5 * dt * k1); k3 = f(e + 0.5 * dt * k2); k4 = f(e + dt * k3)
        e += dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += dt
        out.append((t, e))
    return out


def sls_creep(E1, E2, eta, sigma, t):
    """Standard linear solid (spring E1 in series with a Kelvin-Voigt unit E2, eta): instant then delayed strain."""
    return sigma / E1 + sigma / E2 * (1 - math.exp(-E2 * t / eta))


if __name__ == "__main__":
    E, eta = 2.0e9, 2.0e12         # Pa, Pa s: tau = 1000 s
    tau = eta / E
    hist = maxwell_relax(E, eta, 0.01, 3 * tau, dt=1.0)
    for tt, s in hist:
        if abs(tt - tau) < 0.5 or abs(tt - 3 * tau) < 0.5:
            print(f"Maxwell, held at 1 % strain: stress {s/1e6:.2f} MPa after {tt:.0f} s (started at 20 MPa)")
    assert abs(hist[-1][1] - 20e6 * math.exp(-3)) < 1e-3 * 20e6 * math.exp(-3)
    cr = kv_creep(E, eta, 10e6, 5 * tau, dt=1.0)
    for tt, e in cr:
        if abs(tt - tau) < 0.5:
            print(f"Kelvin-Voigt under 10 MPa: strain {e*100:.4f} % after one tau (limit 0.5 %)")
            assert abs(e - 0.005 * (1 - math.exp(-1))) < 1e-9
    # a nylon-like standard linear solid: 3 GPa instant, 6 GPa delayed, retardation 1 hour
    E1, E2 = 3e9, 6e9; eta2 = E2 * 3600
    for th in (0, 1, 3, 10):
        print(f"SLS under 15 MPa after {th} h: strain {sls_creep(E1, E2, eta2, 15e6, th*3600)*100:.3f} %")
    assert abs(sls_creep(E1, E2, eta2, 15e6, 1e9) - 15e6 * (1 / E1 + 1 / E2)) < 1e-12
