"""Four-bar linkage: position and velocity analysis, and Grashof's rule for which link can turn fully."""
import math
import numpy as np


def positions(a, b, c, d, th2, branch=+1):
    """Ground pivots O2 = (0, 0), O4 = (d, 0). Crank a at angle th2, coupler b, rocker c.
    Returns joint A, joint B, or None if the loop can't close at this crank angle."""
    A = np.array([a * math.cos(th2), a * math.sin(th2)])
    O4 = np.array([d, 0.0])
    e = O4 - A; L = np.linalg.norm(e)
    if L > b + c or L < abs(b - c):
        return None
    # circle intersection: B is b from A and c from O4
    x = (b * b - c * c + L * L) / (2 * L); h = math.sqrt(max(b * b - x * x, 0))
    u = e / L; n = np.array([-u[1], u[0]])
    return A, A + x * u + branch * h * n


def velocities(a, b, c, d, th2, w2, branch=+1):
    """v_B = v_A + w3 x r_AB and v_B = w4 x r_O4B; solve the 2 x 2 system for w3, w4."""
    A, B = positions(a, b, c, d, th2, branch)
    rAB, rO4B = B - A, B - np.array([d, 0.0])
    vA = w2 * np.array([-A[1], A[0]])
    # w3 * perp(rAB) - w4 * perp(rO4B) = -vA
    M = np.array([[-rAB[1], rO4B[1]], [rAB[0], -rO4B[0]]])
    w3, w4 = np.linalg.solve(M, -vA)
    return w3, w4, vA, w4 * np.array([-rO4B[1], rO4B[0]])


def grashof(links):
    s, *_, l = sorted(links)
    p, q = sorted(links)[1:3]
    return s + l <= p + q


def crank_turns_fully(a, b, c, d, n=3600):
    return all(positions(a, b, c, d, t) is not None for t in np.linspace(0, 2 * math.pi, n, endpoint=False))


if __name__ == "__main__":
    # a windscreen-wiper style linkage: crank 20, coupler 70, rocker 45, ground 70 (mm)
    a, b, c, d = 20.0, 70.0, 45.0, 70.0
    print(f"links {a, b, c, d}: Grashof {grashof([a, b, c, d])}, crank turns fully {crank_turns_fully(a, b, c, d)}")
    th2, w2 = math.radians(60), 2 * math.pi * 1.0               # 60 rpm motor
    w3, w4, vA, vB = velocities(a, b, c, d, th2, w2)
    A, B = positions(a, b, c, d, th2)
    print(f"at 60 deg: A = {A.round(3)}, B = {B.round(3)}; w3 = {w3:.4f}, w4 = {w4:.4f} rad/s; |vA| = {np.linalg.norm(vA):.3f}, |vB| = {np.linalg.norm(vB):.3f} mm/s")
    # check by finite differences of the rocker angle
    h = 1e-6
    ang = lambda t: math.atan2(*(positions(a, b, c, d, t)[1] - np.array([d, 0]))[::-1])
    w4_fd = (ang(th2 + h) - ang(th2 - h)) / (2 * h) * w2
    print(f"finite-difference rocker speed {w4_fd:.4f} rad/s")
    assert abs(w4_fd - w4) < 1e-5
    # rocker swing over a full crank turn
    ts = np.linspace(0, 2 * math.pi, 3601)
    angs = np.unwrap([ang(t) for t in ts])
    print(f"rocker swings between {math.degrees(angs.min()):.1f} and {math.degrees(angs.max()):.1f} deg ({math.degrees(angs.max() - angs.min()):.1f} deg)")
    # Grashof predicts full rotation in random linkages (shortest link as the crank)
    rng = np.random.default_rng(7); agree = 0; N = 400
    for _ in range(N):
        L = rng.uniform(10, 100, 4)
        s = L.min(); others = list(L); others.remove(s)
        rng.shuffle(others)
        a2, b2, c2, d2 = s, *others
        agree += grashof(L) == crank_turns_fully(a2, b2, c2, d2, 720)
    print(f"Grashof's rule matched the simulation in {agree} of {N} random linkages (shortest link as crank)")
    assert agree == N
