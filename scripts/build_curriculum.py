"""Builds curriculum/curriculum.json and one markdown file per phase from scripts/phases/*.py."""
import json, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "phases"))
from p1 import PHASES as A
from p2 import PHASES as B
from p3 import PHASES as C
from p4 import PHASES as D

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "curriculum"
SITE_DATA = ROOT / "site" / "public"

raw = A + B + C + D
by = {p["slug"]: p for p in raw}
# Werkstoffe und Fertigung is one ETH course: merge materials + manufacturing into one phase.
mat, man = by.pop("materials"), by.pop("manufacturing")
mat = dict(mat, slug="materials-manufacturing", title="Materials & Manufacturing",
           de="Werkstoffe und Fertigung", eth="Werkstoffe und Fertigung; Engineering Design and Material Selection",
           anchor=mat["anchor"] + "; " + man["anchor"],
           summary="Atoms to alloys to finished parts: why materials behave as they do and how things are made.",
           lessons=mat["lessons"] + man["lessons"])
order = ["setup","analysis-1","linear-algebra","analysis-2-3","numerical-methods","statics","deformable-solids",
         "dynamics","vibrations","materials-manufacturing","thermodynamics","fluid-dynamics-1","fluid-dynamics-2",
         "heat-transfer","cad","machine-design","fem","cfd","measurement-control","capstone"]
by["materials-manufacturing"] = mat
assert set(order) == set(by), set(by) ^ set(order)

LABS = {
 "coconut": ("The coconut that never escapes", "https://andreolf.github.io/coconut-lab/"),
 "subak": ("Subak rice terraces", "https://andreolf.github.io/subak-lab/"),
 "truss": ("Break the bridge", "#lab-truss"),
 "flywheel": ("Gyroscope & flywheel", "#lab-flywheel"),
 "pipe": ("Pipe flow & Bernoulli", "#lab-pipe"),
}
phases, total = [], 0
for i, slug in enumerate(order):
    p = by[slug]
    lessons = []
    for j, line in enumerate([l for l in p["lessons"].strip().splitlines() if l.strip()]):
        f = [x.strip() for x in line.split(" | ")]
        assert len(f) == 7, (slug, j, len(f), line[:80])
        title, goal, math, code, lab, test, tool = f
        links = []
        for key in re.findall(r"LAB:(\w+)", lab):
            links.append({"id": key, "title": LABS[key][0], "url": LABS[key][1]})
        if "hero beam" in lab:
            links.append({"id": "beam", "title": "Cantilever beam (hero)", "url": "#hero"})
        lab = re.sub(r"\s*\((LAB:\w+|hero beam)\)", "", lab)
        lessons.append(dict(id=f"{i:02d}.{j+1:02d}", title=title, goal=goal, math=math, code=code,
                            lab=lab, test=test, tool=tool, eth=p["eth"], labLinks=links, status="outline"))
    total += len(lessons)
    phases.append(dict(id=f"{i:02d}", slug=slug, title=p["title"], de=p["de"], eth=p["eth"],
                       ethNamed=p["eth_named"], anchor=p["anchor"], summary=p["summary"], lessons=lessons))

data = dict(title="Mechanical Engineering from Scratch", version="0.1.0", license="MIT",
            author="Francesco Andreoli", generated="scripts/build_curriculum.py",
            note=("ETH course names refer to the ETH Zurich D-MAVT BSc (Programme Regulations 2022) where marked; "
                  "others are generic descriptions. Not affiliated with or endorsed by ETH Zurich."),
            labs=[{"id": k, "title": v[0], "url": v[1]} for k, v in LABS.items()],
            phaseCount=len(phases), lessonCount=total, phases=phases)
OUT.mkdir(exist_ok=True); SITE_DATA.mkdir(parents=True, exist_ok=True)
js = json.dumps(data, indent=1, ensure_ascii=False)
(OUT / "curriculum.json").write_text(js); (SITE_DATA / "curriculum.json").write_text(js)

for old in OUT.glob("phase-*.md"): old.unlink()
idx = ["# Mechanical Engineering from Scratch: Curriculum", "", f"{len(phases)} phases, {total} lessons. Every lesson: derive by hand, code from scratch, prove with a test, then meet the pro tool.", "", data["note"], "", "| # | Phase | ETH reference | Lessons |", "|---|---|---|---|"]
for p in phases:
    fn = f"phase-{p['id']}-{p['slug']}.md"
    idx.append(f"| {p['id']} | [{p['title']}]({fn}) | {p['eth']}{'' if p['ethNamed'] else ' (generic)'} | {len(p['lessons'])} |")
    md = [f"# Phase {p['id']}: {p['title']}", "", f"*{p['de']}*", "", p["summary"], "",
          f"- **ETH reference:** {p['eth']}{'' if p['ethNamed'] else ' (generic description)'}",
          f"- **Real-world anchors:** {p['anchor']}", f"- **Lessons:** {len(p['lessons'])}", ""]
    for l in p["lessons"]:
        md += [f"## {l['id']} {l['title']}", "", f"**Goal:** {l['goal']}", "",
               f"- **Derive by hand:** {l['math']}", f"- **Code from scratch:** {l['code']}",
               f"- **Interactive lab:** {l['lab']}" + "".join(f" ([{k['title']}]({k['url']}))" for k in l["labLinks"]),
               f"- **Test that proves it:** {l['test']}", f"- **Pro tool:** {l['tool']}", f"- **ETH course:** {l['eth']}", ""]
    (OUT / fn).write_text("\n".join(md))
(OUT / "README.md").write_text("\n".join(idx) + "\n")
print(len(phases), total)
for p in phases: print(p["id"], p["title"], len(p["lessons"]))
