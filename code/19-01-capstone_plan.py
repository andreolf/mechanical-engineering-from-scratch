"""Capstone method: a verification matrix (every requirement traced to a test that passes), a
critical-path schedule (forward and backward pass, float of every task) and a risk register scored
likelihood x impact. The example is a micro-hydro capstone in a Bali village. numpy only."""
import numpy as np

# ---- requirements and the tests that verify them ----
reqs = {
    "R1": "Deliver at least 2.0 kW electrical at the design flow",
    "R2": "Runner stresses below yield / 2 at runaway speed",
    "R3": "Penstock survives the water-hammer pressure of a 2 s valve closure",
    "R4": "Frequency within 50 +- 1 Hz from 20 % to 100 % load",
    "R5": "All figures reproduce from a fresh clone in under 10 minutes",
}
tests = {   # test id: (requirement, method, measured, limit, pass if measured >= limit for '>=' or <= for '<=')
    "T1": ("R1", "test", 2.31, 2.0, ">="),
    "T2": ("R2", "analysis", 0.38, 0.5, "<="),          # sigma / yield
    "T3": ("R3", "analysis", 11.6, 16.0, "<="),         # bar, peak vs rating
    "T4": ("R4", "test", 0.7, 1.0, "<="),               # Hz, worst deviation
    "T5": ("R5", "demonstration", 6.5, 10.0, "<="),     # minutes
    "T6": ("R1", "analysis", 2.42, 2.0, ">="),          # the model also predicts R1
}
def verdict(m, lim, op): return m >= lim if op == ">=" else m <= lim
print("requirement  tests      result")
for r, text in reqs.items():
    ts = [t for t, v in tests.items() if v[0] == r]
    ok = [verdict(*tests[t][2:]) for t in ts]
    print(f"{r:11s}  {','.join(ts):9s}  {'PASS' if ts and all(ok) else 'OPEN'}  {text}")
    assert ts, f"{r} has no test"                       # every requirement has a test
    assert all(ok)
assert set(v[0] for v in tests.values()) <= set(reqs)   # and every test traces to a requirement

# ---- critical path method ----
tasks = {   # id: (duration in weeks, predecessors)
    "A survey site and flow":      (2, []),
    "B hydrology and head":        (2, ["A survey site and flow"]),
    "C turbine design":            (3, ["B hydrology and head"]),
    "D penstock design":           (2, ["B hydrology and head"]),
    "E fabricate runner":          (4, ["C turbine design"]),
    "F buy pipe and generator":    (3, ["D penstock design"]),
    "G install":                   (2, ["E fabricate runner", "F buy pipe and generator"]),
    "H commission and test":       (1, ["G install"]),
    "I write report and publish":  (2, ["H commission and test"]),
}
ES, EF = {}, {}
for t in tasks:                                          # forward pass (tasks listed in a valid order)
    d, pre = tasks[t]
    ES[t] = max((EF[p] for p in pre), default=0); EF[t] = ES[t] + d
end = max(EF.values())
LF, LS = {}, {}
for t in reversed(list(tasks)):                          # backward pass
    succ = [s for s in tasks if t in tasks[s][1]]
    LF[t] = min((LS[s] for s in succ), default=end); LS[t] = LF[t] - tasks[t][0]
print(f"\nproject length {end} weeks")
crit = [t for t in tasks if LS[t] == ES[t]]
for t in tasks: print(f"  {t:28s} ES {ES[t]:2d}  EF {EF[t]:2d}  float {LS[t]-ES[t]}{'  critical' if LS[t]==ES[t] else ''}")
assert end == 16 and [t[0] for t in crit] == list("ABCEGHI")
assert LS["D penstock design"] - ES["D penstock design"] == 2

# ---- risk register: score = likelihood x impact on 1..5 scales ----
risks = [("Dry season flow below design", 4, 4, "Size for the 90 % exceedance flow; measure in August", 2, 4),
         ("Runner casting porosity", 3, 4, "X-ray or dye-penetrant test; second supplier", 2, 3),
         ("Generator delivery slips 4 weeks", 3, 3, "Order in week 4, before the design is frozen", 2, 2),
         ("Village loses interest", 2, 5, "Monthly meeting with the subak and the banjar", 1, 4)]
print("\nrisk                                score  after mitigation")
for name, L, I, act, L2, I2 in sorted(risks, key=lambda r: -r[1] * r[2]):
    print(f"  {name:34s} {L*I:3d}  -> {L2*I2:2d}   {act}")
    assert L2 * I2 < L * I
assert max(L * I for _, L, I, *_ in risks) == 16
