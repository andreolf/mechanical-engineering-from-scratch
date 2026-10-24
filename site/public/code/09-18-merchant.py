"""Orthogonal cutting: Merchant's shear-angle model, cutting forces and spindle power, with the shear angle found by minimising the cutting force."""
import math


def forces(phi, alpha, beta, tau_s, t0, w):
    """Cutting and thrust force for shear angle phi, rake alpha, friction angle beta (rad)."""
    Fs = tau_s * t0 * w / math.sin(phi)
    R = Fs / math.cos(phi + beta - alpha)
    return R * math.cos(beta - alpha), R * math.sin(beta - alpha)


def merchant_phi(alpha, beta):
    return math.pi / 4 + alpha / 2 - beta / 2


if __name__ == "__main__":
    alpha, mu = math.radians(10), 0.5
    beta = math.atan(mu)
    tau_s, t0, w, V = 550e6, 0.2e-3, 2e-3, 200 / 60      # medium-carbon steel, feed 0.2 mm, depth 2 mm, 200 m/min
    phi = merchant_phi(alpha, beta)
    # brute-force minimum of the cutting force over the shear angle
    grid = [math.radians(5 + 0.0001 * k) for k in range(500000)]
    phi_num = min(grid, key=lambda p: forces(p, alpha, beta, tau_s, t0, w)[0])
    print(f"Merchant shear angle {math.degrees(phi):.3f} deg; numerical minimum of Fc at {math.degrees(phi_num):.3f} deg")
    assert abs(phi - phi_num) < math.radians(0.001)
    Fc, Ft = forces(phi, alpha, beta, tau_s, t0, w)
    r = math.sin(phi) / math.cos(phi - alpha)
    print(f"chip ratio t0/tc = {r:.3f} (chip {t0/r*1e3:.3f} mm thick)")
    print(f"cutting force {Fc:.0f} N, thrust {Ft:.0f} N; power {Fc*V/1000:.2f} kW")
    print(f"specific cutting energy {Fc/(t0*w)/1e6:.0f} MJ/m^3 (= N/mm^2)")
    # removal rate x specific energy = power
    assert abs(Fc / (t0 * w) * (t0 * w * V) - Fc * V) < 1e-9
    for a in (0, 10, 20):
        p = merchant_phi(math.radians(a), beta)
        print(f"  rake {a:2d} deg: phi {math.degrees(p):.1f} deg, Fc {forces(p, math.radians(a), beta, tau_s, t0, w)[0]:.0f} N")
