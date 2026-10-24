"""Hardy Cross on a looped village water network, checked against an independent node-head solution."""
import math
import numpy as np
from scipy.optimize import fsolve

G = 9.81
# nodes: 0 1 2 on top, 3 4 5 below; water enters at 0
pipes = [(0, 1, 400, 0.20), (1, 2, 400, 0.15), (0, 3, 300, 0.20), (1, 4, 300, 0.15),
         (2, 5, 300, 0.10), (3, 4, 400, 0.15), (4, 5, 400, 0.10)]          # (from, to, length m, diameter m)
demand = np.array([-0.060, 0.010, 0.010, 0.010, 0.015, 0.015])           # m^3/s; negative = supply
loops = [[(0, +1), (3, +1), (5, -1), (2, -1)],                           # 0-1-4-3-0
         [(1, +1), (4, +1), (6, -1), (3, -1)]]                           # 1-2-5-4-1
F = 0.02
K = np.array([8 * F * L / (G * math.pi ** 2 * D ** 5) for _, _, L, D in pipes])


def hardy_cross(Q, tol=1e-12, max_iter=200):
    Q = Q.copy(); history = []
    for it in range(max_iter):
        biggest = 0.0
        for loop in loops:
            num = sum(s * K[p] * Q[p] * abs(Q[p]) for p, s in loop)
            den = sum(2 * K[p] * abs(Q[p]) for p, s in loop)
            dQ = -num / den
            for p, s in loop: Q[p] += s * dQ
            biggest = max(biggest, abs(dQ))
        history.append(biggest)
        if biggest < tol: break
    return Q, history


def node_residual(Q):
    r = demand.copy()
    for k, (a, b, _, _) in enumerate(pipes):
        r[a] += Q[k]; r[b] -= Q[k]
    return r


if __name__ == "__main__":
    Q0 = np.array([0.030, 0.012, 0.030, 0.008, 0.002, 0.020, 0.013])     # any guess that satisfies continuity
    assert np.max(np.abs(node_residual(Q0))) < 1e-15
    Q, hist = hardy_cross(Q0)
    print(f"converged in {len(hist)} sweeps; corrections {', '.join(f'{h:.1e}' for h in hist[:5])} ...")
    for k, (a, b, L, D) in enumerate(pipes):
        print(f"pipe {a}-{b}: {Q[k]*1000:8.3f} L/s, head loss {K[k]*Q[k]*abs(Q[k]):7.3f} m")
    res = node_residual(Q)
    print(f"largest continuity error at a node: {np.max(np.abs(res)):.1e} m^3/s")
    assert np.max(np.abs(res)) < 1e-15                                     # mass conserved at every node
    for loop in loops:
        assert abs(sum(s * K[p] * Q[p] * abs(Q[p]) for p, s in loop)) < 1e-9
    # independent check: unknown node heads (node 0 fixed at 50 m), flows from h = K Q|Q|
    def eqs(H):
        Hall = np.concatenate([[50.0], H]); Qn = np.array([np.sign(Hall[a] - Hall[b]) * math.sqrt(abs(Hall[a] - Hall[b]) / K[k]) for k, (a, b, _, _) in enumerate(pipes)])
        return node_residual(Qn)[1:]
    H = fsolve(eqs, np.full(5, 40.0), xtol=1e-12)
    Hall = np.concatenate([[50.0], H])
    Qn = np.array([np.sign(Hall[a] - Hall[b]) * math.sqrt(abs(Hall[a] - Hall[b]) / K[k]) for k, (a, b, _, _) in enumerate(pipes)])
    print(f"node-head solution differs by at most {np.max(np.abs(Qn - Q))*1000:.1e} L/s; lowest head {Hall.min():.3f} m at node {Hall.argmin()}")
    assert np.max(np.abs(Qn - Q)) < 1e-8
