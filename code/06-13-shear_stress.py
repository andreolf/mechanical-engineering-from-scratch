"""Shear stress in beams by Jourawski's formula tau = V Q / (I b), for a rectangle and an I-section."""
import numpy as np


def jourawski(y, b_of_y, V):
    """y from bottom to top (centroid at 0 assumed). Q(y) = first moment of the area above y. Returns tau(y), I."""
    b = b_of_y(y)
    I = np.trapezoid(b * y**2, y)
    # Q(y) = int_y^top b(s) s ds, accumulated from the top down
    f = b * y
    Q = np.concatenate([np.cumsum(((f[1:] + f[:-1]) / 2 * np.diff(y))[::-1])[::-1], [0.0]])
    return V * Q / (I * b), I, Q


if __name__ == "__main__":
    V = 20e3                                             # N
    # rectangle 50 x 200
    b, h = 50.0, 200.0
    y = np.linspace(-h / 2, h / 2, 20001)
    tau, I, Q = jourawski(y, lambda y: b + 0 * y, V)
    print(f"rectangle: max tau {tau.max():.4f} MPa at y = {y[tau.argmax()]:.2f} mm (1.5 V/A = {1.5 * V / (b * h):.4f}); I = {I:.4e}")
    assert abs(tau.max() - 1.5 * V / (b * h)) < 1e-4 and abs(I - b * h**3 / 12) < 1e-3 * I
    assert abs(np.trapezoid(tau * b, y) - V) < 1e-3 * V          # the shear stresses add up to V
    # I-section from 06.10: flanges 100 x 8.5, web 5.6, depth 200
    H, B, tf, tw = 200.0, 100.0, 8.5, 5.6
    bI = lambda y: np.where(np.abs(y) > H / 2 - tf, B, tw)
    y = np.linspace(-H / 2, H / 2, 40001)
    tau, I, Q = jourawski(y, bI, V)
    web = np.abs(y) < H / 2 - tf
    k = np.argmin(np.abs(y - (H / 2 - tf + 0.01)))        # just inside the top flange
    print(f"I-section: max tau in the web {tau[web].max():.4f} MPa, at the web-flange junction {tau[web][-1]:.4f} MPa, just inside the flange {tau[k]:.4f} MPa")
    assert abs(tau[k] - tau[web][-1] * tw / B) < 0.05      # same Q, but spread over the flange width
    print(f"  average over the web V / (h_w t_w) = {V / ((H - 2 * tf) * tw):.4f} MPa; I = {I:.4e} mm^4")
    share = np.trapezoid(np.where(web, tau * tw, 0), y) / V
    print(f"  the web carries {share * 100:.1f} % of the shear force")
    assert share > 0.95 and abs(np.trapezoid(tau * bI(y), y) - V) < 2e-3 * V
