"""Bamboo footbridge: a 6 m Pratt truss solved with the direct stiffness method, checked by statics
and by virtual work, then member, buckling, joint and deflection checks. numpy only.
Teaching model, not a design: a real bridge needs tested bamboo, a code and a licensed engineer."""
import numpy as np

L, H, n = 6.0, 1.0, 6                                   # span, depth, panels
E = 15e9                                                # bamboo along the grain, Pa (assumed, test your culms)
Do, t = 0.080, 0.008                                    # culm outer diameter and wall
A = np.pi / 4 * (Do**2 - (Do - 2 * t) ** 2)
I = np.pi / 64 * (Do**4 - (Do - 2 * t) ** 4)
print(f"culm: A = {A*1e6:.1f} mm^2, I = {I*1e12:.0f} mm^4")

# nodes: bottom 0..6 at x = 0..6, top 7..11 at x = 1..5
xy = np.array([[i * L / n, 0] for i in range(n + 1)] + [[i * L / n, H] for i in range(1, n)])
bot = list(range(n + 1)); top = list(range(n + 1, 2 * n))
el = [(bot[i], bot[i + 1]) for i in range(n)]                                    # bottom chord
el += [(top[i], top[i + 1]) for i in range(n - 2)]                               # top chord
el += [(bot[i], top[i - 1]) for i in range(1, n)]                                # verticals
el += [(bot[0], top[0]), (bot[n], top[-1])]                                      # end posts (inclined)
el += [(top[i - 1], bot[i + 1]) for i in range(1, n // 2)] + [(top[i - 1], bot[i - 1]) for i in range(n // 2 + 1, n)]   # Pratt diagonals, down towards midspan
el = np.array(el)
nn, ne = len(xy), len(el)
assert ne + 3 == 2 * nn                                 # statically determinate: m + r = 2j

def solve(F, fixed):
    K = np.zeros((2 * nn, 2 * nn)); geo = []
    for a, b in el:
        d = xy[b] - xy[a]; Le = np.hypot(*d); c, s = d / Le
        k = E * A / Le * np.outer([-c, -s, c, s], [-c, -s, c, s])
        idx = [2 * a, 2 * a + 1, 2 * b, 2 * b + 1]
        K[np.ix_(idx, idx)] += k; geo.append((Le, c, s, idx))
    free = np.setdiff1d(np.arange(2 * nn), fixed)
    u = np.zeros(2 * nn); u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    N = np.array([E * A / Le * (np.array([-c, -s, c, s]) @ u[idx]) for Le, c, s, idx in geo])
    R = K @ u - F
    return u, N, R, np.array([g[0] for g in geo])

# loads per truss (two trusses, 1.2 m deck): crowd 4 kPa plus deck and self weight 0.6 kPa, factored 1.5 and 1.35
w_crowd, w_dead, width = 4.0e3, 0.6e3, 1.2
w = (1.5 * w_crowd + 1.35 * w_dead) * width / 2          # N/m on one truss
F = np.zeros(2 * nn)
for i in bot: F[2 * i + 1] = -w * L / n * (0.5 if i in (0, n) else 1.0)
fixed = [0, 1, 2 * n + 1]                                # pin at left, roller at right
u, N, R, Le = solve(F, fixed)
print(f"design line load {w/1e3:.3f} kN/m per truss, total {w*L/1e3:.2f} kN")
assert np.isclose(R[1] + R[2 * n + 1], w * L) and np.isclose(R[1], R[2 * n + 1])   # reactions carry the load, symmetrically
mid = [k for k, (a, b) in enumerate(el) if {a, b} == {bot[2], bot[3]}][0]
topmid = [k for k, (a, b) in enumerate(el) if {a, b} == {top[1], top[2]}][0]
M = w * L**2 / 8
print(f"bottom chord at midspan {N[mid]/1e3:.3f} kN, top chord {N[topmid]/1e3:.3f} kN; wL^2/(8H) = {M/H/1e3:.3f} kN")
assert np.isclose(N[topmid], -M / H, rtol=1e-9)          # method of sections at midspan (top chord panel 2-3 spans the centre line)
# bottom chord panel 2-3 sits left of midspan: section through it, moment about top node at x = 2
M2 = R[1] * 2 - w * 2**2 / 2
assert np.isclose(N[mid], M2 / H, rtol=1e-9)

# deflection by virtual work: unit load at midspan bottom node
F1 = np.zeros(2 * nn); F1[2 * bot[3] + 1] = -1.0
_, n1, _, _ = solve(F1, fixed)
d_vw = np.sum(N * n1 * Le / (E * A))
print(f"midspan deflection: FEM {-u[2*bot[3]+1]*1e3:.3f} mm, virtual work {d_vw*1e3:.3f} mm")
assert np.isclose(-u[2 * bot[3] + 1], d_vw, rtol=1e-9)

# service deflection under crowd only (unfactored), limit L/250
_, Ns, _, _ = solve(F * (w_crowd / (1.5 * w_crowd + 1.35 * w_dead)), fixed)
us = solve(F * (w_crowd / (1.5 * w_crowd + 1.35 * w_dead)), fixed)[0]
ds = -us[2 * bot[3] + 1]
print(f"crowd-only deflection {ds*1e3:.2f} mm vs L/250 = {L/250*1e3:.1f} mm")

# member checks, characteristic strengths assumed and divided by a material factor 2.0
fc, ft, gm = 40e6, 80e6, 2.0
Pcr = np.pi**2 * E * I / Le**2                           # pin-ended Euler buckling
sig = N / A
comp = N < 0
u_ax = np.where(comp, -sig / (fc / gm), sig / (ft / gm))
u_buck = np.where(comp, -N / (Pcr / 2.0), 0)             # factor 2 on buckling as well
P_bolt = 4.0e3                                           # design shear capacity of one 12 mm bolt through a mortar-filled node (assumed)
names = np.array(["bottom"] * n + ["top"] * (n - 2) + ["vertical"] * (n - 1) + ["end post"] * 2 + ["diagonal"] * (n - 2))
chord = np.isin(names, ["bottom", "top"])
# first attempt: every member is a separate culm bolted at both ends with one bolt
u_joint1 = np.abs(N) / P_bolt
print(f"\none bolt per member end: worst joint utilisation {u_joint1.max():.2f} ({names[np.argmax(u_joint1)]}), so the joints govern by far")
# redesign: chords run as continuous culms through the nodes, so a node only carries the web member forces;
# each web member gets as many bolts as it needs
bolts = np.where(chord, 0, np.maximum(1, np.ceil(np.abs(N) / P_bolt))).astype(int)
print("\nmember      force kN   axial  buckling  bolts")
for k in np.argsort(-np.abs(N)):
    if k in np.argsort(-np.abs(N))[:4] or not chord[k] and bolts[k] == bolts.max():
        print(f"{names[k]:<10} {N[k]/1e3:9.3f}   {u_ax[k]:5.2f}   {u_buck[k]:5.2f}   {bolts[k] if not chord[k] else 'continuous'}")
for kind in ("vertical", "diagonal", "end post"):
    m = names == kind
    print(f"{kind:>9}s: force {np.abs(N[m]).min()/1e3:.3f} to {np.abs(N[m]).max()/1e3:.3f} kN, bolts {bolts[m].min()} to {bolts[m].max()}")
worst = np.maximum(u_ax, u_buck)
k = np.argmax(worst)
print(f"worst member: {names[k]}, utilisation {worst[k]:.2f} ({'buckling' if u_buck[k] > u_ax[k] else 'axial'})")
assert worst.max() < 1.0 and ds < L / 250 and bolts.max() <= 5
