"""Belt and rope friction: T2 / T1 = exp(mu beta), checked by stacking many small slipping segments."""
import math
import numpy as np


def capstan_ratio(mu, beta):
    return math.exp(mu * beta)


def segments_ratio(mu, beta, n):
    """Split the wrap into n small arcs; each arc d(beta) is in limiting equilibrium:
    the normal force is ~ T d(beta) and friction mu N makes up the tension difference."""
    T = 1.0; db = beta / n
    for _ in range(n):
        # exact equilibrium of a short arc with entry tension T and exit tension T' (both tangent):
        # radial: N = (T + T') sin(db/2); tangential: (T' - T) cos(db/2) = mu N
        T = T * (math.cos(db / 2) + mu * math.sin(db / 2)) / (math.cos(db / 2) - mu * math.sin(db / 2))
    return T


if __name__ == "__main__":
    mu = 0.3
    for turns in (0.5, 1, 2, 3):
        beta = 2 * math.pi * turns
        print(f"{turns:3} turns round a bollard: holding ratio {capstan_ratio(mu, beta):9.2f}")
    beta = 6 * math.pi
    errs = []
    for n in (10, 100, 1000, 10000):
        r = segments_ratio(mu, beta, n); errs.append(abs(r / capstan_ratio(mu, beta) - 1))
        print(f"  {n:5d} segments: {r:.4f}")
    assert errs[-1] < 1e-5 and all(e1 > e2 for e1, e2 in zip(errs, errs[1:]))       # converges to the exponential
    # exponential in the wrap angle: each extra half turn multiplies the ratio by the same factor
    r = [capstan_ratio(mu, b) for b in np.arange(1, 6) * math.pi]
    assert np.allclose(np.array(r[1:]) / np.array(r[:-1]), math.exp(mu * math.pi))
    # a flat belt drive: 160 deg wrap on the small pulley, mu = 0.35, belt limited to 1.2 kN tight side
    beta, T1 = math.radians(160), 1.2
    T2 = T1 / capstan_ratio(0.35, beta)
    r_pulley, rpm = 0.08, 1450
    torque = (T1 - T2) * r_pulley; power = torque * rpm * 2 * math.pi / 60
    print(f"flat belt: slack side {T2:.4f} kN, torque {torque * 1000:.2f} N m, power {power:.3f} kW at {rpm} rpm")
    # V-belt with 40 deg groove: effective mu = mu / sin(20 deg)
    mu_v = 0.35 / math.sin(math.radians(20))
    print(f"V-belt: effective mu {mu_v:.4f}, ratio {capstan_ratio(mu_v, beta):.3f} vs flat {capstan_ratio(0.35, beta):.3f}")
