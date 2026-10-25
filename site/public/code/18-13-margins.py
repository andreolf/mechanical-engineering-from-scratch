"""Frequency response and robustness: Bode data, gain and phase margins found numerically by
bisection on the crossover frequencies, the delay margin, and the Nyquist encirclement count.
Reference values were computed with python-control 0.10.2 (stability_margins). numpy only."""
import numpy as np

def freq(num, den, w, delay=0.0):
    s = 1j * w
    return np.polyval(num, s) / np.polyval(den, s) * np.exp(-s * delay)

def bisect(f, a, b, n=200):
    fa = f(a)
    for _ in range(n):
        m = np.sqrt(a * b); fm = f(m)
        if np.sign(fm) == np.sign(fa): a, fa = m, fm
        else: b = m
    return np.sqrt(a * b)

def margins(num, den, delay=0.0, w=np.geomspace(1e-3, 1e3, 20001)):
    L = freq(num, den, w, delay)
    mag, ph = np.abs(L), np.unwrap(np.angle(L))
    out = {}
    i = np.where(np.diff(np.sign(mag - 1)))[0]                   # gain crossover |L| = 1
    if len(i):
        wc = bisect(lambda x: abs(freq(num, den, x, delay)) - 1, w[i[0]], w[i[0] + 1])
        phc = np.interp(np.log(wc), np.log(w), ph)
        out['wc'], out['PM'] = wc, np.degrees(phc) + 180
        out['delay_margin'] = np.radians(out['PM']) / wc
    j = np.where(np.diff(np.sign(ph + np.pi)))[0]                # phase crossover arg L = -180 deg
    if len(j):                                                   # inside the bracket the angle of -L is near 0, no wrap
        wp = bisect(lambda x: np.angle(-freq(num, den, x, delay)), w[j[0]], w[j[0] + 1])
        out['wp'], out['GM'] = wp, 1 / abs(freq(num, den, wp, delay))
    return out

# case 1: L = 10 / (s (s + 1)(s + 5))
num, den = [10.0], [1.0, 6.0, 5.0, 0.0]
m1 = margins(num, den)
print(f"L = 10/(s(s+1)(s+5)): GM = {m1['GM']:.6f} ({20*np.log10(m1['GM']):.3f} dB) at {m1['wp']:.6f} rad/s; PM = {m1['PM']:.4f} deg at {m1['wc']:.6f} rad/s; delay margin {m1['delay_margin']:.4f} s")
ref = dict(GM=3.000000, PM=25.389823, wp=2.236068, wc=1.227064)       # python-control 0.10.2
for k, v in ref.items(): assert abs(m1[k] - v) < 1e-5 * max(1, abs(v)), (k, m1[k], v)
assert abs(m1['GM'] - 30 / 10) < 1e-9                                  # Routh: K_crit = 30
wc = m1['wc']; assert abs(wc**2 * (wc**2 + 1) * (wc**2 + 25) - 100) < 1e-6

# a pure delay eats phase: at the delay margin the loop is on the edge
Td = m1['delay_margin']
md = margins(num, den, delay=Td * 0.999)
print(f"with a {Td*0.999:.4f} s delay: PM = {md['PM']:.3f} deg, GM = {md['GM']:.4f}")
assert 0 < md['PM'] < 0.1

# case 2: the PI e-bike loop of lesson 18.12
m, c, ta, ts = 100.0, 1.2 * 0.5 * 25 / 3.6, 0.2, 0.3
Ku = 850.781; Tu = 1.5233
Kp, Ki = 0.3 * Ku, 0.3 * Ku / (4 * Tu)
numb = [Kp, Ki]; denb = np.polymul([1, 0], np.polymul([m, c], np.polymul([ta, 1], [ts, 1])))
m2 = margins(numb, denb)
print(f"e-bike PI loop: GM = {m2['GM']:.4f} ({20*np.log10(m2['GM']):.2f} dB), PM = {m2['PM']:.3f} deg at {m2['wc']:.4f} rad/s, delay margin {m2['delay_margin']*1e3:.1f} ms")
assert abs(m2['GM'] - 3.064163) < 1e-4 and abs(m2['PM'] - 33.174253) < 1e-3   # python-control 0.10.2

# Nyquist on a stable open loop, L = K/(s+1)^3: Z = N + P, with P = 0 open-loop RHP poles and N the
# number of clockwise encirclements of -1 as w runs from -inf to +inf
def clockwise_encirclements(K, W=1e4, n=400001):
    w = np.linspace(-W, W, n)
    L = K / (1j * w + 1) ** 3                                    # strictly proper: the big arc maps to 0, so the path closes
    return -round((np.unwrap(np.angle(L + 1))[-1] - np.angle(L[0] + 1)) / (2 * np.pi))
mc = margins([1.0], [1.0, 3.0, 3.0, 1.0])
print(f"L = 1/(s+1)^3: GM = {mc['GM']:.6f} at {mc['wp']:.6f} rad/s (exact 8 at sqrt 3)")
assert abs(mc['GM'] - 8) < 1e-6
for K in (4.0, 7.9, 8.1, 20.0):
    N = clockwise_encirclements(K)
    Z = int(np.sum(np.roots(np.polyadd([1.0, 3.0, 3.0, 1.0], [K])).real > 0))
    print(f"K = {K:5.1f}: Nyquist encircles -1 {N} times clockwise; closed-loop RHP poles {Z}")
    assert N == Z
m4 = margins([4.0], [1.0, 3.0, 3.0, 1.0])
print(f"K = 4: GM = {m4['GM']:.4f}, PM = {m4['PM']:.4f} deg (python-control: 2.0000, 27.1416)")
assert abs(m4['GM'] - 2) < 1e-6 and abs(m4['PM'] - 27.14163) < 1e-4
