"""Euler's equations for torque-free rotation: the intermediate-axis (tennis racket) instability."""
import numpy as np


def euler_rhs(w, I):
    I1, I2, I3 = I
    w1, w2, w3 = w
    return np.array([(I2 - I3) * w2 * w3 / I1, (I3 - I1) * w3 * w1 / I2, (I1 - I2) * w1 * w2 / I3])


def spin(w0, I, t_end, dt=1e-3):
    w = np.array(w0, float); out = [w.copy()]
    for _ in range(int(round(t_end / dt))):
        k1 = euler_rhs(w, I); k2 = euler_rhs(w + dt/2*k1, I); k3 = euler_rhs(w + dt/2*k2, I); k4 = euler_rhs(w + dt*k3, I)
        w = w + dt/6*(k1 + 2*k2 + 2*k3 + k4); out.append(w.copy())
    return np.array(out)


if __name__ == "__main__":
    # a phone (or tennis racket): I1 < I2 < I3 about its principal axes (kg m^2, phone-like proportions)
    I = np.array([1.0, 2.5, 3.3]) * 1e-4
    eps = 1e-3
    for k, name in enumerate(("smallest", "intermediate", "largest")):
        w0 = np.full(3, eps); w0[k] = 10.0             # 10 rad/s about one axis plus a tiny wobble
        tr = spin(w0, I, 10.0)
        others = np.delete(tr, k, axis=1)
        growth = np.max(np.abs(others)) / eps
        flips = np.sum(np.diff(np.sign(tr[:, k])) != 0)
        T = 0.5 * np.sum(I * tr**2, axis=1); H = np.linalg.norm(I * tr, axis=1)
        print(f"spin about the {name:12s} axis: wobble grows x{growth:9.1f}, main spin changes sign {flips} times; energy drift {abs(T[-1]/T[0]-1):.1e}, |H| drift {abs(H[-1]/H[0]-1):.1e}")
        assert abs(T[-1] / T[0] - 1) < 1e-9 and abs(H[-1] / H[0] - 1) < 1e-9
        if k == 1:
            assert growth > 1000 and flips >= 2
        else:
            assert growth < 10
    # linearised growth rate about axis 2: lambda = w2 sqrt((I2 - I1)(I3 - I2) / (I1 I3))
    lam = 10.0 * np.sqrt((I[1] - I[0]) * (I[2] - I[1]) / (I[0] * I[2]))
    print(f"linear theory: the wobble about the intermediate axis grows like exp({lam:.3f} t), doubling every {np.log(2)/lam:.3f} s")
