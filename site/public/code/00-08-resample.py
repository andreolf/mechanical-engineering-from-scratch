"""Parse irregular sensor CSV, convert 4-20 mA to metres, resample to hourly by linear interpolation."""
import csv
import io
import math
import random
from bisect import bisect_right


def ma_to_level(ma, lo=0.0, hi=5.0):
    if not 3.8 <= ma <= 20.5:
        raise ValueError(f"{ma} mA is outside the loop range: broken wire or sensor fault")
    return lo + (ma - 4.0) / 16.0 * (hi - lo)


def make_sample_csv(seed=3):
    """Three days of 10-minute samples with jitter and a 2-hour modem dropout."""
    rng = random.Random(seed)
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["t_seconds", "current_mA"])
    t = 0.0
    while t < 3 * 86400:
        if not (30 * 3600 <= t < 32 * 3600):     # dropout
            level = 2.2 + 0.3 * math.sin(2 * math.pi * t / 86400) + rng.gauss(0, 0.005)
            w.writerow([f"{t:.0f}", f"{4 + 16 * level / 5:.4f}"])
        t += 600 + rng.uniform(-30, 30)
    return out.getvalue()


def read_series(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    t = [float(r["t_seconds"]) for r in rows]
    y = [ma_to_level(float(r["current_mA"])) for r in rows]
    return t, y


def interp(t, ts, ys):
    i = bisect_right(ts, t) - 1
    i = max(0, min(i, len(ts) - 2))
    f = (t - ts[i]) / (ts[i + 1] - ts[i])
    return ys[i] + f * (ys[i + 1] - ys[i])


def resample(ts, ys, step=3600):
    grid = [ts[0] + k * step for k in range(int((ts[-1] - ts[0]) // step) + 1)]
    gap = max(b - a for a, b in zip(ts, ts[1:]))
    return grid, [interp(t, ts, ys) for t in grid], gap


if __name__ == "__main__":
    assert abs(ma_to_level(11.2) - 2.25) < 1e-12
    ts, ys = read_series(make_sample_csv())
    grid, hourly, gap = resample(ts, ys)
    assert all(math.isfinite(v) for v in hourly)                 # no NaNs
    raw_mean = sum((y0 + y1) / 2 * (t1 - t0) for t0, t1, y0, y1 in zip(ts, ts[1:], ys, ys[1:])) / (ts[-1] - ts[0])
    new_mean = sum(hourly) / len(hourly)
    print(f"{len(ts)} raw samples -> {len(hourly)} hourly, longest gap {gap / 3600:.1f} h")
    print(f"mean raw {raw_mean:.4f} m, hourly {new_mean:.4f} m")
    assert abs(new_mean / raw_mean - 1) < 0.01                   # mean kept within 1%
    assert gap > 7000                                            # the dropout is reported
    f, fs = 0.9, 1.0
    assert abs(abs(f - round(f / fs) * fs) - 0.1) < 1e-12        # alias of 0.9 Hz at 1 Hz
