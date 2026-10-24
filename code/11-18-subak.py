"""Weirs from critical flow, and a cascade of Balinese rice terraces (subak) each spilling over a weir into the next."""
import math
import numpy as np

G = 9.81


def broad_crested(b, H, Cd=1.0):
    """Critical depth forms on the crest: Q = Cd b (2/3)^(3/2) sqrt(g) H^(3/2)."""
    return Cd * b * (2 / 3) ** 1.5 * math.sqrt(G) * max(H, 0.0) ** 1.5


def sharp_crested(b, H, Cd=0.62):
    """Integrating sqrt(2 g h) over the nappe: Q = Cd (2/3) sqrt(2 g) b H^(3/2)."""
    return Cd * 2 / 3 * math.sqrt(2 * G) * b * max(H, 0.0) ** 1.5


def cascade(n, area, crest, b, inflow, t_end, dt=1.0):
    """Water depth in n terraces in series. Each holds water up to its weir crest, then spills over a broad-crested
    notch of width b into the next. Returns times and depths (explicit Euler, small step)."""
    h = np.zeros(n); out_hist, h_hist, ts = [], [], []
    for k in range(int(t_end / dt)):
        Qin = inflow
        dh = np.zeros(n)
        for i in range(n):
            Qout = broad_crested(b, h[i] - crest)
            dh[i] = (Qin - Qout) / area
            Qin = Qout
        h += dh * dt
        if k % 60 == 0:
            ts.append(k * dt); h_hist.append(h.copy()); out_hist.append(Qin)
    return np.array(ts), np.array(h_hist), np.array(out_hist)


if __name__ == "__main__":
    Hs = np.array([0.02, 0.05, 0.1, 0.2])
    Q = np.array([broad_crested(0.3, H) for H in Hs])
    slope = np.polyfit(np.log(Hs), np.log(Q), 1)[0]
    print("broad-crested notch 0.3 m wide: " + ", ".join(f"H {H*100:.0f} cm -> {q*1000:.2f} L/s" for H, q in zip(Hs, Q)))
    print(f"log-log slope {slope:.6f}")
    assert abs(slope - 1.5) < 1e-9                                        # discharge scales with head^(3/2)
    print(f"sharp-crested, same width, 10 cm head: {sharp_crested(0.3, 0.1)*1000:.2f} L/s")
    # five terraces of 400 m^2, water held 5 cm deep before spilling, 0.3 m notches, 10 L/s from the canal
    ts, h, out = cascade(5, 400.0, 0.05, 0.3, 0.010, 12 * 3600)
    Hss = (0.010 / (0.3 * (2 / 3) ** 1.5 * math.sqrt(G))) ** (2 / 3)
    print(f"steady head over each notch {Hss*100:.3f} cm; after 12 h the depths are {np.round(h[-1]*100, 2)} cm and the outflow {out[-1]*1000:.3f} L/s")
    first = [ts[np.argmax(h[:, i] > 0.05)] / 3600 for i in range(5)]
    print("terrace starts spilling after (h): " + ", ".join(f"{x:.2f}" for x in first))
    assert abs(out[-1] - 0.010) < 1e-4                                    # mass balance: outflow returns to inflow
