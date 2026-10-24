"""Integrating orientation from angular velocity: rotation matrices, Euler angles and quaternions."""
import math
import numpy as np


def qmul(a, b):
    w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
    return np.array([w1*w2 - x1*x2 - y1*y2 - z1*z2, w1*x2 + x1*w2 + y1*z2 - z1*y2,
                     w1*y2 - x1*z2 + y1*w2 + z1*x2, w1*z2 + x1*y2 - y1*x2 + z1*w2])


def qrot(q):
    w, x, y, z = q
    return np.array([[1 - 2*(y*y + z*z), 2*(x*y - w*z), 2*(x*z + w*y)],
                     [2*(x*y + w*z), 1 - 2*(x*x + z*z), 2*(y*z - w*x)],
                     [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x*x + y*y)]])


def axis_angle(axis, ang):
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    return np.r_[math.cos(ang / 2), math.sin(ang / 2) * axis]


def integrate(omega_body, t_end, dt, renorm=True):
    """q' = q * (0, w) / 2 with w in body axes, RK4."""
    q = np.array([1.0, 0, 0, 0]); t = 0.0; norms = []
    f = lambda t, q: 0.5 * qmul(q, np.r_[0.0, omega_body(t)])
    while t < t_end - 1e-12:
        k1 = f(t, q); k2 = f(t + dt/2, q + dt/2*k1); k3 = f(t + dt/2, q + dt/2*k2); k4 = f(t + dt, q + dt*k3)
        q = q + dt/6*(k1 + 2*k2 + 2*k3 + k4); t += dt
        if renorm: q = q / np.linalg.norm(q)
        norms.append(np.linalg.norm(q))
    return q, np.array(norms)


def euler_zyx_rates(phi, theta, w):
    """Roll-pitch-yaw angle rates from body rates: singular when cos(theta) = 0 (gimbal lock)."""
    p, q, r = w
    c, s, t = math.cos(phi), math.sin(phi), math.tan(theta)
    return np.array([p + (q * s + r * c) * t, q * c - r * s, (q * s + r * c) / math.cos(theta)])


if __name__ == "__main__":
    np.set_printoptions(suppress=True)
    # 1. constant spin about a fixed axis: the integrated quaternion must equal the exact axis-angle rotation
    axis = np.array([1.0, 2.0, 2.0]) / 3.0; rate = 1.5
    q, norms = integrate(lambda t: rate * axis, 4.0, 1e-3)
    q_exact = axis_angle(axis, rate * 4.0)
    print(f"constant spin: |q - exact| = {np.linalg.norm(q - q_exact):.2e}, |q| = {np.linalg.norm(q):.15f}")
    assert np.linalg.norm(q - q_exact) < 1e-9
    # 2. a tumbling body: renormalising keeps |q| = 1; without it the norm drifts slowly
    wt = lambda t: np.array([1.0 + 0.5 * math.sin(2 * t), 0.7 * math.cos(3 * t), 0.4])
    q1, n1 = integrate(wt, 200.0, 0.05, renorm=True)
    q2, n2 = integrate(wt, 200.0, 0.05, renorm=False)
    print(f"tumbling for 200 s at dt = 0.05: norm error with renormalisation {np.max(np.abs(n1 - 1)):.1e}, without {abs(n2[-1] - 1):.1e}")
    assert np.max(np.abs(n1 - 1)) < 1e-14
    R = qrot(q1)
    print(f"rotation matrix stays orthogonal: |R^T R - I| = {np.linalg.norm(R.T @ R - np.eye(3)):.1e}, det = {np.linalg.det(R):.12f}")
    # 3. gimbal lock: Euler-angle rates blow up as pitch approaches 90 degrees, quaternions don't care
    for th in (0, 60, 85, 89, 89.9):
        rates = euler_zyx_rates(0.3, math.radians(th), np.array([0.0, 0.0, 1.0]))
        print(f"  pitch {th:5.1f} deg: Euler angle rates {np.round(rates, 2)} rad/s for a body yaw rate of 1 rad/s")
