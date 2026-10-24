"""Newton's law of viscosity and Couette flow: the finite-difference velocity profile between a fixed and a moving plate."""
import numpy as np


def couette_fd(U, h, mu, dpdx=0.0, n=51):
    """Solve mu u'' = dp/dx on 0 <= y <= h with u(0) = 0, u(h) = U by central differences."""
    y = np.linspace(0, h, n); dy = y[1] - y[0]
    A = np.zeros((n, n)); b = np.full(n, dpdx / mu * dy * dy)
    A[0, 0] = A[-1, -1] = 1; b[0], b[-1] = 0.0, U
    for i in range(1, n - 1):
        A[i, i - 1], A[i, i], A[i, i + 1] = 1, -2, 1
    return y, np.linalg.solve(A, b)


def couette_exact(y, U, h, mu, dpdx=0.0):
    return U * y / h + dpdx / (2 * mu) * (y * y - h * y)


if __name__ == "__main__":
    U, h = 2.0, 1e-3
    for name, mu in (("water, 20 C", 1.0e-3), ("SAE 30 oil, 20 C", 0.29), ("honey, 20 C", 10.0)):
        tau = mu * U / h
        print(f"{name}: mu = {mu} Pa s, shear stress {tau:.1f} Pa, force on a 0.5 m^2 plate {tau*0.5:.1f} N")
    y, u = couette_fd(U, h, 0.29)
    assert np.allclose(u, U * y / h, atol=1e-12)                      # Newtonian, no pressure gradient: linear
    assert np.allclose(np.gradient(u, y), U / h)                       # constant shear rate
    y, u = couette_fd(U, h, 0.29, dpdx=-2e6)
    assert np.allclose(u, couette_exact(y, U, h, 0.29, -2e6), atol=1e-9)
    print(f"with dp/dx = -2 MPa/m the profile bulges: centre speed {u[len(u)//2]:.4f} m/s instead of {U/2:.1f}")
    print(f"flow rate per metre width: linear {U*h/2*1000:.4f} L/s, with gradient {float(np.sum((u[1:] + u[:-1]) / 2 * np.diff(y)))*1000:.4f} L/s (exact {(U*h/2 + 2e6*h**3/(12*0.29))*1000:.4f})")
