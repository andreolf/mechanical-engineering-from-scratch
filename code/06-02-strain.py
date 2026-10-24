"""Small strain from a displacement field on a grid: eps = (grad u + grad u^T) / 2, by central differences."""
import numpy as np


def strain_field(ux, uy, h):
    """ux, uy sampled on a grid with spacing h (axis 0 = y, axis 1 = x). Returns eps_xx, eps_yy, eps_xy, rotation."""
    dux_dy, dux_dx = np.gradient(ux, h, edge_order=2)
    duy_dy, duy_dx = np.gradient(uy, h, edge_order=2)
    return dux_dx, duy_dy, 0.5 * (dux_dy + duy_dx), 0.5 * (duy_dx - dux_dy)


if __name__ == "__main__":
    h = 0.01
    y, x = np.mgrid[0:1 + h / 2:h, 0:1 + h / 2:h]
    # stretch 0.2 % in x, contract 0.06 % in y, shear: a 1 m square patch of aluminium skin
    ux = 0.002 * x + 0.0005 * y
    uy = -0.0006 * y + 0.0005 * x
    exx, eyy, exy, w = strain_field(ux, uy, h)
    print(f"homogeneous field: eps_xx {exx.mean():.6f}, eps_yy {eyy.mean():.6f}, eps_xy {exy.mean():.6f}, rotation {w.mean():.2e}")
    assert np.allclose(exx, 0.002) and np.allclose(eyy, -0.0006) and np.allclose(exy, 0.0005) and np.allclose(w, 0)
    # a rigid rotation by theta: small strain is only second order, -theta^2/2 on the diagonal
    for th in (1e-2, 1e-3):
        c, s = np.cos(th), np.sin(th)
        ux, uy = c * x - s * y - x, s * x + c * y - y
        exx, eyy, exy, w = strain_field(ux, uy, h)
        print(f"rigid rotation {th:.0e} rad: max |eps| = {max(abs(exx).max(), abs(exy).max()):.3e} (theta^2/2 = {th**2 / 2:.3e}), rotation {w.mean():.6e}")
        assert abs(abs(exx).max() - (1 - c)) < 1e-12 and abs((1 - c) / (th**2 / 2) - 1) < 1e-4 and abs(exy).max() < 1e-12 and abs(w.mean() - s) < 1e-12
    # a bending-like field u_x = -k x y, u_y = k x^2 / 2: eps_xx = -k y varies across the depth, shear strain zero
    k = 0.01
    ux, uy = -k * x * y, k * x**2 / 2
    exx, eyy, exy, w = strain_field(ux, uy, h)
    assert np.allclose(exx, -k * y) and np.allclose(exy, 0, atol=1e-12)
    print(f"bending field: eps_xx from {exx.max():.4f} (y = 0) to {exx.min():.4f} (y = 1), no shear strain")
