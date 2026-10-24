"""Newton's method for a node hanging from two elastic cables: residual, analytic Jacobian, quadratic convergence."""
import numpy as np

ANCHORS = np.array([[0.0, 0.0], [4.0, 0.0]])     # m
L0 = np.array([2.5, 2.0])                        # unstretched lengths, m
EA = 50e3                                        # axial stiffness of each cable, N
W = 2000.0                                       # hanging load, N


def residual(p):
    r = np.array([0.0, -W])
    for a, l0 in zip(ANCHORS, L0):
        d = a - p; L = np.linalg.norm(d)
        T = EA * (L - l0) / l0 if L > l0 else 0.0   # cables cannot push
        r += T * d / L
    return r


def jacobian(p):
    J = np.zeros((2, 2))
    for a, l0 in zip(ANCHORS, L0):
        d = a - p; L = np.linalg.norm(d); u = d / L
        if L <= l0:
            continue
        k = EA / l0; T = k * (L - l0)
        # d/dp of T u: stiffness along the cable plus geometric stiffness T/L across it
        J -= k * np.outer(u, u) + (T / L) * (np.eye(2) - np.outer(u, u))
    return J


def newton(F, J, p, tol=1e-10, maxit=20):
    hist = []
    for k in range(maxit):
        r = F(p); hist.append(np.linalg.norm(r))
        if hist[-1] < tol:
            return p, hist
        p = p - np.linalg.solve(J(p), r)
    raise RuntimeError("no convergence")


if __name__ == "__main__":
    p0 = np.array([2.0, -2.0])
    # check the analytic Jacobian against finite differences
    h = 1e-6
    Jfd = np.column_stack([(residual(p0 + h * e) - residual(p0 - h * e)) / (2 * h) for e in np.eye(2)])
    assert np.allclose(Jfd, jacobian(p0), rtol=1e-6, atol=1e-2)
    p, hist = newton(residual, jacobian, p0)
    T = [EA * (np.linalg.norm(a - p) - l0) / l0 for a, l0 in zip(ANCHORS, L0)]
    print(f"node at ({p[0]:.4f}, {p[1]:.4f}) m after {len(hist) - 1} Newton steps")
    print("residual history:", " ".join(f"{r:.1e}" for r in hist))
    print(f"tensions: left {T[0]:.1f} N, right {T[1]:.1f} N")
    assert len(hist) - 1 <= 10 and hist[-1] < 1e-10
    # vertical equilibrium check by hand: sum of vertical tension components equals W
    assert abs(sum(t * (a - p)[1] / np.linalg.norm(a - p) for t, a in zip(T, ANCHORS)) - W) < 1e-6
