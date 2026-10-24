"""Navier-Stokes: symbolic check that plane Poiseuille flow and the Taylor-Green vortex are exact solutions, and that a wrong field is not."""
import sympy as sp

x, y, t = sp.symbols("x y t", real=True)
rho, mu, G, h, U = sp.symbols("rho mu G h U", positive=True)


def residuals(u, v, p):
    """Continuity and the two momentum equations, each rearranged to equal zero."""
    cont = sp.diff(u, x) + sp.diff(v, y)
    lap = lambda f: sp.diff(f, x, 2) + sp.diff(f, y, 2)
    mx = rho * (sp.diff(u, t) + u * sp.diff(u, x) + v * sp.diff(u, y)) + sp.diff(p, x) - mu * lap(u)
    my = rho * (sp.diff(v, t) + u * sp.diff(v, x) + v * sp.diff(v, y)) + sp.diff(p, y) - mu * lap(v)
    return [sp.simplify(e) for e in (cont, mx, my)]


if __name__ == "__main__":
    # plane Poiseuille flow between plates at y = +-h driven by a pressure gradient dp/dx = -G
    u = G / (2 * mu) * (h ** 2 - y ** 2); v = sp.Integer(0); p = -G * x
    print("Poiseuille residuals:", residuals(u, v, p))
    assert residuals(u, v, p) == [0, 0, 0]
    # Taylor-Green vortex, decaying in time
    nu = mu / rho; F = sp.exp(-2 * nu * t)
    u = U * sp.sin(x) * sp.cos(y) * F; v = -U * sp.cos(x) * sp.sin(y) * F
    p = rho * U ** 2 / 4 * (sp.cos(2 * x) + sp.cos(2 * y)) * F ** 2
    print("Taylor-Green residuals:", residuals(u, v, p))
    assert residuals(u, v, p) == [0, 0, 0]
    # a field that conserves mass but has the wrong pressure fails the momentum equation
    print("Taylor-Green with p = 0:", residuals(u, v, sp.Integer(0))[1])
    assert residuals(u, v, sp.Integer(0))[1] != 0
    # the plane Poiseuille flow rate per unit width and mean speed
    Q = sp.integrate(G / (2 * mu) * (h ** 2 - y ** 2), (y, -h, h))
    print("flow per unit width:", sp.simplify(Q), "; mean / max:", sp.simplify(Q / (2 * h) / (G * h ** 2 / (2 * mu))))
