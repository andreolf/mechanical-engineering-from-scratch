"""A ski jumper in flight: gravity plus quadratic drag, integrated with RK4."""
import math
import numpy as np


def rk4(f, y0, t_end, dt):
    ys, t, y = [np.array(y0, float)], 0.0, np.array(y0, float)
    while t < t_end - 1e-12:
        h = min(dt, t_end - t)
        k1 = f(y); k2 = f(y + h / 2 * k1); k3 = f(y + h / 2 * k2); k4 = f(y + h * k3)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += h; ys.append(y)
    return np.array(ys)


def jumper(m=65.0, cdA=0.5, rho=1.2, g=9.81):
    """State (x, y, vx, vy); drag force 0.5 rho CdA |v| v opposes the velocity (no lift here)."""
    def f(s):
        vx, vy = s[2], s[3]; v = math.hypot(vx, vy)
        k = 0.5 * rho * cdA * v / m
        return np.array([vx, vy, -k * vx, -g - k * vy])
    return f


def landing(traj, slope_deg, dt):
    """First crossing of a straight landing slope y = -tan(slope) x through the take-off point."""
    s = math.tan(math.radians(slope_deg))
    gap = traj[:, 1] + s * traj[:, 0]
    i = int(np.argmax(gap < 0))
    a = gap[i - 1] / (gap[i - 1] - gap[i])             # linear interpolation inside the step
    return traj[i - 1] + a * (traj[i] - traj[i - 1]), (i - 1 + a) * dt


if __name__ == "__main__":
    v0, ang, dt = 25.0, -11.0, 0.001                  # take-off at 90 km/h, table angled 11 deg down
    s0 = [0, 0, v0 * math.cos(math.radians(ang)), v0 * math.sin(math.radians(ang))]
    # zero drag must reproduce the parabola x = vx t, y = vy t - g t^2 / 2
    tr = rk4(jumper(cdA=0.0), s0, 3.0, dt)
    t = np.arange(len(tr)) * dt
    para_y = s0[3] * t - 9.81 * t**2 / 2
    print(f"no drag: max |y - parabola| = {np.max(np.abs(tr[:, 1] - para_y)):.2e} m")
    assert np.max(np.abs(tr[:, 1] - para_y)) < 1e-9 and np.max(np.abs(tr[:, 0] - s0[2] * t)) < 1e-9
    for cdA in (0.0, 0.3, 0.5, 0.8):
        tr = rk4(jumper(cdA=cdA), s0, 8.0, dt)
        p, tl = landing(tr, 35.0, dt)
        dist = math.hypot(p[0], p[1])
        v = math.hypot(p[2], p[3])
        print(f"CdA = {cdA:.1f} m^2: lands {dist:6.2f} m down a 35 deg slope after {tl:.2f} s at {v*3.6:5.1f} km/h")
    # hand check of the no-drag landing: y = -tan(35) x with x = vx t, y = vy t - g t^2/2
    vx, vy = s0[2], s0[3]
    tl = 2 * (vy + vx * math.tan(math.radians(35))) / 9.81
    print(f"hand, no drag: t = {tl:.4f} s, distance {vx * tl / math.cos(math.radians(35)):.2f} m")
