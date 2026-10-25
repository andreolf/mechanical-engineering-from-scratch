"""Discharge of a canal by the velocity-area method: mid-section sums from current-meter readings
at 0.6 depth, and the float method with a surface-to-mean coefficient. A synthetic cross-section
with a 1/7-power velocity profile gives the exact answer to compare against. numpy only."""
import numpy as np

B, D, Us = 3.0, 0.8, 0.9          # canal width m, max depth m, max surface velocity m/s
depth = lambda y: D * np.clip(1 - (2 * y / B - 1) ** 2, 0, None)           # parabolic bed
usurf = lambda y: Us * (depth(y) / D) ** (2 / 3)                             # faster where deeper (Manning-like)
u = lambda y, z: usurf(y) * np.clip(z / np.maximum(depth(y), 1e-12), 0, 1) ** (1 / 7)   # z above the bed

# exact discharge: the depth-mean of a 1/7 profile is 7/8 of the surface value
yf = np.linspace(0, B, 200_001)
Q_exact = np.trapezoid(7 / 8 * usurf(yf) * depth(yf), yf)
zf = np.linspace(0, 1, 100_001)
assert abs(np.trapezoid(zf ** (1 / 7), zf) - 7 / 8) < 1e-6
print(f"exact Q = {Q_exact:.5f} m^3/s, area {np.trapezoid(depth(yf), yf):.5f} m^2 (2BD/3 = {2*B*D/3:.5f})")
print(f"0.6 depth below the surface is 0.4 d above the bed: u/u_s = 0.4^(1/7) = {0.4**(1/7):.5f} vs mean 0.875")

def mid_section(yv, dv, vv):
    """ISO 748 mid-section method: Q = sum v_i d_i w_i, panel width w_i = (y_{i+1} - y_{i-1}) / 2."""
    yy = np.concatenate([[0.0], yv, [B]])                      # the banks have zero depth
    w = (yy[2:] - yy[:-2]) / 2
    A = dv * w
    return np.sum(vv * A), A

rng = np.random.default_rng(2)
print(" verticals   Q, 0.6-depth meter   error    Q, floats (k=0.85)   error")
for n in (5, 10, 20):
    yv = (np.arange(n) + 0.5) * B / n
    dv = depth(yv) + 0.005 * rng.standard_normal(n)            # wading rod read to about 5 mm
    v06 = u(yv, 0.4 * depth(yv)) * (1 + 0.02 * rng.standard_normal(n))   # current meter, 2 % repeatability
    Q06, A = mid_section(yv, dv, v06)
    assert abs(Q06 - np.sum(v06 * A)) < 1e-15                  # the discharge is the sum of v_i A_i
    L = 10.0                                                   # floats timed over 10 m
    tf = L / usurf(yv) * (1 + 0.04 * rng.standard_normal(n))   # stopwatch reaction, wind gusts
    Qf, _ = mid_section(yv, dv, 0.85 * L / tf)
    print(f"{n:6d} {Q06:16.4f} {(Q06/Q_exact-1)*100:+9.2f} % {Qf:16.4f} {(Qf/Q_exact-1)*100:+9.2f} %")
    if n >= 10: assert abs(Q06 / Q_exact - 1) < 0.05
yv = (np.arange(20) + 0.5) * B / 20
Qn, _ = mid_section(yv, depth(yv), u(yv, 0.4 * depth(yv)))
print(f"20 verticals, no reading errors: {Qn:.5f} ({(Qn/Q_exact-1)*100:+.2f} %): the rest of the error above is the instruments")
assert abs(Qn / Q_exact - 1) < 0.01
