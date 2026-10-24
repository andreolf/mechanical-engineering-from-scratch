"""The material derivative Du/Dt = du/dt + (u . grad) u, computed by finite differences and checked two ways."""
import numpy as np

A, B = 0.5, 0.2      # stagnation-point flow whose strength grows in time: u = a(t) x, v = -a(t) y with a = A (1 + B t)


def field(x, y, t):
    a = A * (1 + B * t)
    return np.array([a * x, -a * y])


def material_acc(f, x, y, t, h=1e-5):
    """Local plus convective acceleration from central differences."""
    dudt = (f(x, y, t + h) - f(x, y, t - h)) / (2 * h)
    dudx = (f(x + h, y, t) - f(x - h, y, t)) / (2 * h)
    dudy = (f(x, y + h, t) - f(x, y - h, t)) / (2 * h)
    u, v = f(x, y, t)
    return dudt, u * dudx + v * dudy


def exact_acc(x, y, t):
    a, adot = A * (1 + B * t), A * B
    return np.array([adot * x + a * a * x, -adot * y + a * a * y])


if __name__ == "__main__":
    x, y, t = 2.0, 1.0, 3.0
    local, conv = material_acc(field, x, y, t)
    total = local + conv
    print(f"at ({x}, {y}), t = {t}: local {local.round(6)}, convective {conv.round(6)}, total {total.round(6)}")
    print(f"exact: {exact_acc(x, y, t).round(6)}")
    assert np.allclose(total, exact_acc(x, y, t), atol=1e-7)
    # second check: follow the particle and differentiate its velocity along the path
    dt = 1e-4; vels = []
    for k in range(-2, 3):
        # exact particle path for this field: x(t) = x0 exp(int a dt)
        tt = t + k * dt; I = A * ((tt - t) + B * (tt * tt - t * t) / 2)
        p = np.array([x * np.exp(I), y * np.exp(-I)])
        vels.append(field(*p, tt))
    acc_path = (-vels[4] + 8 * vels[3] - 8 * vels[1] + vels[0]) / (12 * dt)
    print(f"following the particle: {acc_path.round(6)}")
    assert np.allclose(acc_path, total, atol=1e-6)
    # steady flow still accelerates: at t = 0 with B = 0 the local part vanishes but the convective part does not
    print(f"steady version at (2, 1): convective acceleration {np.array([A*A*2, A*A*1])} m/s^2 even though nothing changes in time")
