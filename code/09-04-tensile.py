"""The tensile test: process raw load-extension data into E, 0.2 % offset yield, UTS and elongation."""
import math
import numpy as np


def synthetic_test(E=69e3, K=380.0, n=0.06, d0=6.0, L0=30.0, seed=3):
    """Load (N) and extension (mm) for a round bar, from sigma_true = K eps_p^n with an elastic part,
    up to necking at true strain n (Considere). Units: MPa, mm, N."""
    s_true = np.linspace(1.0, K * n**n * 1.0, 4000)            # true stress up to the necking point
    eps_true = s_true / E + (s_true / K)**(1 / n)
    keep = eps_true <= n + s_true / E
    s_true, eps_true = s_true[keep], eps_true[keep]
    e_eng = np.exp(eps_true) - 1; s_eng = s_true / (1 + e_eng)
    A0 = math.pi * d0**2 / 4
    rng = np.random.default_rng(seed)
    load = s_eng * A0 + rng.normal(0, 5.0, s_eng.size)            # 5 N load-cell noise
    ext = e_eng * L0 + rng.normal(0, 0.0005, s_eng.size)          # 0.5 um extensometer noise
    return load, ext, A0, L0


def process(load, ext, A0, L0):
    s = load / A0; e = ext / L0
    smax = s.max()
    sel = (s > 0.1 * smax) & (s < 0.4 * smax)                     # clearly elastic window
    E, b = np.polyfit(e[sel], s[sel], 1)
    e0 = -b / E                                                   # toe correction: where the fitted line crosses zero
    offset = s - E * (e - e0 - 0.002)                             # positive left of the 0.2 % offset line
    i = np.argmax(offset < 0)
    t = offset[i - 1] / (offset[i - 1] - offset[i])
    sy = s[i - 1] + t * (s[i] - s[i - 1])
    return E, sy, smax, e[np.argmax(s)] - e0


if __name__ == "__main__":
    E_true, K, n = 69e3, 380.0, 0.06                               # an aluminium alloy
    load, ext, A0, L0 = synthetic_test(E_true, K, n)
    E, sy, uts, eu = process(load, ext, A0, L0)
    sy_true = K * 0.002**n
    uts_true = K * n**n * math.exp(-n)
    print(f"specimen d0 = 6 mm, A0 = {A0:.3f} mm^2, gauge 30 mm; {len(load)} data points")
    print(f"E = {E/1e3:.2f} GPa (input {E_true/1e3:.0f})")
    print(f"0.2 % offset yield {sy:.2f} MPa (exact K 0.002^n = {sy_true:.2f})")
    print(f"UTS {uts:.2f} MPa (Considere prediction K n^n e^-n = {uts_true:.2f}), uniform elongation {eu*100:.2f} % (Considere, elastic part included: {(math.exp(n + K*n**n/E_true)-1)*100:.2f} %)")
    assert abs(E / E_true - 1) < 0.02 and abs(sy / sy_true - 1) < 0.01 and abs(uts / uts_true - 1) < 0.005
    # true stress at the UTS point equals the hardening slope there (Considere)
    eps = n; s_t = K * eps**n; slope = n * K * eps**(n - 1)
    print(f"at necking: true stress {s_t:.2f} MPa = d sigma / d eps {slope:.2f} MPa")
    assert abs(s_t - slope) < 1e-9
