"""Newmark-beta time integration on a two-storey steel portal frame (frame elements, lumped floor masses, Rayleigh damping) under harmonic ground shaking; average acceleration is unconditionally stable and conserves energy, central difference blows up beyond its limit."""
import math
import numpy as np


def k_frame(E, A, I, x1, y1, x2, y2):
    L = math.hypot(x2 - x1, y2 - y1); c, s = (x2 - x1) / L, (y2 - y1) / L
    a, b, d, e = E * A / L, 12 * E * I / L**3, 6 * E * I / L**2, E * I / L
    kl = np.array([[a, 0, 0, -a, 0, 0], [0, b, d, 0, -b, d], [0, d, 4 * e, 0, -d, 2 * e], [-a, 0, 0, a, 0, 0], [0, -b, -d, 0, b, -d], [0, d, 2 * e, 0, -d, 4 * e]])
    T = np.zeros((6, 6))
    for i in (0, 3): T[i:i + 3, i:i + 3] = [[c, s, 0], [-s, c, 0], [0, 0, 1]]
    return T.T @ kl @ T


def portal(E=210e9, storey=3.5, bay=6.0, Ac=7.81e-3, Ic=6.1e-5, Ab=7.64e-3, Ib=1.6e-4, floor_mass=20000.0):
    """Two storeys, one bay. Columns HEB 200-like, beams IPE 360-like (section values rounded). Each floor's mass lumped half at each beam end, horizontal and vertical."""
    nodes = [(0, 0), (bay, 0), (0, storey), (bay, storey), (0, 2 * storey), (bay, 2 * storey)]
    elems = [(0, 2, Ac, Ic), (1, 3, Ac, Ic), (2, 4, Ac, Ic), (3, 5, Ac, Ic), (2, 3, Ab, Ib), (4, 5, Ab, Ib)]
    n = 3 * len(nodes); K = np.zeros((n, n)); M = np.zeros((n, n))
    for i, j, A, I in elems:
        d = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        K[np.ix_(d, d)] += k_frame(E, A, I, *nodes[i], *nodes[j])
    for k in (2, 3, 4, 5):
        M[3 * k, 3 * k] = M[3 * k + 1, 3 * k + 1] = floor_mass / 2
        M[3 * k + 2, 3 * k + 2] = floor_mass / 2 * 0.05     # small rotary inertia keeps M positive definite
    free = list(range(6, n))
    return K[np.ix_(free, free)], M[np.ix_(free, free)]


def gen_eig(K, M):
    Li = np.linalg.inv(np.linalg.cholesky(M)); lam, y = np.linalg.eigh(Li @ K @ Li.T)
    return lam, Li.T @ y


def newmark(K, M, C, F, dt, nsteps, beta=0.25, gamma=0.5, u0=None, v0=None):
    """F(t) -> load vector. Returns displacement history."""
    n = len(K); u = np.zeros(n) if u0 is None else u0.copy(); v = np.zeros(n) if v0 is None else v0.copy()
    a = np.linalg.solve(M, F(0.0) - C @ v - K @ u)
    Keff = K + gamma / (beta * dt) * C + M / (beta * dt * dt)
    Kinv = np.linalg.inv(Keff); hist = [u.copy()]
    for s in range(1, nsteps + 1):
        t = s * dt
        rhs = F(t) + M @ (u / (beta * dt**2) + v / (beta * dt) + (1 / (2 * beta) - 1) * a) \
            + C @ (gamma / (beta * dt) * u + (gamma / beta - 1) * v + dt * (gamma / (2 * beta) - 1) * a)
        un = Kinv @ rhs
        an = (un - u) / (beta * dt**2) - v / (beta * dt) - (1 / (2 * beta) - 1) * a
        vn = v + dt * ((1 - gamma) * a + gamma * an)
        u, v, a = un, vn, an; hist.append(u.copy())
    return np.array(hist), v


def central_difference(K, M, u0, dt, nsteps):
    Minv = np.linalg.inv(M); a0 = -Minv @ K @ u0
    u = u0.copy(); prev = u0 + 0.5 * dt**2 * a0          # u(-dt) from a Taylor step with v0 = 0
    out = [u.copy()]
    for _ in range(nsteps):
        un = 2 * u - prev - dt**2 * Minv @ K @ u; prev, u = u, un; out.append(u.copy())
    return np.array(out)


if __name__ == "__main__":
    K, M = portal()
    lam, phi = gen_eig(K, M); w = np.sqrt(lam); f = w / (2 * math.pi)
    print(f"frame: {len(K)} dofs; f1 = {f[0]:.3f} Hz, f2 = {f[1]:.3f} Hz, highest {f[-1]:.1f} Hz (period {1000/f[-1]:.3f} ms)")
    # Rayleigh damping, 5 % in modes 1 and 2
    z = 0.05; a0, a1 = 2 * z * w[0] * w[1] / (w[0] + w[1]), 2 * z / (w[0] + w[1]); C = a0 * M + a1 * K
    # 1) undamped free vibration from a static sway with a time step 10x the shortest period: energy is conserved
    Fs = np.zeros(len(K)); Fs[[0, 6]] = 10e3   # 10 kN sideways at each floor (free dof 0: first floor u, dof 6: roof u)
    us = np.linalg.solve(K, Fs)
    dt_big = 10 / f[-1]
    hist, v = newmark(K, M, 0 * C, lambda t: np.zeros(len(K)), dt_big, 400, u0=us)
    E0 = 0.5 * us @ K @ us; E1 = 0.5 * hist[-1] @ K @ hist[-1] + 0.5 * v @ M @ v
    print(f"average acceleration, dt = {dt_big*1000:.3f} ms (10 x the shortest period), 400 steps: energy ratio {E1/E0:.12f}")
    assert abs(E1 / E0 - 1) < 1e-9 and np.abs(hist).max() <= np.abs(us).max() * 3
    # central difference: stable only for dt < 2 / w_max
    dt_crit = 2 / w[-1]
    ok = central_difference(K, M, us, 0.9 * dt_crit, 2000); bad = central_difference(K, M, us, 1.1 * dt_crit, 200)
    print(f"central difference: dt_crit = {dt_crit*1000:.4f} ms; at 0.9 dt_crit max |u| {np.abs(ok).max()*1000:.3f} mm; at 1.1 dt_crit {np.abs(bad).max():.2e} m (blown up)")
    assert np.abs(ok).max() < 3 * np.abs(us).max() and np.abs(bad).max() > 1e3 * np.abs(us).max()
    # 2) harmonic ground acceleration a_g = A sin(2 pi f t): effective load -M r a_g with r = 1 on horizontal dofs
    r = np.zeros(len(K)); r[0::3] = 1.0
    def roof_peak(fg, A=0.5, T=20.0, dt=0.005):
        hist, _ = newmark(K, M, C, lambda t: -M @ r * A * math.sin(2 * math.pi * fg * t), dt, int(T / dt))
        return np.abs(hist[:, 6]).max()
    peaks = {fg: roof_peak(fg) for fg in (0.5, f[0], 2 * f[0], 3 * f[0])}
    for fg, pk in peaks.items():
        print(f"ground shaking 0.5 m/s^2 at {fg:.3f} Hz: peak roof sway {pk*1000:.2f} mm")
    # SDOF estimate at resonance: modal participation, steady amplitude Gamma A / (2 zeta w1^2) times the roof modal value
    G1 = phi[:, 0] @ M @ r; est = abs(G1 * phi[6, 0]) * 0.5 / (2 * z * w[0]**2)
    print(f"modal estimate at resonance (mode 1 only, steady state): {est*1000:.2f} mm")
    assert max(peaks, key=peaks.get) == f[0] and abs(peaks[f[0]] / est - 1) < 0.1
