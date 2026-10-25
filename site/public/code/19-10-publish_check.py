"""Publishing a reproducible project: SHA-256 written from scratch (checked against hashlib), a
manifest of output hashes, and a check that two fresh copies of a small project reproduce every
hash, while an unseeded or time-stamped output does not. numpy only plus the standard library."""
import hashlib, os, shutil, subprocess, sys, tempfile
import numpy as np

K = np.array([int(x, 16) for x in """428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 d807aa98 12835b01
243185be 550c7dc3 72be5d74 80deb1fe 9bdc06a7 c19bf174 e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da
983e5152 a831c66d b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb
81c2c92e 92722c85 a2bfe8a1 a81a664b c24b8b70 c76c51a3 d192e819 d6990624 f40e3585 106aa070 19a4c116 1e376c08 2748774c 34b0bcb5
391c0cb3 4ed8aa4a 5b9cca4f 682e6ff3 748f82ee 78a5636f 84c87814 8cc70208 90befffa a4506ceb bef9a3f7 c67178f2""".split()], dtype=np.uint64)

def sha256(data: bytes) -> str:
    M = 0xFFFFFFFF
    rotr = lambda x, n: ((x >> n) | (x << (32 - n))) & M
    h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    msg = data + b"\x80" + b"\x00" * ((55 - len(data)) % 64) + (8 * len(data)).to_bytes(8, "big")
    for c in range(0, len(msg), 64):
        w = [int.from_bytes(msg[c + 4 * i: c + 4 * i + 4], "big") for i in range(16)]
        for i in range(16, 64):
            s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & M)
        a, b, cc, d, e, f, g, hh = h
        for i in range(64):
            S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25); ch = (e & f) ^ (~e & g)
            t1 = (hh + S1 + ch + int(K[i]) + w[i]) & M
            S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22); mj = (a & b) ^ (a & cc) ^ (b & cc)
            t2 = (S0 + mj) & M
            hh, g, f, e, d, cc, b, a = g, f, e, (d + t1) & M, cc, b, a, (t1 + t2) & M
        h = [(x + y) & M for x, y in zip(h, [a, b, cc, d, e, f, g, hh])]
    return "".join(f"{x:08x}" for x in h)

assert sha256(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"     # FIPS 180-2 test vector
for n in (0, 55, 56, 64, 119, 1000):
    s = bytes(range(256)) * 4
    assert sha256(s[:n]) == hashlib.sha256(s[:n]).hexdigest()
print("SHA-256 from scratch matches the FIPS test vector and hashlib at every padding edge case")

# a tiny project: a deterministic analysis, a seeded Monte Carlo, and a careless one
project = {
    "README.md": "# Pole check\nRun `python3 run_all.py`. Outputs go to out/. Hashes are in MANIFEST.sha256.\n",
    "analysis.py": (
        "import numpy as np\n"
        "D, t, L, F = 0.1683, 0.005, 4.5, 1296.0\n"
        "I = np.pi / 64 * (D**4 - (D - 2*t)**4)\n"
        "print(f'I = {I:.6e} m^4')\n"
        "print(f'base stress = {F*L/(I/(D/2))/1e6:.4f} MPa')\n"),
    "montecarlo.py": (
        "import numpy as np\n"
        "rng = np.random.default_rng(2026)\n"
        "V = 5.5 * np.sqrt(-np.log(rng.random(200000)))\n"
        "print(f'P(V > 15 m/s) = {np.mean(V > 15):.5f}')\n"),
    "careless.py": (
        "import numpy as np, time\n"
        "print(f'run at {time.time_ns()}')\n"
        "print(f'P(V > 15 m/s) = {np.mean(5.5*np.sqrt(-np.log(np.random.random(1000))) > 15):.5f}')\n"),
    "run_all.py": (
        "import subprocess, sys, os\n"
        "os.makedirs('out', exist_ok=True)\n"
        "for s in ('analysis', 'montecarlo', 'careless'):\n"
        "    r = subprocess.run([sys.executable, s + '.py'], capture_output=True, text=True, check=True)\n"
        "    open(f'out/{s}.txt', 'w', newline='\\n').write(r.stdout)\n"),
}

def build_and_hash(root):
    subprocess.run([sys.executable, "run_all.py"], cwd=root, check=True, env={**os.environ, "PYTHONHASHSEED": "0"})
    return {f: sha256(open(os.path.join(root, "out", f), "rb").read()) for f in sorted(os.listdir(os.path.join(root, "out")))}

with tempfile.TemporaryDirectory() as tmp:
    src = os.path.join(tmp, "src")
    os.makedirs(src)
    for name, text in project.items():
        open(os.path.join(src, name), "w", newline="\n").write(text)
    manifest = build_and_hash(src)                           # the author's run, published with the code
    open(os.path.join(src, "MANIFEST.sha256"), "w").write("".join(f"{h}  out/{f}\n" for f, h in manifest.items()))
    print("\nMANIFEST.sha256")
    print(open(os.path.join(src, "MANIFEST.sha256")).read(), end="")
    results = []
    for k in range(2):                                       # two fresh copies: only the source, no out/ folder
        fresh = os.path.join(tmp, f"fresh{k}")
        shutil.copytree(src, fresh, ignore=shutil.ignore_patterns("out"))
        assert not os.path.exists(os.path.join(fresh, "out"))
        results.append(build_and_hash(fresh))
    print("\nfile              copy 1   copy 2")
    for f in manifest:
        ok = [r[f] == manifest[f] for r in results]
        print(f"{f:<16}  {'match' if ok[0] else 'DIFF':>6}   {'match' if ok[1] else 'DIFF':>6}")
    assert all(r["analysis.txt"] == manifest["analysis.txt"] and r["montecarlo.txt"] == manifest["montecarlo.txt"] for r in results)
    assert all(r["careless.txt"] != manifest["careless.txt"] for r in results)
    print("\n" + open(os.path.join(src, "out", "analysis.txt")).read() + open(os.path.join(src, "out", "montecarlo.txt")).read(), end="")
p = np.exp(-(15 / 5.5) ** 2)
print(f"exact Weibull P(V > 15) = {p:.5f}")
