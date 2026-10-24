"""A Newton-based 2D sketch solver: geometric constraints as equations, minimum-norm Newton steps (so a dragged sketch moves as little as possible), and degrees of freedom from the Jacobian rank."""
import numpy as np


def residuals(x, cons):
    P = x.reshape(-1, 2); r = []
    for c in cons:
        k = c[0]
        if k == "fix":       _, i, (px, py) = c; r += [P[i, 0] - px, P[i, 1] - py]
        elif k == "dist":    _, i, j, d = c; r.append(np.sum((P[j] - P[i]) ** 2) - d * d)
        elif k == "horiz":   _, i, j = c; r.append(P[j, 1] - P[i, 1])
        elif k == "vert":    _, i, j = c; r.append(P[j, 0] - P[i, 0])
        elif k == "perp":    _, i, j, k2, l = c; r.append((P[j] - P[i]) @ (P[l] - P[k2]))
        elif k == "parallel":
            _, i, j, k2, l = c; a, b = P[j] - P[i], P[l] - P[k2]; r.append(a[0] * b[1] - a[1] * b[0])
        elif k == "angle":   # angle of segment ij from horizontal, in degrees
            _, i, j, deg = c; d = P[j] - P[i]; t = np.radians(deg); r.append(d[0] * np.sin(t) - d[1] * np.cos(t))
    return np.array(r)


def jacobian(x, cons, h=1e-7):
    r0 = residuals(x, cons); J = np.zeros((len(r0), len(x)))
    for k in range(len(x)):
        e = np.zeros(len(x)); e[k] = h
        J[:, k] = (residuals(x + e, cons) - residuals(x - e, cons)) / (2 * h)
    return J


def solve(x, cons, tol=1e-12, iters=50):
    """Newton with the minimum-norm step dx = -J^T (J J^T)^+ r: under-constrained sketches change as little as possible."""
    x = np.array(x, float)
    for it in range(iters):
        r = residuals(x, cons)
        if np.abs(r).max() < tol: return x, it
        J = jacobian(x, cons)
        x = x - np.linalg.pinv(J) @ r
    raise RuntimeError("did not converge")


def dof(x, cons):
    J = jacobian(x, cons)
    return len(x) - np.linalg.matrix_rank(J, tol=1e-6)


if __name__ == "__main__":
    # a rectangular plate outline, 80 x 50 mm, corner 0 fixed at the origin
    w, h = 80.0, 50.0
    cons = [("fix", 0, (0, 0)), ("dist", 0, 1, w), ("dist", 1, 2, h), ("perp", 0, 1, 1, 2), ("perp", 1, 2, 2, 3), ("perp", 2, 3, 3, 0)]
    x0 = np.array([0, 0, 70, 10, 75, 60, -5, 45], float)            # a rough sketch
    x, it = solve(x0, cons)
    print(f"solved in {it} Newton steps; residual {np.abs(residuals(x, cons)).max():.1e}; DOF left {dof(x, cons)} (rotation about the fixed corner)")
    assert dof(x, cons) == 1
    cons.append(("horiz", 0, 1))
    x, it = solve(x, cons)
    print(f"with P0P1 horizontal: {np.round(x.reshape(-1, 2), 9).tolist()}, DOF {dof(x, cons)}")
    assert dof(x, cons) == 0 and np.allclose(x.reshape(-1, 2), [[0, 0], [80, 0], [80, 50], [0, 50]], atol=1e-9)
    # a redundant constraint (opposite side length) does not remove a DOF: the rank stays 8
    print(f"adding |P2P3| = 80 (redundant): DOF still {dof(x, cons + [('dist', 2, 3, w)])}, rank {np.linalg.matrix_rank(jacobian(x, cons + [('dist', 2, 3, w)]), tol=1e-6)} of {len(residuals(x, cons)) + 1} equations")
    # drag: an under-constrained bracket (no horizontal constraint, but corner 0 fixed). The user drags corner 2 to (40, 90).
    cons_u = cons[:-1]
    x_rect = np.array([0, 0, 80, 0, 80, 50, 0, 50], float)
    xd = x_rect.copy(); xd[4:6] = (40, 90)
    xs, it = solve(xd, cons_u)
    P = xs.reshape(-1, 2)
    ang = np.degrees(np.arctan2(P[1, 1], P[1, 0]))
    print(f"drag corner 2 to (40, 90): solved in {it} steps, residual {np.abs(residuals(xs, cons_u)).max():.1e}; plate rotated {ang:.4f} deg; corner 2 at {P[2].round(4)}")
    assert np.abs(residuals(xs, cons_u)).max() < 1e-9
    assert abs(np.linalg.norm(P[1] - P[0]) - w) < 1e-9 and abs(np.linalg.norm(P[2] - P[1]) - h) < 1e-9
    # whatever the drag, the solved shape is still an 80 x 50 rectangle: the diagonal is fixed
    diag = np.hypot(w, h)
    print(f"|P0P2| = {np.linalg.norm(P[2]):.9f} = sqrt(80^2 + 50^2) = {diag:.9f}")
    assert abs(np.linalg.norm(P[2]) - diag) < 1e-9
