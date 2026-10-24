"""Statistical process control: X-bar and R charts from subgroups, process capability Cp and Cpk, and catching a shift."""
import math
import numpy as np

A2, D3, D4, D2 = 0.577, 0.0, 2.114, 2.326     # constants for subgroups of 5
LSL, USL = 24.980, 25.020                     # shaft tolerance 25.000 +- 0.020 mm


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def capability(mu, sigma):
    cp = (USL - LSL) / (6 * sigma)
    cpk = min(USL - mu, mu - LSL) / (3 * sigma)
    ppm = 1e6 * (phi((LSL - mu) / sigma) + 1 - phi((USL - mu) / sigma))
    return cp, cpk, ppm


if __name__ == "__main__":
    rng = np.random.default_rng(11)
    mu, sigma = 25.004, 0.004
    groups = rng.normal(mu, sigma, (25, 5))
    xbar, R = groups.mean(axis=1), np.ptp(groups, axis=1)
    xbb, Rb = xbar.mean(), R.mean()
    s_hat = Rb / D2
    print(f"grand mean {xbb:.4f} mm, mean range {Rb*1000:.2f} um, sigma estimate {s_hat*1000:.2f} um (true 4.00)")
    assert abs(s_hat / sigma - 1) < 0.15
    ucl, lcl = xbb + A2 * Rb, xbb - A2 * Rb
    print(f"X-bar limits {lcl:.4f} to {ucl:.4f}; R chart upper limit {D4*Rb*1000:.2f} um")
    # A2 R-bar is 3 sigma of the subgroup mean
    assert abs(A2 * D2 * math.sqrt(5) - 3) < 0.01
    cp, cpk, ppm = capability(xbb, s_hat)
    print(f"Cp = {cp:.2f}, Cpk = {cpk:.2f}, expected {ppm:.0f} ppm out of tolerance")
    cp0, cpk0, ppm0 = capability(25.000, sigma)
    print(f"centred at 25.000 with sigma 4 um: Cp = Cpk = {cp0:.2f}, {ppm0:.2f} ppm")
    # simulated check of the ppm for the true process
    big = rng.normal(mu, sigma, 4_000_000)
    sim = 1e6 * np.mean((big < LSL) | (big > USL))
    print(f"true process: formula {capability(mu, sigma)[2]:.0f} ppm, simulation {sim:.0f} ppm")
    assert abs(sim - capability(mu, sigma)[2]) < 0.1 * capability(mu, sigma)[2]
    # tool wear shifts the mean by 4 um after group 25: how soon does a point fall outside?
    later = rng.normal(mu + 0.004, sigma, (20, 5)).mean(axis=1)
    first = next((i + 1 for i, x in enumerate(later) if x > ucl or x < lcl), None)
    p_out = 1 - phi((ucl - mu - 0.004) / (sigma / math.sqrt(5)))
    print(f"after a 4 um shift: first point outside at subgroup {first}; chance per subgroup {p_out:.2f}, average run length {1/p_out:.1f}")
