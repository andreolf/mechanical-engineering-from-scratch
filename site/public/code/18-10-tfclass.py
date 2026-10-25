"""A transfer-function class from scratch: polynomial algebra for series, parallel and feedback
connections, poles and zeros, and a step response through a state-space realisation and an exact
matrix-exponential discretisation. Checked against the closed-form response and a direct RK4
integration of the physical ODEs. numpy only."""
import numpy as np

class TF:
    def __init__(self, num, den):
        num, den = np.atleast_1d(np.asarray(num, float)), np.atleast_1d(np.asarray(den, float))
        num = np.trim_zeros(num, 'f') if np.any(num) else np.array([0.0])
        self.num, self.den = num / den[0], den / den[0]          # monic denominator
    def __mul__(self, o): o = o if isinstance(o, TF) else TF([o], [1]); return TF(np.polymul(self.num, o.num), np.polymul(self.den, o.den))
    __rmul__ = __mul__
    def __add__(self, o): o = o if isinstance(o, TF) else TF([o], [1]); return TF(np.polyadd(np.polymul(self.num, o.den), np.polymul(o.num, self.den)), np.polymul(self.den, o.den))
    def feedback(self, H=1.0):
        """Negative feedback G / (1 + G H)."""
        H = H if isinstance(H, TF) else TF([H], [1])
        return TF(np.polymul(self.num, H.den), np.polyadd(np.polymul(self.den, H.den), np.polymul(self.num, H.num)))
    def poles(self): return np.roots(self.den)
    def zeros(self): return np.roots(self.num) if len(self.num) > 1 else np.array([])
    def dcgain(self): return np.polyval(self.num, 0) / np.polyval(self.den, 0)
    def __call__(self, s): return np.polyval(self.num, s) / np.polyval(self.den, s)
    def ss(self):
        """Controllable canonical form (strictly proper part) plus direct feed-through D."""
        n = len(self.den) - 1
        num = np.r_[np.zeros(n + 1 - len(self.num)), self.num]
        D = num[0]; b = num[1:] - D * self.den[1:]             # remove the feed-through
        A = np.zeros((n, n)); A[0, :] = -self.den[1:]; A[1:, :-1] = np.eye(n - 1)
        B = np.zeros(n); B[0] = 1.0
        return A, B, b, D
    def step(self, t):
        A, B, Cr, D = self.ss(); n = len(B); h = t[1] - t[0]
        M = np.zeros((n + 1, n + 1)); M[:n, :n] = A * h; M[:n, n] = B * h
        E = expm(M); Ad, Bd = E[:n, :n], E[:n, n]              # exact for a step input held over each interval
        x = np.zeros(n); y = np.empty(len(t))
        for k in range(len(t)):
            y[k] = Cr @ x + D; x = Ad @ x + Bd
        return y

def expm(M):
    """Matrix exponential by scaling and squaring with a 16-term Taylor series."""
    s = max(0, int(np.ceil(np.log2(max(np.abs(M).sum(1).max(), 1e-16)))) + 1)
    X = M / 2**s; E = np.eye(len(M)); term = np.eye(len(M))
    for k in range(1, 17): term = term @ X / k; E = E + term
    for _ in range(s): E = E @ E
    return E

s = TF([1, 0], [1])                                            # the Laplace variable itself
m, c, k = 2.0, 4.0, 50.0
G = TF([1], [m, c, k])                                         # mass-spring-damper, force -> position
wn, zeta = np.sqrt(k / m), c / (2 * np.sqrt(k * m))
print(f"plant: wn = {wn:.4f} rad/s, zeta = {zeta:.4f}, poles {np.round(G.poles(), 4)}")
t = np.linspace(0, 6, 6001)
wd = wn * np.sqrt(1 - zeta**2)
exact = (1 - np.exp(-zeta * wn * t) * (np.cos(wd * t) + zeta / np.sqrt(1 - zeta**2) * np.sin(wd * t))) / k
yG = G.step(t)
print(f"open-loop step: max error vs closed form {np.max(abs(yG - exact)):.2e} m; overshoot {(yG.max()*k-1)*100:.2f} % (formula {np.exp(-zeta*np.pi/np.sqrt(1-zeta**2))*100:.2f} %)")
assert np.max(abs(yG - exact)) < 1e-12

act = TF([1], [0.05, 1])                                       # actuator lag, 50 ms
Kp = 50.0
T = (Kp * act * G).feedback(1.0)                               # unity feedback around actuator + plant
print(f"closed loop: den = {np.round(T.den, 4)}, poles {np.round(T.poles(), 4)}, DC gain {T.dcgain():.5f} (= Kp/(k+Kp) = {Kp/(k+Kp):.5f})")
assert abs(T.dcgain() - Kp / (k + Kp)) < 1e-12 and np.all(T.poles().real < 0)

# the same closed loop written as ODEs and integrated with RK4: e = r - x, 0.05 F' + F = Kp e, m x'' + c x' + k x = F
def f(z, r=1.0):
    x, v, F = z
    return np.array([v, (F - c * v - k * x) / m, (Kp * (r - x) - F) / 0.05])
z = np.zeros(3); h = t[1] - t[0]; xo = np.empty(len(t))
for i in range(len(t)):
    xo[i] = z[0]
    k1 = f(z); k2 = f(z + h / 2 * k1); k3 = f(z + h / 2 * k2); k4 = f(z + h * k3); z = z + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
yT = T.step(t)
print(f"closed-loop step from the TF vs RK4 on the ODEs: max difference {np.max(abs(yT - xo)):.2e}; peak {yT.max():.4f} at t = {t[np.argmax(yT)]:.3f} s, final {yT[-1]:.4f}")
assert np.max(abs(yT - xo)) < 1e-8
P = TF([1, 2], [1, 3]) + TF([1], [1, 1])                       # parallel connection check at s = 1j
assert abs(P(1j) - ((1j + 2) / (1j + 3) + 1 / (1j + 1))) < 1e-14
