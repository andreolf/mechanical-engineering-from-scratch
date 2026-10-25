"""Feedback and stability: the Routh-Hurwitz test from scratch, a root locus traced by sweeping
the gain, and the gain at which the closed-loop poles cross into the right half-plane, found both
ways. Also why feedback works: a 20 % change in the plant barely moves the closed loop. numpy only."""
import numpy as np

def routh(c, eps=1e-9):
    """Routh array of the polynomial c[0] s^n + ... + c[n]. Returns the array and the number of
    sign changes in its first column (= number of right-half-plane roots)."""
    c = np.asarray(c, float); n = len(c)
    cols = (n + 1) // 2
    R = np.zeros((n, cols))
    R[0, :len(c[0::2])] = c[0::2]; R[1, :len(c[1::2])] = c[1::2]
    for i in range(2, n):
        if abs(R[i - 1, 0]) < eps: R[i - 1, 0] = eps            # epsilon trick for a zero pivot
        for j in range(cols - 1):
            R[i, j] = (R[i - 1, 0] * R[i - 2, j + 1] - R[i - 2, 0] * R[i - 1, j + 1]) / R[i - 1, 0]
    first = R[:, 0]
    return R, int(np.sum(np.sign(first[:-1]) != np.sign(first[1:])))

def char_poly(num, den, K):
    return np.polyadd(den, K * np.asarray(num, float))       # 1 + K N/D = 0  ->  D + K N = 0

def crossing_gain(num, den, lo=1e-6, hi=1e6):
    """Bisection on 'is any closed-loop pole in the RHP', in log K."""
    unstable = lambda K: np.max(np.roots(char_poly(num, den, K)).real) > 0
    assert not unstable(lo) and unstable(hi)
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        lo, hi = (lo, mid) if unstable(mid) else (mid, hi)
    return np.sqrt(lo * hi)

# case 1: G = 1 / (s (s + 1)(s + 5)): characteristic s^3 + 6 s^2 + 5 s + K
num, den = [1.0], np.polymul([1, 0], np.polymul([1, 1], [1, 5]))
for K in (10, 30 - 1e-6, 30 + 1e-6, 50):
    R, nrhp = routh(char_poly(num, den, K))
    print(f"K = {K:9.6f}: Routh first column {np.round(R[:, 0], 4)}, RHP roots {nrhp}, from np.roots: {int(np.sum(np.roots(char_poly(num, den, K)).real > 0))}")
    assert nrhp == int(np.sum(np.roots(char_poly(num, den, K)).real > 0))
Kc = crossing_gain(num, den)
wc = np.max(np.abs(np.roots(char_poly(num, den, Kc)).imag))
print(f"root locus crosses the imaginary axis at K = {Kc:.6f}, omega = {wc:.6f} rad/s (Routh: K = 30, omega = sqrt 5 = {np.sqrt(5):.6f})")
assert abs(Kc - 30) < 1e-6 and abs(wc - np.sqrt(5)) < 1e-4

# the locus itself: closed-loop poles over a sweep of K
Ks = np.geomspace(0.01, 200, 20000)
locus = np.array([np.sort_complex(np.roots(char_poly(num, den, K))) for K in Ks])
brk = Ks[np.argmax(np.abs(locus[:, 1].imag) > 1e-6)]
print(f"two real poles meet and split off the axis at K = {brk:.3f} (breakaway point s = {np.real(locus[np.argmax(np.abs(locus[:, 1].imag) > 1e-6) - 1, 1]):.3f})")
sb = (-12 + np.sqrt(144 - 60)) / 6                           # dK/ds = 0: 3 s^2 + 12 s + 5 = 0
print(f"breakaway from dK/ds = 0: s = {sb:.4f}, K = {-np.polyval(den, sb):.4f}")
assert abs(brk + np.polyval(den, sb)) < 0.005

# case 2: the positioner from lesson 18.10: 0.1 s^3 + 2.2 s^2 + 6.5 s + 50 + Kp
num2, den2 = [1.0], np.polymul([0.05, 1], [2, 4, 50])
Kc2 = crossing_gain(num2, np.polyadd(den2, [0]))
print(f"positioner: unstable above Kp = {Kc2:.4f} (Routh: (22*65 - 500)/10 = {(22*65-500)/10:.1f}), oscillating at {np.max(np.abs(np.roots(char_poly(num2, den2, Kc2)).imag)):.4f} rad/s (sqrt 65 = {np.sqrt(65):.4f})")
assert abs(Kc2 - 93) < 1e-5

# why feedback works: plant gain drops 20 %, closed loop with K = 20 on G0 = 10 / (s + 1)
for g in (10.0, 8.0):
    print(f"plant DC gain {g:4.1f}: open-loop output {g:5.2f}, closed loop K = 20 -> {20*g/(1+20*g):.4f}")
dT = (20 * 8 / 161) / (20 * 10 / 201) - 1
print(f"a 20 % plant change moves the closed loop by {dT*100:.3f} % (sensitivity 1/(1 + KG) = {1/201:.4f})")
assert abs(dT) < 0.0015
