"""Lagrangian mechanics: derive the double pendulum's equations with SymPy, then simulate them."""
import math
import numpy as np
import sympy as sp


def derive():
    t = sp.symbols("t")
    m1, m2, l1, l2, g = sp.symbols("m1 m2 l1 l2 g", positive=True)
    th1, th2 = sp.Function("th1")(t), sp.Function("th2")(t)
    x1, y1 = l1 * sp.sin(th1), -l1 * sp.cos(th1)
    x2, y2 = x1 + l2 * sp.sin(th2), y1 - l2 * sp.cos(th2)
    T = m1 / 2 * (sp.diff(x1, t)**2 + sp.diff(y1, t)**2) + m2 / 2 * (sp.diff(x2, t)**2 + sp.diff(y2, t)**2)
    V = m1 * g * y1 + m2 * g * y2
    L = sp.simplify(T - V)
    eqs = [sp.diff(sp.diff(L, sp.diff(q, t)), t) - sp.diff(L, q) for q in (th1, th2)]
    a1, a2 = sp.symbols("a1 a2"); w1, w2, q1, q2 = sp.symbols("w1 w2 q1 q2")
    sub = {sp.diff(th1, t, 2): a1, sp.diff(th2, t, 2): a2, sp.diff(th1, t): w1, sp.diff(th2, t): w2}
    eqs = [e.subs(sub).subs({th1: q1, th2: q2}) for e in eqs]
    sol = sp.solve(eqs, [a1, a2], dict=True)[0]
    energy = (T + V).subs(sub).subs({th1: q1, th2: q2})
    args = (q1, q2, w1, w2, m1, m2, l1, l2, g)
    return sp.lambdify(args, [sol[a1], sol[a2]], "math"), sp.lambdify(args, energy, "math")


def simulate(acc, s0, p, t_end, dt):
    def f(s):
        a = acc(*s, *p); return np.array([s[2], s[3], a[0], a[1]])
    s = np.array(s0, float); out = [s.copy()]
    for _ in range(int(round(t_end / dt))):
        k1 = f(s); k2 = f(s + dt/2*k1); k3 = f(s + dt/2*k2); k4 = f(s + dt*k3)
        s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4); out.append(s.copy())
    return np.array(out)


if __name__ == "__main__":
    acc, energy = derive()
    p = (1.0, 1.0, 1.0, 1.0, 9.81)                        # m1, m2, l1, l2, g
    # small swings: the linearised normal-mode frequencies for equal masses and lengths are sqrt((2 -+ sqrt 2) g / l)
    s0 = [0.01, 0.01 * math.sqrt(2), 0, 0]                  # in-phase mode shape
    tr = simulate(acc, s0, p, 10.0, 1e-3)
    zc = np.where(np.diff(np.sign(tr[:, 0])) != 0)[0]
    period = 2 * np.mean(np.diff(zc)) * 1e-3
    w_mode = math.sqrt((2 - math.sqrt(2)) * 9.81)
    print(f"in-phase mode: simulated period {period:.4f} s, theory {2 * math.pi / w_mode:.4f} s")
    assert abs(period - 2 * math.pi / w_mode) < 2e-3
    # large swings: chaos, but energy must be conserved
    for dt in (1e-2, 1e-3):
        tr = simulate(acc, [2.0, 2.5, 0, 0], p, 20.0, dt)
        E = np.array([energy(*s, *p) for s in tr])
        print(f"chaotic swing, dt = {dt}: relative energy drift {np.max(np.abs(E - E[0])) / abs(E[0]):.1e}")
    assert np.max(np.abs(E - E[0])) / abs(E[0]) < 1e-6
    # sensitivity: two starts differing by 1e-9 rad separate completely
    a = simulate(acc, [2.0, 2.5, 0, 0], p, 20.0, 1e-3); b = simulate(acc, [2.0 + 1e-9, 2.5, 0, 0], p, 20.0, 1e-3)
    sep = np.abs(a[:, 1] - b[:, 1])
    i = int(np.argmax(sep > 0.1))
    print(f"a 1e-9 rad difference grows past 0.1 rad after {i * 1e-3:.2f} s")
