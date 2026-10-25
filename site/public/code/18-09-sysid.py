"""System identification of a DC motor from step data: ARX models fitted by linear least squares.
The 'true' motor is a second-order electro-mechanical model simulated with RK4; the identified
gain, time constant and poles are compared with it, and the model is validated on fresh data. numpy only."""
import numpy as np

R, L, k, J, bv = 2.0, 8e-3, 0.03, 5.4e-5, 1e-5          # ohm, H, N m/A (= V s/rad), kg m^2, N m s/rad
A = np.array([[-R / L, -k / L], [k / J, -bv / J]])       # states: current i, speed w
Bm = np.array([1 / L, 0.0])
K_true = k / (R * bv + k * k)                            # steady speed per volt
poles_true = np.linalg.eigvals(A)
fs = 200.0; T = 1 / fs

def simulate(u, sub=40):
    """Zero-order-hold input, RK4 with 40 sub-steps per sample. Returns speed at the sample instants."""
    x = np.zeros(2); out = np.empty(len(u)); h = T / sub
    f = lambda x, v: A @ x + Bm * v
    for n, v in enumerate(u):
        out[n] = x[1]
        for _ in range(sub):
            k1 = f(x, v); k2 = f(x + h / 2 * k1, v); k3 = f(x + h / 2 * k2, v); k4 = f(x + h * k3, v)
            x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return out

def arx(y, u, na, nb):
    """y[n] = sum_i a_i y[n-i] + sum_j b_j u[n-j] + e[n], solved by least squares."""
    n0 = max(na, nb)
    Phi = np.column_stack([y[n0 - i: len(y) - i] for i in range(1, na + 1)] + [u[n0 - j: len(u) - j] for j in range(1, nb + 1)])
    th = np.linalg.lstsq(Phi, y[n0:], rcond=None)[0]
    return th[:na], th[na:]

def sim_arx(a, b, u):
    y = np.zeros(len(u))
    for n in range(len(u)):
        y[n] = sum(a[i] * y[n - 1 - i] for i in range(len(a)) if n - 1 - i >= 0) + sum(b[j] * u[n - 1 - j] for j in range(len(b)) if n - 1 - j >= 0)
    return y

rng = np.random.default_rng(8)
t = np.arange(0, 1.5, T)
u = np.where(t >= 0.05, 6.0, 0.0)                              # 6 V step at 50 ms
w = simulate(u) + 0.3 * rng.standard_normal(len(t))           # tachometer noise 0.3 rad/s
print(f"true motor: K = {K_true:.4f} rad/s/V, poles {np.sort(poles_true.real).round(3)} 1/s, mechanical tau = {-1/max(poles_true.real):.5f} s")

a1, b1 = arx(w, u, 1, 1)
tau1 = -T / np.log(a1[0]); K1 = b1[0] / (1 - a1[0])
print(f"ARX(1,1): a = {a1[0]:.6f}, b = {b1[0]:.6f} -> K = {K1:.4f} rad/s/V ({(K1/K_true-1)*100:+.2f} %), tau = {tau1:.5f} s ({(tau1/(-1/max(poles_true.real))-1)*100:+.2f} %)")
a2, b2 = arx(w, u, 2, 2)
zp = np.roots(np.r_[1, -a2]); sp = np.log(zp.astype(complex)) / T
K2 = b2.sum() / (1 - a2.sum())
print(f"ARX(2,2): K = {K2:.4f}, continuous poles from ln(z)/T = {np.sort(sp.real).round(2)}")
assert abs(K1 / K_true - 1) < 0.02 and 0 < tau1 / (-1 / max(poles_true.real)) - 1 < 0.10   # first order soaks up the electrical lag
assert abs(K2 / K_true - 1) < 0.02 and abs(max(sp.real) / max(poles_true.real) - 1) < 0.05

# validate on different data: a staircase of voltages the model has not seen
uv = np.repeat([0, 3, 9, 4, 12, 0, 6], 60).astype(float)
wv = simulate(uv)
for name, (a, b) in (("ARX(1,1)", (a1, b1)), ("ARX(2,2)", (a2, b2))):
    ym = sim_arx(a, b, uv)
    fit = 100 * (1 - np.linalg.norm(wv - ym) / np.linalg.norm(wv - wv.mean()))
    print(f"{name} validation fit (NRMSE) = {fit:.2f} %")
    assert fit > 95

# why noise matters: with 10x more output noise the ARX estimate of a is biased low (tau too short)
wn = simulate(u) + 3.0 * rng.standard_normal(len(t))
an, bn = arx(wn, u, 1, 1)
assert -1 / max(sp.real) < tau1                       # the second-order model separates the two lags
print(f"with 3 rad/s noise: tau = {-T/np.log(an[0]):.5f} s, K = {bn[0]/(1-an[0]):.4f}: equation-error bias")
