"""Reynolds decomposition of a velocity record: mean, fluctuations, Reynolds stresses and turbulent kinetic energy."""
import numpy as np


def decompose(u):
    U = u.mean()
    return U, u - U


def reynolds_stresses(u, v, w, rho=1000.0):
    _, up = decompose(u); _, vp = decompose(v); _, wp = decompose(w)
    uu, vv, ww, uv = (up * up).mean(), (vp * vp).mean(), (wp * wp).mean(), (up * vp).mean()
    return {"uu": uu, "vv": vv, "ww": ww, "uv": uv, "k": 0.5 * (uu + vv + ww), "tau_xy": -rho * uv}


def synthetic_channel(n, U=1.5, su=0.15, sv=0.08, sw=0.10, r_uv=-0.4, seed=7):
    """Gaussian fluctuations with a prescribed u'v' correlation, as near the bed of a river."""
    rng = np.random.default_rng(seed)
    a, b, c = rng.standard_normal((3, n))
    u = U + su * a
    v = sv * (r_uv * a + np.sqrt(1 - r_uv ** 2) * b)
    w = sw * c
    return u, v, w


if __name__ == "__main__":
    u, v, w = synthetic_channel(200_000)
    U, up = decompose(u)
    print(f"mean U = {U:.4f} m/s; mean of the fluctuation u' = {up.mean():.1e}")
    assert abs(up.mean()) < 1e-12                                # fluctuations average to zero by construction
    R = reynolds_stresses(u, v, w)
    print(f"<u'u'> = {R['uu']:.5f}, <v'v'> = {R['vv']:.5f}, <w'w'> = {R['ww']:.5f}, <u'v'> = {R['uv']:.6f} m^2/s^2")
    print(f"turbulent kinetic energy k = {R['k']:.5f} J/kg; Reynolds shear stress -rho<u'v'> = {R['tau_xy']:.3f} Pa")
    print(f"expected <u'v'> = r su sv = {-0.4*0.15*0.08:.6f}; turbulence intensity {np.sqrt(R['uu'])/U*100:.2f} %")
    # averaging a product is not the product of averages: the closure problem in one line
    uv_bar = (u * v).mean(); print(f"mean(u v) = {uv_bar:.6f} = U V + <u'v'> = {U*v.mean() + R['uv']:.6f}")
    assert abs(uv_bar - (U * v.mean() + R['uv'])) < 1e-12
