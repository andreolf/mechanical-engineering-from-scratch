"""Checks curriculum.json: every lesson has every required field, ids are unique, counts match."""
import json, pathlib, sys
d = json.loads((pathlib.Path(__file__).resolve().parent.parent / "curriculum" / "curriculum.json").read_text())
REQ = ["id", "title", "goal", "math", "code", "lab", "test", "tool", "eth"]
ids, n = set(), 0
for p in d["phases"]:
    for l in p["lessons"]:
        n += 1
        missing = [k for k in REQ if not str(l.get(k, "")).strip()]
        assert not missing, (l["id"], missing)
        assert l["id"] not in ids, l["id"]; ids.add(l["id"])
assert n == d["lessonCount"] and len(d["phases"]) == d["phaseCount"]
assert any(k["id"] == "coconut" for p in d["phases"] for l in p["lessons"] for k in l["labLinks"])
assert any(k["id"] == "subak" for p in d["phases"] for l in p["lessons"] for k in l["labLinks"])
print(f"OK: {d['phaseCount']} phases, {n} lessons, all fields present")
