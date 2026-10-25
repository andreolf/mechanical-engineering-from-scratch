"""Thermocouple time constant from a plunge test. The probe obeys tau dTs/dt = T - Ts. Three ways
to identify tau from noisy samples: the 63.2 % time, a log-linear least-squares fit, and a full
non-linear Gauss-Newton fit of (T_inf, T_0, tau, t_0). numpy only."""
import numpy as np

tau_true, T0, Tinf, t0 = 1.50, 22.0, 80.0, 0.37     # s, deg C: a 3 mm sheathed probe plunged into 80 C water at t0
fs = 20.0
t = np.arange(0, 12, 1 / fs)
rng = np.random.default_rng(4)
model = lambda p, t: p[1] + (p[0] - p[1]) * (1 - np.exp(-np.clip(t - p[3], 0, None) / p[2]))   # p = Tinf, T0, tau, t0
T = model([Tinf, T0, tau_true, t0], t) + 0.15 * rng.standard_normal(len(t))                    # 0.15 K noise

# 1) 63.2 % of the step: needs the start time, read off the first jump
pre, post = T[t < 0.3].mean(), T[t > 10].mean()
ts = t[np.argmax(T > pre + 5 * 0.15)] - 1 / fs / 2                 # first sample clearly above the noise
t63 = t[np.argmax(T > pre + 0.632 * (post - pre))]
tau1 = t63 - ts
# 2) log-linear: ln((Tinf - T)/(Tinf - T0)) = -(t - t0)/tau, using the 5 % to 90 % part of the rise
y = (post - T) / (post - pre)
m = (y < 0.95) & (y > 0.10)
slope, icpt = np.polyfit(t[m], np.log(y[m]), 1)
tau2, t0_2 = -1 / slope, icpt / (-slope)
# 3) Gauss-Newton on all four parameters, numerical Jacobian
p = np.array([post, pre, tau2, t0_2])
for it in range(30):
    r = T - model(p, t)
    J = np.empty((len(t), 4))
    for k in range(4):
        dp = np.zeros(4); dp[k] = 1e-6 * max(1, abs(p[k]))
        J[:, k] = (model(p + dp, t) - model(p - dp, t)) / (2 * dp[k])
    step = np.linalg.lstsq(J, r, rcond=None)[0]
    p += step
    if np.max(np.abs(step / p)) < 1e-10: break
s = np.sqrt(np.sum((T - model(p, t)) ** 2) / (len(t) - 4))
u_tau = s * np.sqrt(np.linalg.inv(J.T @ J)[2, 2])
print(f"true tau = {tau_true} s")
print(f"63.2 % time:        tau = {tau1:.3f} s ({(tau1/tau_true-1)*100:+.1f} %)")
print(f"log-linear fit:     tau = {tau2:.3f} s ({(tau2/tau_true-1)*100:+.1f} %), t0 = {t0_2:.3f} s")
print(f"Gauss-Newton ({it+1} iterations): tau = {p[2]:.4f} +- {u_tau:.4f} s ({(p[2]/tau_true-1)*100:+.2f} %), T_inf = {p[0]:.3f}, T_0 = {p[1]:.3f}, t0 = {p[3]:.4f}")
for tau in (tau1, tau2, p[2]): assert abs(tau / tau_true - 1) < 0.05      # all within 5 %
assert abs(p[2] - tau_true) < 3 * u_tau + 0.01

# what the time constant means: a lumped bead tau = rho c d / (6 h)
rho_c = 8700 * 450                                   # J/(m^3 K), nickel-chromium wire
for d, h, where in ((0.5e-3, 2000, "0.5 mm bead in stirred water"), (0.5e-3, 100, "0.5 mm bead in moving air")):
    print(f"{where:30s}: tau = {rho_c * d / (6 * h):.3f} s")
# dynamic error: following a ramp of rate R, a first-order sensor lags by R tau
R = 5 / 60
print(f"oven ramp 5 K/min: steady lag = {R*p[2]:.3f} K behind the air")
tt = np.linspace(0, 60, 60001); Ts = np.zeros_like(tt); Ta = R * tt
for i in range(1, len(tt)): Ts[i] = Ts[i - 1] + (tt[i] - tt[i - 1]) * (Ta[i - 1] - Ts[i - 1]) / tau_true
assert abs((Ta[-1] - Ts[-1]) - R * tau_true) < 1e-3
