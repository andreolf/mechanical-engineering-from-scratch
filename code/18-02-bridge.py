"""Wheatstone bridge with strain gauges: exact output for quarter, half and full bridges,
the quarter-bridge non-linearity, temperature compensation and lead-wire error. numpy only."""
import numpy as np

def bridge(V, R1, R2, R3, R4):
    """Output V_out = V [R1/(R1+R2) - R4/(R3+R4)]. R1 and R2 form one half, R4 and R3 the other.
    Arms R1 and R3 are opposite, so their changes add; adjacent arms (R1, R2) subtract."""
    return V * (R1 / (R1 + R2) - R4 / (R3 + R4))

R, GF, V = 350.0, 2.1, 5.0
def gauges(eps, kind, app=0.0):
    """Arm resistances for a bending beam with surface strain eps. app = apparent strain from temperature
    (the same on every gauge stuck to the beam)."""
    d = lambda e: R * (1 + GF * (e + app))
    if kind == 'quarter': return d(eps), R, R, R                    # one active gauge, three fixed resistors
    if kind == 'quarter+dummy': return d(eps), d(0.0), R, R        # dummy gauge on unstrained steel, adjacent arm
    if kind == 'half': return d(eps), d(-eps), R, R                # top (tension) and bottom (compression), adjacent
    if kind == 'full': return d(eps), d(-eps), d(eps), d(-eps)

eps = 1000e-6
x = GF * eps
print(f"GF eps = {x:.5f}")
for kind, approx in [('quarter', V * x / 4), ('half', V * x / 2), ('full', V * x)]:
    vo = bridge(V, *gauges(eps, kind))
    print(f"{kind:8s}: exact {vo*1e3:.5f} mV, linear formula {approx*1e3:.5f} mV, non-linearity {(approx/vo-1)*100:.4f} %")
vq = bridge(V, *gauges(eps, 'quarter'))
assert abs(vq - V * x / (4 + 2 * x)) < 1e-15                    # the closed form derived in the text
assert abs(vq / (V * x / 4) - 1) < 1.1e-3                         # quarter bridge ~ V GF eps / 4
assert abs(bridge(V, *gauges(eps, 'half')) - V * x / 2) < 1e-15   # half and full bridges are exactly linear
assert abs(bridge(V, *gauges(eps, 'full')) - V * x) < 1e-15

# non-linearity grows with strain: at 1 % strain (a yielding mild-steel coupon)
for e in (1e-3, 5e-3, 1e-2):
    xe = GF * e
    print(f"eps = {e*1e6:6.0f} microstrain: quarter-bridge reads {bridge(V, *gauges(e, 'quarter')) / (V/4*GF):.6f} -> error {(1 - bridge(V, *gauges(e, 'quarter')) / (V*xe/4))*100:.3f} %")

# temperature: 10 K warmer, gauge on steel shows 1.5 microstrain/K of apparent strain
app = 10 * 1.5e-6
for kind in ('quarter', 'quarter+dummy', 'half'):
    v0 = bridge(V, *gauges(0.0, kind, app))
    print(f"{kind:14s}: zero shift from +10 K = {v0*1e6:8.3f} microvolt = {v0 / (V*GF/4) * 1e6:6.2f} microstrain (quarter-bridge scale)")
assert abs(bridge(V, *gauges(0.0, 'half', app))) < 1e-15 and abs(bridge(V, *gauges(0.0, 'quarter+dummy', app))) < 1e-15

# lead wires: 10 m of 0.14 mm^2 copper each way in series with a quarter-bridge gauge
Rl = 2 * 0.0175 * 10 / 0.14                                      # ohm, both leads
vo = bridge(V, R * (1 + x) + Rl, R, R, R) - bridge(V, R + Rl, R, R, R)   # sensitivity after re-zeroing
print(f"lead resistance {Rl:.3f} ohm desensitises the quarter bridge by {(1 - vo / vq)*100:.2f} % (expected R/(R+R_L) -> {Rl/(R+Rl)*100:.2f} %)")
assert abs((1 - vo / vq) - Rl / (R + Rl)) < 2e-4
