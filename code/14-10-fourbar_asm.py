"""Assemblies and mates: a four-bar linkage as bodies (x, y, theta) joined by revolute mates. Count DOF from the constraint Jacobian, solve positions, and check against Freudenstein's closed form."""
import math
import numpy as np

# link lengths (mm): ground a, crank b, coupler c, rocker d
A_, B_, C_, D_ = 100.0, 40.0, 120.0, 80.0
O2, O4 = np.array([0.0, 0.0]), np.array([A_, 0.0])


def body_point(q, k, local):
    """World position of a point given in body k's local frame. q holds (x, y, theta) for bodies 1..3 (crank, coupler, rocker)."""
    x, y, t = q[3 * k: 3 * k + 3]
    c, s = math.cos(t), math.sin(t)
    return np.array([x + c * local[0] - s * local[1], y + s * local[0] + c * local[1]])


def mates(q, crank_angle=None):
    """Each body is a bar along its local x axis from (0, 0) to (length, 0). Revolute mate = two equations (points coincide)."""
    r = []
    r += list(body_point(q, 0, (0, 0)) - O2)                           # crank pinned to ground at O2
    r += list(body_point(q, 0, (B_, 0)) - body_point(q, 1, (0, 0)))   # crank-coupler pin
    r += list(body_point(q, 1, (C_, 0)) - body_point(q, 2, (D_, 0)))  # coupler-rocker pin (rocker tip)
    r += list(body_point(q, 2, (0, 0)) - O4)                           # rocker pinned to ground at O4
    if crank_angle is not None:
        r.append(q[2] - crank_angle)                                   # a motor drive on the crank
    return np.array(r)


def jac(q, crank_angle=None, h=1e-7):
    r0 = mates(q, crank_angle); J = np.zeros((len(r0), 9))
    for k in range(9):
        e = np.zeros(9); e[k] = h
        J[:, k] = (mates(q + e, crank_angle) - mates(q - e, crank_angle)) / (2 * h)
    return J


def solve(q, crank_angle):
    for _ in range(50):
        r = mates(q, crank_angle)
        if np.abs(r).max() < 1e-12: return q
        q = q - np.linalg.lstsq(jac(q, crank_angle), r, rcond=None)[0]
    raise RuntimeError("assembly failed")


def freudenstein(theta2):
    """Rocker angle theta4 for the open configuration, from K1 cos t4 - K2 cos t2 + K3 = cos(t2 - t4)."""
    K1, K2, K3 = A_ / B_, A_ / D_, (B_ ** 2 - C_ ** 2 + D_ ** 2 + A_ ** 2) / (2 * B_ * D_)
    Aq = math.cos(theta2) - K1 - K2 * math.cos(theta2) + K3
    Bq = -2 * math.sin(theta2)
    Cq = K1 - (K2 + 1) * math.cos(theta2) + K3
    return 2 * math.atan2(-Bq - math.sqrt(Bq * Bq - 4 * Aq * Cq), 2 * Aq)


if __name__ == "__main__":
    s, l = min(A_, B_, C_, D_), max(A_, B_, C_, D_)
    pq = A_ + B_ + C_ + D_ - s - l
    print(f"Grashof: s + l = {s + l} <= p + q = {pq}: {s + l <= pq}; the shortest link is the crank, so the crank turns fully")
    assert s + l <= pq and s == B_
    # Grubler: 3 moving bodies, 4 revolute joints -> 3*3 - 2*4 = 1
    print(f"Grubler: M = 3 (n - 1) - 2 j = 3*3 - 2*4 = {3*3 - 2*4}")
    # assemble from a rough guess at crank angle 60 deg
    q = np.array([0, 0, 1.0, 20, 35, 0.3, 100, 0, 1.8])
    q = solve(q, math.radians(60))
    rank_free = np.linalg.matrix_rank(jac(q)[:, :], tol=1e-6)
    print(f"mates only: 8 equations, rank {rank_free} -> DOF {9 - rank_free}; with the crank drive: DOF {9 - np.linalg.matrix_rank(jac(q, math.radians(60)), tol=1e-6)}")
    assert 9 - rank_free == 1 and 9 - np.linalg.matrix_rank(jac(q, math.radians(60)), tol=1e-6) == 0
    # sweep the crank once around, continuing from the previous solution, and compare with Freudenstein
    worst, out = 0.0, []
    for deg in range(0, 361, 5):
        q = solve(q, math.radians(deg))
        t4 = q[8] % (2 * math.pi)                                          # the rocker body runs from O4 to its tip
        t4f = freudenstein(math.radians(deg)) % (2 * math.pi)
        worst = max(worst, abs((t4 - t4f + math.pi) % (2 * math.pi) - math.pi))
        out.append(math.degrees(t4))
    print(f"rocker angle over a full crank turn: {min(out):.3f} to {max(out):.3f} deg (swing {max(out)-min(out):.3f}); worst gap to Freudenstein {worst:.1e} rad")
    assert worst < 1e-9
    # every pin stays assembled: link lengths are preserved
    P_b = body_point(q, 0, (B_, 0)); P_c = body_point(q, 1, (C_, 0))
    assert abs(np.linalg.norm(P_c - P_b) - C_) < 1e-9 and abs(np.linalg.norm(P_c - O4) - D_) < 1e-9
