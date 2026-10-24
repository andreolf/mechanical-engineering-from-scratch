"""A slider-crank as a multibody system: bodies, constraint equations and Lagrange multipliers, with Baumgarte stabilisation."""
import math
import numpy as np

# bodies: 1 crank (pinned to ground at the origin), 2 connecting rod, 3 piston (slides on the x axis)
r, l = 0.05, 0.15                      # crank radius and rod length (m)
m = np.array([2.0, 1.0, 0.5])          # masses (kg)
J = np.array([2.0 * r**2 / 3, 1.0 * l**2 / 12, 0.0])   # crank as a uniform bar about its centre, rod about its centre
# coordinates q = (x1, y1, th1, x2, y2, th2, x3, y3, th3); body centres at the middle of crank and rod


def constraints(q):
    x1, y1, t1, x2, y2, t2, x3, y3, t3 = q
    A = np.array([x1 - r / 2 * math.cos(t1), y1 - r / 2 * math.sin(t1)])          # crank end at the ground pin
    Bc = np.array([x1 + r / 2 * math.cos(t1), y1 + r / 2 * math.sin(t1)])          # crank pin
    Br = np.array([x2 - l / 2 * math.cos(t2), y2 - l / 2 * math.sin(t2)])          # rod big end
    Cr = np.array([x2 + l / 2 * math.cos(t2), y2 + l / 2 * math.sin(t2)])          # rod small end
    return np.r_[A, Bc - Br, Cr - np.array([x3, y3]), y3, t3]                      # 8 equations, 9 coordinates: 1 DOF


def jacobian(q):
    """Analytic constraint Jacobian dC/dq (8 x 9)."""
    t1, t2 = q[2], q[5]
    s1, c1, s2, c2 = math.sin(t1), math.cos(t1), math.sin(t2), math.cos(t2)
    Cq = np.zeros((8, 9))
    Cq[0, [0, 2]] = [1, r / 2 * s1]
    Cq[1, [1, 2]] = [1, -r / 2 * c1]
    Cq[2, [0, 2, 3, 5]] = [1, -r / 2 * s1, -1, -l / 2 * s2]
    Cq[3, [1, 2, 4, 5]] = [1, r / 2 * c1, -1, l / 2 * c2]
    Cq[4, [3, 5, 6]] = [1, -l / 2 * s2, -1]
    Cq[5, [4, 5, 7]] = [1, l / 2 * c2, -1]
    Cq[6, 7] = 1; Cq[7, 8] = 1
    return Cq


def gamma(q, qd):
    """Right-hand side -(dCq/dt) qd: the velocity-squared terms of the constraint accelerations."""
    t1, t2, w1, w2 = q[2], q[5], qd[2], qd[5]
    s1, c1, s2, c2 = math.sin(t1), math.cos(t1), math.sin(t2), math.cos(t2)
    return np.array([-r / 2 * c1 * w1**2, -r / 2 * s1 * w1**2,
                     r / 2 * c1 * w1**2 + l / 2 * c2 * w2**2, r / 2 * s1 * w1**2 + l / 2 * s2 * w2**2,
                     l / 2 * c2 * w2**2, l / 2 * s2 * w2**2, 0.0, 0.0])


def initial(th1, w1):
    """Consistent positions and velocities for a crank angle and speed."""
    B = r * np.array([math.cos(th1), math.sin(th1)])
    t2 = -math.asin(B[1] / l)
    C = B + l * np.array([math.cos(t2), math.sin(t2)])
    q = np.array([B[0] / 2, B[1] / 2, th1, (B[0] + C[0]) / 2, (B[1] + C[1]) / 2, t2, C[0], 0.0, 0.0])
    # velocities: solve Cq qd = 0 with crank speed fixed
    Cq = jacobian(q)
    A = np.vstack([Cq, np.eye(9)[2]]); b = np.r_[np.zeros(8), w1]
    return q, np.linalg.solve(A, b)


def simulate(t_end, dt, alpha=0.0, beta=0.0, torque=0.0):
    M = np.diag([m[0], m[0], J[0], m[1], m[1], J[1], m[2], m[2], 1.0])
    q, qd = initial(0.3, 2 * math.pi * 10)                  # 600 rpm
    Q = np.zeros(9); Q[2] = torque
    drift = []
    def acc(q, qd):
        Cq = jacobian(q); C = constraints(q)
        rhs = gamma(q, qd) - 2 * alpha * (Cq @ qd) - beta**2 * C
        K = np.block([[M, Cq.T], [Cq, np.zeros((8, 8))]])
        sol = np.linalg.solve(K, np.r_[Q, rhs])
        return sol[:9], sol[9:]
    for _ in range(int(round(t_end / dt))):
        def f(s):
            a, _ = acc(s[:9], s[9:]); return np.r_[s[9:], a]
        s = np.r_[q, qd]
        k1 = f(s); k2 = f(s + dt/2*k1); k3 = f(s + dt/2*k2); k4 = f(s + dt*k3)
        s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4); q, qd = s[:9], s[9:]
        drift.append(np.max(np.abs(constraints(q))))
    T = 0.5 * qd @ M @ qd
    return q, qd, np.array(drift), T


if __name__ == "__main__":
    # check the analytic Jacobian against finite differences
    qa, _ = initial(0.7, 1.0); h = 1e-6
    Jfd = np.column_stack([(constraints(qa + h * e) - constraints(qa - h * e)) / (2 * h) for e in np.eye(9)])
    assert np.max(np.abs(Jfd - jacobian(qa))) < 1e-9
    q0, qd0 = initial(0.3, 2 * math.pi * 10)
    M = np.diag([m[0], m[0], J[0], m[1], m[1], J[1], m[2], m[2], 1.0])
    T0 = 0.5 * qd0 @ M @ qd0
    print(f"start: crank 0.3 rad at 600 rpm, piston at x = {q0[6]*1000:.3f} mm, kinetic energy {T0:.4f} J")
    for alpha, beta, name in ((0.0, 0.0, "no stabilisation"), (20.0, 20.0, "Baumgarte (alpha = beta = 20)")):
        q, qd, drift, T = simulate(0.5, 5e-4, alpha, beta)
        print(f"{name:30s}: worst constraint violation {drift.max():.1e} m, final {drift[-1]:.1e}; energy change {abs(T / T0 - 1):.1e}")
    assert drift.max() < 1e-8
    # the free mechanism (no torque, no gravity) keeps its kinetic energy, so it speeds up and slows down as the
    # effective inertia changes with crank angle: crank speed is not constant even with no load
    q, qd, _, _ = simulate(0.05, 5e-4, 20.0, 20.0)
    print(f"after 0.05 s: crank angle {q[2]:.4f} rad, crank speed {qd[2]:.3f} rad/s (started at {2 * math.pi * 10:.3f})")
