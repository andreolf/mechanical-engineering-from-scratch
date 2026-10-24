"""Tool life: fit Taylor's equation V T^n = C to wear tests and find the cutting speed that minimises cost per part."""
import math
import numpy as np

N_TRUE, C_TRUE = 0.25, 400.0      # carbide on steel: exponent and speed (m/min) for a 1 minute life


def life(V, n=N_TRUE, C=C_TRUE):
    return (C / V) ** (1 / n)


def fit(V, T):
    """log V = log C - n log T."""
    slope, icpt = np.polyfit(np.log(T), np.log(V), 1)
    return -slope, math.exp(icpt)


def cost_per_part(V, n, C, Lc=180.0, D=60.0, L=200.0, f=0.25, Co=1.5, Ct=6.0, tch=2.0, tl=1.0):
    """Turning one pass: machining time from speed, tool cost shared per life.
    Co: machine and operator cost per minute, Ct: cost per cutting edge, tch: minutes to change an edge, tl: load time."""
    tm = math.pi * D * L / (1000 * V * f)          # minutes cutting (D, L in mm, V in m/min, f in mm/rev)
    T = life(V, n, C)
    return Co * tl + Co * tm + (Co * tch + Ct) * tm / T


if __name__ == "__main__":
    rng = np.random.default_rng(5)
    V = np.array([150, 200, 250, 300, 350.0])
    T = np.array([life(v) for v in V]) * np.exp(rng.normal(0, 0.05, len(V)))
    for v, t in zip(V, T):
        print(f"  {v:.0f} m/min: tool lasts {t:.1f} min")
    n, C = fit(V, T)
    print(f"fit: n = {n:.3f}, C = {C:.0f} m/min (true 0.25, 400)")
    assert abs(n - N_TRUE) < 0.03 and abs(C / C_TRUE - 1) < 0.1
    # minimum cost: T_opt = (1/n - 1)(tch + Ct/Co)
    Topt = (1 / N_TRUE - 1) * (2.0 + 6.0 / 1.5)
    Vopt = C_TRUE / Topt ** N_TRUE
    Vs = np.linspace(100, 400, 30001); cs = [cost_per_part(v, N_TRUE, C_TRUE) for v in Vs]
    Vnum = Vs[int(np.argmin(cs))]
    print(f"minimum cost: tool life {Topt:.1f} min at {Vopt:.1f} m/min (numerical {Vnum:.1f}); cost {min(cs):.3f} USD per part")
    assert abs(Vnum - Vopt) < 0.02
    Tmax = (1 / N_TRUE - 1) * 2.0
    print(f"maximum production rate: tool life {Tmax:.1f} min at {C_TRUE / Tmax ** N_TRUE:.1f} m/min")
    print(f"doubling speed from 150 to 300 m/min cuts life by {2**(1/N_TRUE):.0f}x")
