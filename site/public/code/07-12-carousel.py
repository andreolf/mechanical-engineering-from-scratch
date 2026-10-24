"""A ball rolled across a turning carousel: straight in the inertial frame, curved in the rotating one."""
import math
import numpy as np


def rotating_frame_sim(x0, v0, Om, t_end, dt=1e-4):
    """a_rel = -2 Om x v_rel - Om x (Om x r)  (no real force; Om along +z). RK4."""
    def f(s):
        x, y, vx, vy = s
        ax = 2 * Om * vy + Om**2 * x
        ay = -2 * Om * vx + Om**2 * y
        return np.array([vx, vy, ax, ay])
    s = np.array([*x0, *v0], float); out = [s.copy()]
    for _ in range(int(round(t_end / dt))):
        k1 = f(s); k2 = f(s + dt / 2 * k1); k3 = f(s + dt / 2 * k2); k4 = f(s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); out.append(s.copy())
    return np.array(out)


if __name__ == "__main__":
    Om = 2 * math.pi / 6.0           # carousel turning anticlockwise once every 6 s
    R = 3.0
    # ball rolled from the centre straight "outwards" along the rotating x axis at 2 m/s (frictionless, no rolling)
    x0, v_rel0 = np.array([0.0, 0.0]), np.array([2.0, 0.0])
    t_end = 1.2
    tr = rotating_frame_sim(x0, v_rel0, Om, t_end)
    # inertial view: at t = 0 the frames coincide; the inertial velocity is v_rel + Om x r = v_rel (r = 0)
    t = np.linspace(0, t_end, len(tr))
    X, Y = 2.0 * t, 0.0 * t                                    # a straight line
    xr = X * np.cos(Om * t) + Y * np.sin(Om * t); yr = -X * np.sin(Om * t) + Y * np.cos(Om * t)
    err = np.max(np.hypot(tr[:, 0] - xr, tr[:, 1] - yr))
    print(f"rotating-frame simulation vs transformed straight line: max difference {err:.1e} m")
    assert err < 1e-9
    xe, ye = tr[-1, :2]
    print(f"after {t_end} s the ball is at ({xe:.3f}, {ye:.3f}) m in the carousel frame: deflected to the {'right' if ye < 0 else 'left'}")
    assert ye < 0                     # anticlockwise rotation -> deflection to the right (like the northern hemisphere)
    # reversing the rotation reverses the deflection
    tr2 = rotating_frame_sim(x0, v_rel0, -Om, t_end)
    print(f"clockwise carousel: ball ends at ({tr2[-1,0]:.3f}, {tr2[-1,1]:.3f}) m: deflected to the left")
    assert tr2[-1, 1] > 0
    # early on the Coriolis acceleration dominates: 2 Om v
    print(f"Coriolis acceleration 2 Om v = {2 * Om * 2.0:.3f} m/s^2; small-time sideways drift Om v t^2 at 0.1 s: {Om * 2.0 * 0.01:.5f} m vs simulated {-rotating_frame_sim(x0, v_rel0, Om, 0.1)[-1,1]:.5f} m")
    # Foucault-style scale: Earth's rotation at 47 deg N on a 1000 m/s shell over 30 s
    Om_e = 7.292e-5 * math.sin(math.radians(47))
    print(f"Earth at 47 deg N, 1000 m/s for 20 s: Coriolis drift ~ {Om_e * 1000 * 20**2:.2f} m")
