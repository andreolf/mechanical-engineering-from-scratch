"""GUM uncertainty propagation two ways: linearisation (first-order Taylor, numerical partial
derivatives) and Monte Carlo (GUM Supplement 1). Case 1, a pendulum measurement of g, is close
to linear and the two agree. Case 2, a weir discharge from a small measured head, is not. numpy only."""
import numpy as np

def type_a(x):
    """Type A: standard uncertainty of the mean of n repeated readings, s / sqrt(n)."""
    x = np.asarray(x, float)
    return x.mean(), x.std(ddof=1) / np.sqrt(len(x))

def type_b_rect(half_width):
    """Type B, rectangular distribution of half-width a (a resolution or a tolerance): a / sqrt(3)."""
    return half_width / np.sqrt(3)

def linearised(f, x, u):
    """u_c^2 = sum (df/dx_i)^2 u_i^2 for independent inputs; derivatives by central differences."""
    x, u = np.asarray(x, float), np.asarray(u, float)
    c = np.empty_like(x)
    for i in range(len(x)):
        h = 1e-6 * max(abs(x[i]), 1e-12)
        xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        c[i] = (f(*xp) - f(*xm)) / (2 * h)
    return f(*x), np.sqrt(np.sum((c * u) ** 2)), c

def monte_carlo(f, samplers, M=400_000, seed=1):
    rng = np.random.default_rng(seed)
    y = f(*[s(rng, M) for s in samplers])
    lo, hi = np.percentile(y, [2.5, 97.5])
    return y.mean(), y.std(ddof=1), lo, hi

# ---------- case 1: g from a pendulum, g = 4 pi^2 L / T^2 ----------
# ten stopwatch readings of 20 swings each, seconds
t20 = np.array([40.13, 40.21, 40.08, 40.17, 40.25, 40.11, 40.19, 40.06, 40.22, 40.15])
T, uT_a = type_a(t20 / 20)                       # period and its type A uncertainty
uT = np.hypot(uT_a, type_b_rect(0.01) / 20)       # add the 0.01 s stopwatch resolution, spread over 20 swings
L, uL = 1.0000, type_b_rect(0.002)               # tape measure to the bob centre, +-2 mm
g = lambda L, T: 4 * np.pi**2 * L / T**2
gl, ugl, c = linearised(g, [L, T], [uL, uT])
gm, ugm, lo, hi = monte_carlo(g, [lambda r, M: L + uL * np.sqrt(3) * r.uniform(-1, 1, M),
                                  lambda r, M: T + uT * r.standard_normal(M)])
print(f"T = {T:.5f} s, u(T) = {uT:.5f} s (type A {uT_a:.5f}); L = {L:.4f} m, u(L) = {uL:.5f} m")
print(f"sensitivity coefficients dg/dL = {c[0]:.4f} 1/s^2, dg/dT = {c[1]:.4f} m/s^3")
print(f"linearised: g = {gl:.4f} m/s^2, u_c = {ugl:.4f}, expanded (k=2) U = {2*ugl:.4f}")
print(f"Monte Carlo: mean {gm:.4f}, u = {ugm:.4f}, 95 % interval [{lo:.4f}, {hi:.4f}]")
budget = (c * [uL, uT]) ** 2 / ugl**2
print(f"budget: length {budget[0]*100:.1f} %, period {budget[1]*100:.1f} %")
assert abs(ugm / ugl - 1) < 0.02 and abs(gm - gl) < 0.1 * ugl     # near-linear: methods agree

# ---------- case 2: sharp-crested weir, Q = (2/3) Cd b sqrt(2 g) h^1.5, small head ----------
Cd, uCd = 0.62, 0.02
b, ub = 0.50, type_b_rect(0.005)
h, uh = 0.040, 0.008                               # head of 40 mm read off a staff gauge, +-8 mm (1 sigma): ripples
Q = lambda Cd, b, h: 2 / 3 * Cd * b * np.sqrt(2 * 9.81) * np.clip(h, 0, None) ** 1.5
Ql, uQl, _ = linearised(Q, [Cd, b, h], [uCd, ub, uh])
Qm, uQm, qlo, qhi = monte_carlo(Q, [lambda r, M: Cd + uCd * r.standard_normal(M),
                                    lambda r, M: b + ub * np.sqrt(3) * r.uniform(-1, 1, M),
                                    lambda r, M: h + uh * r.standard_normal(M)])
print(f"weir: linearised Q = {Ql*1e3:.3f} L/s +- {2*uQl*1e3:.3f} (k=2) -> [{(Ql-2*uQl)*1e3:.3f}, {(Ql+2*uQl)*1e3:.3f}]")
print(f"weir: Monte Carlo mean {Qm*1e3:.3f} L/s, u = {uQm*1e3:.3f}, 95 % interval [{qlo*1e3:.3f}, {qhi*1e3:.3f}]")
assert Qm > Ql * 1.01                    # h^1.5 is convex: the mean is biased up
assert (qhi - Ql) > 1.15 * (Ql - qlo)     # and the interval is lopsided: linearisation misses this
