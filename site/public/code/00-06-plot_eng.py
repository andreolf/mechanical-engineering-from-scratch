"""Log-log power-law fitting and a small plotting helper with units in the labels."""
import math
import random


def fit_power_law(xs, ys):
    """Least-squares fit of y = a * x**b on log-log axes. Returns (a, b)."""
    X = [math.log(x) for x in xs]
    Y = [math.log(y) for y in ys]
    mx, my = sum(X) / len(X), sum(Y) / len(Y)
    b = sum((x - mx) * (y - my) for x, y in zip(X, Y)) / sum((x - mx) ** 2 for x in X)
    return math.exp(my - b * mx), b


def plot_eng(xs, ys, xlabel, ylabel, path, fit=None, loglog=True):
    """Save a plot with markers for data and a line for the fit. Needs matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=150)
    ax.plot(xs, ys, "o", ms=3, label="data")
    if fit:
        a, b = fit
        ax.plot(xs, [a * x ** b for x in xs], "-", label=f"fit: {a:.3g} x^{b:.3f}")
    if loglog:
        ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.grid(True, which="both", alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


if __name__ == "__main__":
    rng = random.Random(1)
    xs = [10 ** (i / 20) for i in range(-20, 41)]               # 0.1 to 100
    ys = [3 * x ** 1.5 * math.exp(rng.gauss(0, 0.05)) for x in xs]  # 5% scatter
    a, b = fit_power_law(xs, ys)
    print(f"fitted a = {a:.3f}, b = {b:.4f}")
    assert abs(b - 1.5) < 0.01 and abs(a / 3 - 1) < 0.05

    a2, b2 = fit_power_law([1000, 2000], [12, 96])               # fan example
    assert abs(b2 - 3) < 1e-12 and abs(a2 * 1500 ** b2 - 40.5) < 1e-9
    try:
        plot_eng(xs, ys, "x, m", "y, N", "power_law.png", fit=(a, b))
        print("saved power_law.png")
    except ImportError:
        print("matplotlib not installed; skipped the figure")
