"""Stress waves on impact: a striker rod hits a bar end-on; exact characteristic (leapfrog) scheme at Courant number 1."""
import math
import numpy as np

E, rho = 210e9, 7850.0
c = math.sqrt(E / rho); Z = rho * c           # wave speed and impedance per unit area


def simulate(L1, L2, v0, nx_per_m=200, t_end=2e-3):
    """f: right-going velocity part, g: left-going. Particle velocity v = f + g, stress (tension +) s = Z (g - f).
    Striker cells 0..n1-1, bar cells n1..n1+n2-1. The interface transmits compression only."""
    dx = 1 / nx_per_m; dt = dx / c; n1, n2 = int(L1 * nx_per_m), int(L2 * nx_per_m)
    f = np.zeros(n1 + n2); g = np.zeros(n1 + n2); f[:n1] = g[:n1] = v0 / 2
    probe = n1 + n2 - int(0.25 * nx_per_m)                # 0.25 m from the bar's free end
    hist = []; contact = True; t_sep = None
    for step in range(int(t_end / dt)):
        fa, gb = f[n1 - 1], g[n1]                         # waves arriving at the interface from each side
        sig_if = Z * (gb - fa)
        if contact and sig_if > 0:
            contact = False; t_sep = step * dt
        fn = np.empty_like(f); gn = np.empty_like(g)
        fn[1:] = f[:-1]; gn[:-1] = g[1:]
        fn[0] = g[0]                                       # free left end of striker: s = 0 means f = g
        gn[-1] = f[-1]                                     # free right end of bar
        if not contact:                                    # separated: both interface faces are free
            gn[n1 - 1] = f[n1 - 1]; fn[n1] = g[n1]
        f, g = fn, gn
        hist.append((step * dt, Z * (g[probe] - f[probe]), Z * (g[n1 + 5] - f[n1 + 5]), sig_if if contact else 0.0))
    return np.array(hist), f, g, n1, t_sep, dx


if __name__ == "__main__":
    L1, L2, v0 = 1.0, 2.0, 5.0
    hist, f, g, n1, t_sep, dx = simulate(L1, L2, v0)
    print(f"steel: c = {c:.1f} m/s; impact stress rho c v / 2 = {Z*v0/2/1e6:.2f} MPa")
    smin = hist[:, 2].min()
    print(f"simulated peak compression near the impact face: {smin/1e6:.2f} MPa")
    assert abs(smin + Z * v0 / 2) < 1e-6 * Z * v0
    tf = hist[:, 0][hist[:, 3] < -0.5 * Z * v0 / 2]
    dur = tf.max() - tf.min() + dx / c
    print(f"contact force lasts {dur*1e3:.4f} ms (2 L1 / c = {2*L1/c*1e3:.4f} ms); the faces part for good at {t_sep*1e3:.4f} ms")
    assert abs(dur - 2 * L1 / c) < 2 * dx / c
    v = f + g
    print(f"after the impact: striker velocity {v[:n1].mean():.4f} m/s, bar momentum per area {rho*dx*v[n1:].sum():.2f} kg/(m^2 s) (striker had {rho*L1*v0:.2f})")
    assert abs(v[:n1]).max() < 1e-9 and abs(rho * dx * v[n1:].sum() - rho * L1 * v0) < 1e-6 * rho * L1 * v0
    # the probe near the free end first sees compression, then the reflected pulse as tension
    t, sp = hist[:, 0], hist[:, 1]
    tc = t[np.argmax(sp < -1e6)]; tt = t[np.argmax(sp > 1e6)]
    print(f"probe 0.25 m from the free end: compression {sp.min()/1e6:.2f} MPa from t = {tc*1e3:.4f} ms, tension {sp.max()/1e6:.2f} MPa from t = {tt*1e3:.4f} ms")
    assert sp.max() > 0.99 * Z * v0 / 2 and tt > tc
    # the overlap of incoming compression and reflected tension cancels near the end: the probe is 0.25 m from it, the pulse 2 m long
    E_k = 0.5 * rho * dx * np.sum(v**2) + 0.5 * dx * np.sum((Z * (g - f))**2) / E
    print(f"energy per area after: {E_k:.2f} J/m^2 (before {0.5*rho*L1*v0**2:.2f})")
    assert abs(E_k / (0.5 * rho * L1 * v0**2) - 1) < 1e-9
