"""Kinetic theory by simulation: point molecules bouncing elastically in a box, pressure measured from momentum delivered to the walls, compared with N k T / V."""
import numpy as np

K_B = 1.380649e-23
M_N2 = 28.0134e-3 / 6.02214076e23      # kg per molecule


def simulate(N=2000, T=300.0, L=1e-7, steps=4000, seed=1):
    """Return measured pressure (Pa) and the ideal-gas value for N molecules at temperature T in a cube of side L."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, L, (N, 3))
    v = rng.normal(0, np.sqrt(K_B * T / M_N2), (N, 3))     # Maxwell-Boltzmann components
    dt = 0.02 * L / np.sqrt(K_B * T / M_N2)
    impulse = 0.0
    for _ in range(steps):
        x += v * dt
        lo, hi = x < 0, x > L
        hit = lo | hi
        impulse += 2 * M_N2 * np.abs(v[hit]).sum()
        x[lo] = -x[lo]; x[hi] = 2 * L - x[hi]; v[hit] = -v[hit]
    area_time = 6 * L * L * steps * dt
    T_kin = M_N2 * (v**2).sum() / (3 * N * K_B)
    return impulse / area_time, N * K_B * T_kin / L**3, T_kin


if __name__ == "__main__":
    for T in (200.0, 300.0, 600.0):
        p, p_ideal, Tk = simulate(T=T)
        print(f"T = {T:.0f} K (kinetic {Tk:.1f} K): simulated p = {p:.4e} Pa, NkT/V = {p_ideal:.4e} Pa, ratio {p/p_ideal:.4f}")
        assert abs(p / p_ideal - 1) < 0.02
    v_rms = np.sqrt(3 * K_B * 300 / M_N2)
    print(f"rms speed of N2 at 300 K: {v_rms:.0f} m/s")
