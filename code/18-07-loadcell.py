"""A bending-beam load cell: size the beam for 1000 microstrain at rated load, predict the
full-bridge output, then calibrate it with known masses by least squares and report sensitivity,
zero, linearity error, hysteresis and the uncertainty of a reading. numpy only."""
import numpy as np

g = 9.81
E, Sy, GF = 69e9, 276e6, 2.0            # aluminium 6061-T6: modulus, yield; foil gauges
b, a, m_rated = 12.7e-3, 60e-3, 5.0     # beam width, load-to-gauge distance, rated mass
F = m_rated * g
h_req = np.sqrt(6 * F * a / (E * b * 1000e-6))          # eps = M c / (E I) = 6 F a / (E b h^2)
h = 4.5e-3
eps = 6 * F * a / (E * b * h**2)
sig = E * eps
print(f"required h = {h_req*1e3:.3f} mm, chosen {h*1e3:.1f} mm: strain {eps*1e6:.1f} microstrain, stress {sig/1e6:.1f} MPa, yield factor {Sy/sig:.2f}")
print(f"full bridge (2 gauges on top, 2 below): output GF eps = {GF*eps*1e3:.4f} mV/V at rated load")
assert 900e-6 < eps < 1100e-6 and Sy / sig > 3

# calibration: 0, 1, ..., 5 kg up then down; the 'true' cell has 0.05 % FS non-linearity and hysteresis
rng = np.random.default_rng(7)
Vex = 5.0
masses = np.r_[np.arange(6), np.arange(4, -1, -1)].astype(float)
up = np.r_[np.ones(6), np.zeros(5)].astype(bool)
FS = GF * eps * Vex * 1e3                                       # full-scale output, mV
x = masses / m_rated
true = 0.012 + FS * (x - 0.0005 * 4 * x * (1 - x)) + np.where(up, -1, 1) * 0.0002 * FS * np.sin(np.pi * x)
reading = true + 0.0004 * rng.standard_normal(len(masses))     # 0.4 microvolt amplifier noise, mV units
A = np.column_stack([np.ones_like(masses), masses])
coef, res, *_ = np.linalg.lstsq(A, reading, rcond=None)
zero, sens = coef
fit = A @ coef
resid = reading - fit
s = np.sqrt(np.sum(resid**2) / (len(masses) - 2))
cov = s**2 * np.linalg.inv(A.T @ A)
lin = np.max(np.abs(resid)) / (sens * m_rated) * 100
hyst = max(abs(reading[(masses == m) & ~up][0] - reading[(masses == m) & up][0]) for m in range(1, 5)) / (sens * m_rated) * 100
print(f"fit: zero {zero*1e3:.2f} microvolt, sensitivity {sens:.5f} mV/kg (+- {np.sqrt(cov[1,1]):.5f}); predicted {FS/m_rated:.5f} mV/kg")
print(f"best-fit-line linearity error {lin:.3f} % FS, hysteresis {hyst:.3f} % FS, residual s = {s*1e3:.2f} microvolt")
for m, r, e in zip(masses, reading, resid): print(f"  {m:3.0f} kg {r:9.5f} mV   residual {e*1e3:+7.2f} microvolt")
assert abs(sens / (FS / m_rated) - 1) < 0.01                  # the beam theory predicts the sensitivity to 1 %
assert lin < 0.1 and hyst < 0.1
# use: a reading of 4.21 mV; uncertainty of the inverse prediction m = (r - zero) / sens
r = 4.21
m_est = (r - zero) / sens
J = np.array([-1 / sens, -(r - zero) / sens**2])
u_m = np.sqrt(J @ cov @ J + (s / sens) ** 2)
print(f"reading {r} mV -> {m_est:.4f} kg +- {2*u_m*1e3:.1f} g (k = 2)")
assert 2 * u_m < 0.005
