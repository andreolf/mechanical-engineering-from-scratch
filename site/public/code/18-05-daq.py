"""Data acquisition: an ADC model (resolution, quantisation noise q/sqrt(12), SNR = 6.02 N + 1.76 dB)
and a serial logger that parses accelerometer lines with a checksum. Without a board attached it
replays a simulated byte stream; pass --port /dev/ttyACM0 to read a real one (needs pyserial). numpy only."""
import sys, numpy as np

def adc(v, bits, vref):
    """Ideal ADC: round to the nearest code, clip to 0 .. 2^N - 1. Returns codes."""
    return np.clip(np.round(v / vref * 2**bits), 0, 2**bits - 1).astype(int)

rng = np.random.default_rng(5)
# 1) quantisation noise of a busy signal: the error is uniform on [-q/2, q/2]
for bits, vref in ((10, 5.0), (12, 3.3), (16, 3.3)):
    q = vref / 2**bits
    v = rng.uniform(0.1, vref - 0.1, 200_000)
    e = adc(v, bits, vref) * q - v
    print(f"{bits:2d}-bit, Vref {vref} V: q = {q*1e3:.4f} mV, rms error {e.std()*1e3:.4f} mV, theory q/sqrt(12) = {q/np.sqrt(12)*1e3:.4f} mV")
    assert abs(e.std() / (q / np.sqrt(12)) - 1) < 0.01

# 2) SNR of a full-scale sine: 6.02 N + 1.76 dB
bits, vref, n = 10, 5.0, 2**14
t = np.arange(n)
s = vref / 2 + (2**(bits - 1) - 1) * vref / 2**bits * np.sin(2 * np.pi * 1001 / n * t)   # 1001 cycles: not a divisor, so codes do not repeat
err = adc(s, bits, vref) * vref / 2**bits - s
snr = 10 * np.log10(np.mean((s - vref / 2) ** 2) / np.mean(err**2))
print(f"10-bit full-scale sine: SNR {snr:.2f} dB, theory {6.02*bits+1.76:.2f} dB")
assert abs(snr - (6.02 * bits + 1.76)) < 0.3

# 3) an accelerometer at rest on an Arduino Uno: ADXL335 at 3.3 V, 0.33 V/g, 1.65 V at 0 g; 10-bit ADC, Vref 5 V
sens, v0, q = 0.33, 1.65, 5.0 / 1024
print(f"one ADC step = {q*1e3:.3f} mV = {q/sens*1e3:.2f} mg")
quiet = v0 + 0.0002 * rng.standard_normal(4000)          # sensor noise 0.2 mV rms, much less than q
noisy = v0 + 0.004 * rng.standard_normal(4000)           # 4 mV rms (a noisy supply), about q
for name, x in (("quiet", quiet), ("noisy", noisy)):
    c = adc(x, 10, 5.0)
    means = c[: 4000 // 64 * 64].reshape(-1, 64).mean(1) * q
    print(f"{name}: {len(np.unique(c))} distinct codes, averaging 64 readings gives {(means.mean()-v0)/sens*1e3:+.3f} mg bias, spread {means.std()/sens*1e3:.3f} mg")
c = adc(quiet, 10, 5.0); assert len(np.unique(c)) == 1          # stuck on one code: averaging cannot help
m = adc(noisy, 10, 5.0)[:3968].reshape(-1, 64).mean(1) * q
assert abs(m.mean() - v0) < 0.2 * q                              # dither: noise lets averaging resolve below one step

# 4) the logger: lines "t_ms,ax,ay,az*CS" where CS is the XOR of the bytes before '*', in hex
def checksum(body): 
    c = 0
    for ch in body.encode(): c ^= ch
    return f"{c:02X}"
def parse(line):
    line = line.strip()
    if '*' not in line: return None
    body, cs = line.rsplit('*', 1)
    if checksum(body) != cs.upper(): return None
    f = body.split(',')
    return (int(f[0]), *map(int, f[1:])) if len(f) == 4 else None

def simulated_stream(n=200):
    for k in range(n):
        tm = 10 * k
        ax, ay = adc(np.array([v0 + 0.33 * 0.2 * np.sin(2 * np.pi * 1.5 * tm / 1000), v0]), 10, 5.0)
        az = adc(np.array([v0 + 0.33]), 10, 5.0)[0]
        body = f"{tm},{ax},{ay},{az}"
        line = f"{body}*{checksum(body)}\n"
        if k == 57: line = line.replace(',', ';', 1)          # a corrupted line, as a loose wire produces
        yield line

if '--port' in sys.argv:                                      # real hardware: python daq.py --port /dev/ttyACM0
    import serial                                             # pip install pyserial
    port = serial.Serial(sys.argv[sys.argv.index('--port') + 1], 115200, timeout=2)
    lines = (port.readline().decode(errors='replace') for _ in range(2000))
else:
    lines = simulated_stream()
rows, bad = [], 0
for ln in lines:
    r = parse(ln)
    if r is None: bad += 1
    else: rows.append(r)
data = np.array(rows, float)
np.savetxt("accel_log.csv", data, delimiter=",", header="t_ms,ax,ay,az", fmt="%g")
g = (data[:, 1:] * q - v0) / sens
print(f"logged {len(rows)} lines, rejected {bad}; mean az = {g[:, 2].mean():.3f} g, ax amplitude {(g[:,0].max()-g[:,0].min())/2:.3f} g")
if '--port' not in sys.argv:
    assert bad == 1 and len(rows) == 199 and abs(g[:, 2].mean() - 1) < q / sens
