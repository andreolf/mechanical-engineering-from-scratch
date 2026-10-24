"""1D steady conduction with Dirichlet, Neumann and Robin conditions via ghost nodes."""
import numpy as np


def wall(n, L, k, T_in, h, T_inf, q_gen=0.0):
    """Solve k T'' + q_gen = 0 on [0, L]; T(0) = T_in, -k T'(L) = h (T(L) - T_inf)."""
    dx = L / (n - 1)
    A = np.zeros((n, n)); b = np.full(n, -q_gen * dx * dx / k)
    A[0, 0] = 1.0; b[0] = T_in                                   # Dirichlet
    for i in range(1, n - 1):
        A[i, i - 1], A[i, i], A[i, i + 1] = 1.0, -2.0, 1.0
    # ghost node T_{n} from the Robin condition: -k (T_n - T_{n-2}) / (2 dx) = h (T_{n-1} - T_inf)
    # substitute into the stencil at the last node
    A[-1, -2] = 2.0; A[-1, -1] = -2.0 - 2 * dx * h / k; b[-1] += -2 * dx * h / k * T_inf
    return np.linspace(0, L, n), np.linalg.solve(A, b)


if __name__ == "__main__":
    L, k, h = 0.2, 1.4, 25.0
    x, T = wall(11, L, k, 20.0, h, -5.0)
    q = h * (T[-1] + 5.0)
    print(f"outer surface {T[-1]:.4f} C, heat flux {q:.3f} W/m^2, Biot {h*L/k:.2f}")
    assert abs(q - 25 / (L / k + 1 / h)) < 1e-9 and abs(T[-1] - 0.46875) < 1e-9
    # Dirichlet limit: very large h pulls the surface to T_inf
    _, Td = wall(11, L, k, 20.0, 1e9, -5.0)
    assert abs(Td[-1] + 5) < 1e-5
    # Neumann limit: h = 0 is an insulated face, so the wall sits at 20 C
    _, Tn = wall(11, L, k, 20.0, 0.0, -5.0)
    assert np.allclose(Tn, 20.0)
    # with internal heat generation the profile is a parabola; ghost nodes keep second order
    qg = 5e3
    def exact(x):   # T = T_in + C1 x - qg x^2 / (2k), C1 from the Robin condition
        C1 = (h * (-5.0 - 20.0) + qg * L + h * qg * L * L / (2 * k)) / (k + h * L)
        return 20.0 + C1 * x - qg * x * x / (2 * k)
    errs = [np.max(np.abs(wall(n, L, k, 20.0, h, -5.0, qg)[1] - exact(np.linspace(0, L, n)))) for n in (11, 21, 41)]
    print("errors with heat generation:", [f"{e:.2e}" for e in errs])
    assert all(e < 1e-8 for e in errs)    # the stencil is exact for quadratics
