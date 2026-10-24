"""Virtual work on a scissor lift: P = n W cot(theta), checked against a full multi-body FBD solve."""
import math
import numpy as np


def actuator_force_vw(W, theta, n=1):
    """Platform height y = n L sin(theta); the actuator spans the base ends, x = L cos(theta).
    delta W = -W dy + P (-dx) = 0 with dy = n L cos dtheta and dx = -L sin dtheta  ->  P = n W cot(theta)."""
    return n * W / math.tan(theta)


def actuator_force_numeric(W, theta, L=1.0, n=1, h=1e-6):
    y = lambda t: n * L * math.sin(t)
    x = lambda t: L * math.cos(t)
    dy = (y(theta + h) - y(theta - h)) / (2 * h); dx = (x(theta + h) - x(theta - h)) / (2 * h)
    return -W * dy / dx                                      # work balance: P |dx| = W dy


def actuator_force_fbd(W, theta, L=1.0):
    """One-stage scissor: link A from base pin O(0,0) to top roller at (c, s); link B from base roller at (c, 0)
    to top pin (0, s); the links cross at the middle pin. Platform from (0, s) to (c, s) carries W at its middle.
    The actuator pushes the base roller end towards the pin with force P. Unknowns: Ox, Oy, By, P, Mx, My, Tx, Ty, Ry."""
    c, s = L * math.cos(theta), L * math.sin(theta)
    m = (c / 2, s / 2)
    cols, rhs = [], np.zeros(9)                              # 3 equations per body: A (0..2), B (3..5), platform (6..8)
    def col(*contribs):
        v = np.zeros(9)
        for body, (x, y), (fx, fy) in contribs:
            v[3 * body:3 * body + 3] += [fx, fy, x * fy - y * fx]
        cols.append(v)
    col((0, (0, 0), (1, 0))); col((0, (0, 0), (0, 1)))                       # base pin on link A
    col((1, (c, 0), (0, 1)))                                                 # base roller on link B
    col((1, (c, 0), (-1, 0)))                                                # actuator P on link B, pointing inward
    col((0, m, (1, 0)), (1, m, (-1, 0))); col((0, m, (0, 1)), (1, m, (0, -1)))   # middle pin
    col((1, (0, s), (1, 0)), (2, (0, s), (-1, 0))); col((1, (0, s), (0, 1)), (2, (0, s), (0, -1)))  # top pin
    col((0, (c, s), (0, 1)), (2, (c, s), (0, -1)))                           # top roller (vertical contact)
    rhs[6:9] = -np.array([0, -W, (c / 2) * (-W)])                            # the load on the platform
    x = np.linalg.solve(np.array(cols).T, rhs)
    return x[3]


if __name__ == "__main__":
    W = 4.0                       # kN on the platform
    for deg in (20, 35, 60):
        th = math.radians(deg)
        Pv, Pn, Pf = actuator_force_vw(W, th), actuator_force_numeric(W, th), actuator_force_fbd(W, th)
        print(f"theta = {deg} deg: virtual work {Pv:.4f} kN, numerical derivative {Pn:.4f}, nine-unknown FBD {Pf:.4f}")
        assert abs(Pv - Pf) < 1e-9 and abs(Pv - Pn) < 1e-6
    print(f"a 3-stage lift at 20 deg needs {actuator_force_vw(W, math.radians(20), 3):.3f} kN: low and folded is the hard case")
