"""A subak irrigation network: a river intake, a proportional divider weir that splits the canal
into three branches, and chains of terraced fields that spill from one to the next over outlet
weirs. Hourly water balance for a year with assumed seasonal flows, rain, evapotranspiration and
percolation. The mass balance must close at every terrace and for the whole network. numpy only."""
import numpy as np

g = 9.81
def weir(H, b, Cd=0.62):
    """Sharp-crested rectangular weir: Q = (2/3) Cd b sqrt(2g) H^1.5 (H = head over the crest)."""
    return 2 / 3 * Cd * b * np.sqrt(2 * g) * np.clip(H, 0, None) ** 1.5

# proportional divider: three notches at one crest level see the same head, so Q_i ~ b_i
A = np.array([[2400, 2200, 2000, 1800], [1800, 1700, 1600, 1500], [1200, 1100, 1000, 900]], float)   # field areas, m^2
b_div = 0.20 * A.sum(1) / A.sum(1)[0]                    # notch widths in proportion to each branch's land
Q = weir(0.06, b_div)
print(f"notches {np.round(b_div*1e3, 1)} mm; at 6 cm head: {np.round(Q*1e3, 3)} L/s, shares {np.round(Q/Q.sum(), 4)} = land shares {np.round(A.sum(1)/A.sum(), 4)}")
assert np.allclose(Q / Q.sum(), A.sum(1) / A.sum())

nb, nt = 3, 4                                            # branches, terraces per branch
hc, Lo = 0.05, 0.30                                      # field outlet crest 5 cm, 30 cm wide
ET, perc = 5e-3 / 86400, 3e-3 / 86400                    # m/s
dt = 3600.0
hours = np.arange(365 * 24)
day = hours / 24
wet = (day < 120) | (day >= 305)                         # Bali: wet season November to April (day 0 = 1 Jan)
rng = np.random.default_rng(3)
storm = np.zeros(len(hours))
for d in np.where(rng.random(365) < np.where(np.arange(365) < 120, 0.45, np.where(np.arange(365) >= 305, 0.45, 0.08)))[0]:
    storm[d * 24 + 14: d * 24 + 17] = rng.uniform(5, 25) / 3 / 1000 / 3600   # afternoon showers, mm over 3 h -> m/s
Q_river = np.where(wet, 0.060 + 0.02 * np.sin(2 * np.pi * (day - 30) / 365) ** 2, 0.0030)   # assumed river flow at the intake, m^3/s
intake_cap = 0.025

def simulate(rotation=False):
    h = np.zeros((nb, nt)); h[:] = 0.03
    h0 = h.copy()
    led = {k: np.zeros((nb, nt)) for k in ("in", "rain", "out", "et", "perc")}
    wetted = np.zeros((nb, nt)); dry_hours = 0
    for k in hours:
        Qin = min(intake_cap, 0.5 * Q_river[k])          # the intake takes half the river, up to its capacity
        share = b_div / b_div.sum()
        if rotation and not wet[k]:                       # dry-season rotation: the whole flow to one branch for 5 days at a time
            share = np.eye(nb)[int(day[k] // 5) % nb]
        inflow = Qin * share                              # m^3/s into the top terrace of each branch
        for j in range(nt):
            qin = inflow if j == 0 else qout_prev
            qout = np.minimum(weir(h[:, j] - hc, Lo), (h[:, j] - hc).clip(0) * A[:, j] / dt)   # cannot spill more than is above the crest
            vet = np.minimum(ET * A[:, j] * dt, h[:, j] * A[:, j])                            # cannot evaporate more than is there
            vpe = np.where(h[:, j] > 0, np.minimum(perc * A[:, j] * dt, h[:, j] * A[:, j] - vet), 0)
            vr = storm[k] * A[:, j] * dt
            dV = qin * dt + vr - qout * dt - vet - vpe
            h[:, j] += dV / A[:, j]
            for key, val in (("in", qin * dt), ("rain", vr), ("out", qout * dt), ("et", vet), ("perc", vpe)): led[key][:, j] += val
            qout_prev = qout
            if not wet[k]: wetted[:, j] += h[:, j] > 0.01
        dry_hours += not wet[k]
    return h0, h, led, wetted / dry_hours, Qin

for rot in (False, True):
    h0, h, led, frac, _ = simulate(rot)
    dS = (h - h0) * A
    bal = led["in"] + led["rain"] - led["out"] - led["et"] - led["perc"] - dS
    rel = np.abs(bal) / (led["in"] + led["rain"])
    assert rel.max() < 1e-10                                  # mass balance closes at every terrace
    assert np.all(h >= -1e-12)
    for i in range(nb):                                       # and the outflow of one terrace is the inflow of the next
        assert np.allclose(led["out"][i, :-1], led["in"][i, 1:])
    net_in = led["in"][:, 0].sum() + led["rain"].sum()
    net_out = led["out"][:, -1].sum() + led["et"].sum() + led["perc"].sum() + dS.sum()
    print(f"\n{'rotation in the dry season' if rot else 'proportional split all year'}: worst terrace balance error {rel.max():.1e}; network: in {net_in:,.0f} m^3, out + stored {net_out:,.0f} m^3")
    assert abs(net_in - net_out) / net_in < 1e-12
    print("fraction of dry-season hours with standing water (>1 cm), rows = branches, top terrace first:")
    print(np.round(frac, 2))
    if not rot: frac_prop = frac
    else: frac_rot = frac
for name, f in (("proportional", frac_prop), ("rotation", frac_rot)):
    print(f"{name:>12}: mean {f.mean():.3f}, worst terrace {f.min():.3f}, spread (max - min) {f.max() - f.min():.3f}")
assert frac_rot.min() > frac_prop.min() and frac_rot.mean() < frac_prop.mean()   # rotation is fairer to the tail, at a cost in total
print(f"tail-end terrace of branch 3: {frac_prop[2, -1]:.2f} with a proportional split, {frac_rot[2, -1]:.2f} with rotation")
