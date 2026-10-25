"""Turbulent pipe flow from Prandtl's mixing length with van Driest damping: the mean
velocity profile in wall units, the viscous sublayer, the log law, and the friction factor
against Blasius and Prandtl's smooth-pipe law. numpy only."""
import numpy as np

kappa, Aplus = 0.41, 26.0

def profile(Re_tau, n=4000, const_stress=False):
    """u+(y+) across a pipe of radius Re_tau in wall units. The total shear stress falls
    linearly from the wall to zero on the axis: (1 + nu_t+) du+/dy+ = 1 - y+/Re_tau.
    const_stress=True gives the inner layer alone (stress = wall stress), the law of the wall."""
    yp = np.concatenate([[0], np.geomspace(1e-3, Re_tau, n)])
    lp = kappa * yp * (1 - np.exp(-yp / Aplus))                 # mixing length, wall units
    if const_stress:
        tau = np.ones_like(yp)
    else:
        eta = 1 - yp / Re_tau                                   # r / R
        lp = Re_tau * (0.14 - 0.08 * eta**2 - 0.06 * eta**4) * (1 - np.exp(-yp / Aplus))   # Nikuradse's l/R, van Driest damped
        tau = 1 - yp / Re_tau
    dudy = 2 * tau / (1 + np.sqrt(1 + 4 * lp**2 * tau))          # root of l^2 (du/dy)^2 + du/dy - tau = 0
    up = np.concatenate([[0], np.cumsum(0.5 * (dudy[1:] + dudy[:-1]) * np.diff(yp))])
    return yp, up

def bulk(Re_tau):
    yp, up = profile(Re_tau)
    r = Re_tau - yp                                              # radius in wall units
    Ub = 2 / Re_tau**2 * np.sum(0.5 * (up[1:] * r[1:] + up[:-1] * r[:-1]) * -np.diff(r))   # 2/R^2 int u r dr
    Re = 2 * Re_tau * Ub                                         # Re = Ub D / nu
    f = 8 / Ub**2                                                # Darcy f = 8 (u_tau / Ub)^2
    return Re, f, Ub, yp, up

Re_tau = 5000
Re, f, Ub, yp, up = bulk(Re_tau)
sub = yp < 3
print(f"Re_tau = {Re_tau}: bulk U+ = {Ub:.3f}, Re = {Re:.0f}; viscous sublayer: max |u+ - y+| / y+ for y+ < 3 is {np.max(abs(up[sub][1:] - yp[sub][1:]) / yp[sub][1:]):.4f}")
yw, uw = profile(1e4, const_stress=True)
m = (yw > 100) & (yw < 1e4)
slope, B = np.polyfit(np.log(yw[m]), uw[m], 1)
print(f"law of the wall (constant stress), fit for 100 < y+ < 10000: u+ = {slope:.4f} ln y+ + {B:.3f}  (1/kappa = {1/kappa:.4f}; the usual B is 5.0 to 5.5)")
m = (yp > 100) & (yp < 0.1 * Re_tau)
s2, B2 = np.polyfit(np.log(yp[m]), up[m], 1)
print(f"in the pipe itself the stress falls by up to 10 % over 100 < y+ < {0.1*Re_tau:.0f}: slope {s2:.4f}, intercept {B2:.3f}")
assert np.max(abs(up[sub][1:] - yp[sub][1:]) / yp[sub][1:]) < 0.01
assert abs(slope - 1 / kappa) < 0.01 and 4.8 < B < 5.8

print(" Re_tau      Re     f (mixing length)  Blasius   Prandtl smooth law")
for Rt in (200, 500, 1000, 2000, 5000):
    Re, f, *_ = bulk(Rt)
    fb = 0.316 * Re ** -0.25
    fp = 0.02
    for _ in range(50):
        fp = (2.0 * np.log10(Re * np.sqrt(fp)) - 0.8) ** -2
    print(f"{Rt:6d} {Re:8.0f}     {f:.5f}         {fb:.5f}   {fp:.5f}   ({(f/fp-1)*100:+.1f} % vs Prandtl)")
    assert abs(f / fp - 1) < (0.03 if Rt >= 500 else 0.1)
