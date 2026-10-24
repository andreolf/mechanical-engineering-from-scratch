"""Thwaites' method for a laminar boundary layer, used to find where the flow separates from a cylinder."""
import math
import numpy as np


def thwaites(xs, Ue, nu):
    """Momentum thickness theta^2 = 0.45 nu / Ue^6 * integral Ue^5 dx, and lambda = theta^2 Ue' / nu."""
    Ue5 = Ue ** 5
    integral = np.concatenate([[0.0], np.cumsum(0.5 * (Ue5[1:] + Ue5[:-1]) * np.diff(xs))])
    with np.errstate(divide="ignore", invalid="ignore"):
        th2 = 0.45 * nu * integral / Ue ** 6
    dUe = np.gradient(Ue, xs)
    th2[0] = 0.075 * nu / dUe[0]                      # stagnation-point limit
    return th2, th2 * dUe / nu


def separation_angle(ue_of_angle, R=1.0, U=1.0, nu=1e-5, n=200001):
    """Angle (degrees from the front stagnation point) where lambda first falls to -0.09."""
    ang = np.linspace(1e-6, math.radians(170), n)
    xs = ang * R
    Ue = U * ue_of_angle(ang)
    _, lam = thwaites(xs, Ue, nu)
    i = np.argmax(lam < -0.09)
    a = ang[i - 1] + (-0.09 - lam[i - 1]) * (ang[i] - ang[i - 1]) / (lam[i] - lam[i - 1])
    return math.degrees(a), ang, lam


if __name__ == "__main__":
    ideal = lambda a: 2 * np.sin(a)
    hiemenz = lambda a: 1.814 * a - 0.271 * a ** 3 - 0.0471 * a ** 5          # fit to measured pressures, subcritical cylinder
    s1, ang, lam = separation_angle(ideal)
    print(f"lambda at the stagnation point {lam[0]:.4f}; at 60 deg {np.interp(math.pi/3, ang, lam):.4f}, at 120 deg {np.interp(2*math.pi/3, ang, lam):.4f}")
    print(f"ideal-flow pressure distribution: separation at {s1:.2f} deg")
    # literature: 104.5 deg for the exact boundary-layer solution (Terrill), 109.5 deg from Pohlhausen's method
    assert abs(s1 - 104.5) < 2.0                                             # Thwaites lands within 2 degrees of the exact value
    s2, _, _ = separation_angle(hiemenz)
    print(f"measured (Hiemenz) pressure distribution: separation at {s2:.2f} deg (experiments: about 80 deg)")
    # the result doesn't depend on Re or the size: theta scales out of lambda
    s3, _, _ = separation_angle(ideal, R=0.2, U=7.0, nu=1.5e-5)
    assert abs(s3 - s1) < 1e-6
    # momentum thickness on a 0.3 m boulder in a 1 m/s river at 90 degrees
    R, U, nu = 0.15, 1.0, 1e-6
    ang = np.linspace(1e-6, math.pi / 2, 20001)
    th2, _ = thwaites(ang * R, U * 2 * np.sin(ang), nu)
    print(f"boulder: momentum thickness at 90 deg = {math.sqrt(th2[-1])*1000:.4f} mm")
