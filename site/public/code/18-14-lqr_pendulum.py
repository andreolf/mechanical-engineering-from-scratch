"""LQR for an inverted pendulum on a cart. Linearise, check controllability, solve the continuous
algebraic Riccati equation from scratch through the stable invariant subspace of the Hamiltonian
matrix, and balance the full non-linear pendulum from a 15 degree tilt. numpy only; scipy's
solve_continuous_are is used as an optional cross-check if installed."""
import numpy as np

M, m, l, g = 1.0, 0.1, 0.5, 9.81           # cart kg, bob kg (point mass), rod length m
# state x = [cart position, cart velocity, angle from upright, angular velocity]
A = np.array([[0, 1, 0, 0],
              [0, 0, -m * g / M, 0],
              [0, 0, 0, 1],
              [0, 0, (M + m) * g / (M * l), 0]])
B = np.array([[0], [1 / M], [0], [-1 / (M * l)]])
print("open-loop eigenvalues:", np.round(np.sort(np.linalg.eigvals(A).real), 4), "(one positive: it falls)")
Cm = np.hstack([np.linalg.matrix_power(A, k) @ B for k in range(4)])
print("controllability matrix rank:", np.linalg.matrix_rank(Cm))
assert np.linalg.matrix_rank(Cm) == 4

def care(A, B, Q, R):
    """Solve A'P + PA - P B R^-1 B' P + Q = 0. The Hamiltonian H = [[A, -B R^-1 B'], [-Q, -A']] has
    eigenvalues in +- pairs; the n stable eigenvectors [X1; X2] give P = X2 X1^-1."""
    n = len(A); Ri = np.linalg.inv(R)
    H = np.block([[A, -B @ Ri @ B.T], [-Q, -A.T]])
    ev, V = np.linalg.eig(H)
    Vs = V[:, ev.real < 0]
    P = np.real(Vs[n:] @ np.linalg.inv(Vs[:n]))
    return (P + P.T) / 2

Q = np.diag([10.0, 1.0, 100.0, 1.0])       # care most about the angle, then the cart position
R = np.array([[0.1]])
P = care(A, B, Q, R)
K = np.linalg.inv(R) @ B.T @ P
res = A.T @ P + P @ A - P @ B @ np.linalg.inv(R) @ B.T @ P + Q
cl = np.linalg.eigvals(A - B @ K)
print("LQR gain K =", np.round(K.ravel(), 4))
print(f"Riccati residual {np.max(np.abs(res)):.2e}; P symmetric positive definite: {np.all(np.linalg.eigvalsh(P) > 0)}")
print("closed-loop eigenvalues:", np.round(cl, 4))
assert np.max(np.abs(res)) < 1e-8 and np.all(np.linalg.eigvalsh(P) > 0)
assert np.all(cl.real < 0)                  # every closed-loop eigenvalue has a negative real part
try:
    from scipy.linalg import solve_continuous_are
    assert np.allclose(solve_continuous_are(A, B, Q, R), P, rtol=1e-8, atol=1e-10)
    print("matches scipy.linalg.solve_continuous_are")
except ImportError:
    print("scipy not installed: skipped the optional cross-check")

def f(s, F):
    """Full non-linear cart-pendulum: theta from upright, bob at x + l sin(theta). Lagrange's equations
    (M+m) x'' + m l cos(th) th'' - m l sin(th) th'^2 = F and cos(th) x'' + l th'' = g sin(th)."""
    x, xd, th, thd = s
    st, ct = np.sin(th), np.cos(th)
    Mm = np.array([[M + m, m * l * ct], [m * l * ct, m * l * l]])
    rhs = np.array([F + m * l * thd**2 * st, m * g * l * st])
    xdd, thdd = np.linalg.solve(Mm, rhs)
    return np.array([xd, xdd, thd, thdd])

def run(K, th0, Fmax=np.inf, T=6.0, h=1e-3):
    s = np.array([0.0, 0.0, np.radians(th0), 0.0]); out = []; Fpk = 0
    for k in range(int(T / h)):
        F = float(np.clip(-K @ s, -Fmax, Fmax)); Fpk = max(Fpk, abs(F))
        k1 = f(s, F); k2 = f(s + h / 2 * k1, F); k3 = f(s + h / 2 * k2, F); k4 = f(s + h * k3, F)
        s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); out.append(s.copy())
    return np.array(out), Fpk

# the linear model must match the non-linear one for a small tilt
lin = A @ np.array([0, 0, 0.01, 0]); non = f(np.array([0, 0, 0.01, 0]), 0.0)
print(f"linear vs non-linear accelerations at a 0.01 rad tilt: {lin[[1,3]].round(5)} vs {non[[1,3]].round(5)}")
assert np.allclose(lin, non, rtol=1e-3, atol=1e-6)
tr, Fpk = run(K.ravel(), 15.0)
print(f"from 15 deg: angle after 3 s {np.degrees(tr[2999, 2]):.4f} deg, cart overshoot {tr[:, 0].min():.3f} .. {tr[:, 0].max():.3f} m, peak force {Fpk:.2f} N")
assert abs(tr[-1, 2]) < 1e-3 and abs(tr[-1, 0]) < 1e-2
# a force limit: to stop a 15 deg tilt the cart must accelerate at about g tan(15 deg)
print(f"static estimate of the force needed: (M + m) g tan 15 deg = {(M + m) * g * np.tan(np.radians(15)):.3f} N")
for Fmax in (3.0, 4.0):
    tr2, _ = run(K.ravel(), 15.0, Fmax=Fmax, T=10.0)
    ok = abs(tr2[-1, 2]) < 1e-3
    print(f"motor limited to {Fmax:.0f} N: final angle {np.degrees(tr2[-1, 2]):10.2f} deg ({'recovers' if ok else 'falls over'})")
    assert ok == (Fmax == 4.0)
