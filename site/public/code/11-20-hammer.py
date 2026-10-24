"""Water hammer in a penstock: the Joukowsky jump and a method-of-characteristics simulation of valve closure."""
import math
import numpy as np

G = 9.81


def wave_speed(K, rho, D, e, E):
    """Pressure wave speed in a liquid-filled elastic pipe."""
    return math.sqrt(K / rho / (1 + K * D / (E * e)))


def moc(L, a, V0, H0, t_close, t_end, N=40, f=0.0, D=0.5, law='area'):
    """Reservoir (fixed head H0) at x = 0, valve at x = L. Valve area falls linearly to zero over t_close.
    Characteristics C+ and C-: H = H_P -/+ (a/g)(V - V_P), with friction f. Returns times and valve head."""
    dx = L / N; dt = dx / a; B = a / G; R = f * dt / (2 * D)
    H = np.full(N + 1, H0) - (f * L / D * V0 * V0 / (2 * G)) * np.linspace(0, 1, N + 1)
    V = np.full(N + 1, V0)
    Hv0 = H[-1]; ts, hv = [0.0], [H[-1]]
    t = 0.0
    while t < t_end:
        t += dt
        Hn, Vn = H.copy(), V.copy()
        # interior points
        CP = H[:-2] + B * V[:-2] - B * R * V[:-2] * np.abs(V[:-2])
        CM = H[2:] - B * V[2:] + B * R * V[2:] * np.abs(V[2:])
        Hn[1:-1] = (CP + CM) / 2; Vn[1:-1] = (CP - CM) / (2 * B)
        # reservoir
        Hn[0] = H0; CM0 = H[1] - B * V[1] + B * R * V[1] * abs(V[1]); Vn[0] = (H0 - CM0) / B
        # valve: V = tau V0 sqrt(H / Hv0)
        tau = max(0.0, 1 - t / t_close) if t_close > 0 else 0.0
        CPv = H[-2] + B * V[-2] - B * R * V[-2] * abs(V[-2])
        if tau == 0: Vn[-1] = 0.0
        elif law == 'velocity': Vn[-1] = tau * V0
        else:   # V = tau V0 sqrt(H/Hv0) with H = CPv - B V: a quadratic in V
            Cv = (tau * V0) ** 2 / Hv0
            Vn[-1] = (-B * Cv + math.sqrt((B * Cv) ** 2 + 4 * Cv * CPv)) / 2
        Hn[-1] = CPv - B * Vn[-1]
        H, V = Hn, Vn
        ts.append(t); hv.append(H[-1])
    return np.array(ts), np.array(hv)


if __name__ == "__main__":
    a = wave_speed(2.2e9, 1000, 0.5, 0.01, 200e9)
    print(f"wave speed in a 0.5 m steel penstock, 10 mm wall: {a:.1f} m/s (rigid pipe: {math.sqrt(2.2e9/1000):.1f})")
    a = 1000.0; L = 600.0; V0 = 2.0; H0 = 100.0
    dH = a * V0 / G
    print(f"Joukowsky head rise a V0 / g = {dH:.3f} m ({1000*G*dH/1e5:.2f} bar); round trip 2L/a = {2*L/a:.2f} s")
    ts, hv = moc(L, a, V0, H0, 0.0, 6.0)
    print(f"MOC, instant closure: peak head {hv.max():.3f} m (rise {hv.max()-H0:.3f}), minimum {hv.min():.3f} m (would cavitate)")
    assert abs(hv.max() - H0 - dH) < 1e-6                                 # matches Joukowsky exactly
    # the head stays high for 2L/a, then the wave reverses
    dt = ts[1] - ts[0]
    n_high = np.count_nonzero((hv > H0 + dH / 2) & (ts < 2.0))
    print(f"high-pressure phase lasts {n_high * dt:.3f} s")
    assert abs(n_high * dt - 2 * L / a) < 1e-9
    for tc in (0.6, 1.2, 3.0, 6.0, 12.0):
        _, hl = moc(L, a, V0, H0, tc, tc + 8.0, law='velocity')
        _, hv = moc(L, a, V0, H0, tc, tc + 8.0)
        mich = 2 * L * V0 / (G * tc)
        print(f"closure over {tc:5.1f} s: linear velocity ramp {hl.max()-H0:7.2f} m, linear valve area {hv.max()-H0:7.2f} m" + (f", Michaud 2 L V0/(g tc) = {mich:.2f}" if tc > 2 * L / a else ""))
        if tc > 2 * L / a: assert abs(hl.max() - H0 - mich) < 1e-6            # the velocity ramp reproduces Michaud
        else: assert abs(hl.max() - H0 - dH) < 1e-6                          # closing within 2L/a gives the full Joukowsky rise
