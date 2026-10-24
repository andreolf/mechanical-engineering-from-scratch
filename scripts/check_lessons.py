"""Verifies lesson content numerically:
1. Runs every downloadable lesson code file (each one self-tests with asserts).
2. Re-computes every numeric quiz answer that carries a `py` expression and checks it against the stated answer.
"""
import json, math, pathlib, subprocess, sys, tempfile
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
code_dir = ROOT / "site/public/code"
les_dir = ROOT / "site/public/lessons"
fail = 0
files = sorted(code_dir.glob("*.py"))
for f in files:
    with tempfile.TemporaryDirectory() as tmp:  # run outside the site so outputs like plots don't get published
        r = subprocess.run([sys.executable, str(f)], cwd=tmp, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        fail += 1
        print(f"FAIL code {f.name}\n{r.stdout[-800:]}\n{r.stderr[-1500:]}")
print(f"code files run: {len(files)}, failures: {fail}")
nq = nchk = 0
env = {"math": math, "np": np, "pi": math.pi, "sqrt": math.sqrt, "exp": math.exp, "log": math.log, "sin": math.sin, "cos": math.cos, "tan": math.tan}
for pf in sorted(les_dir.glob("[0-9][0-9].json")):
    data = json.loads(pf.read_text())
    qs = [(lid, q) for lid, l in data["lessons"].items() for q in l["quiz"]] + [(f"test-{data['phase']}", q) for q in data.get("tests", [])]
    for lid, q in qs:
        nq += 1
        if q["type"] == "num":
            if not q.get("py"):
                fail += 1; print(f"FAIL {lid}: numeric question without py check"); continue
            val = eval(q["py"], dict(env))
            nchk += 1
            tol = q["tol"]
            if not abs(val - q["answer"]) <= max(abs(val) * tol / 4, 1e-12):
                fail += 1; print(f"FAIL {lid}: stated {q['answer']} vs computed {val} (tol {tol})")
print(f"quiz questions: {nq}, numeric answers re-computed: {nchk}")
sys.exit(1 if fail else 0)
