import sys
import numpy as np


def toolchain_report():
    """Return the facts the rest of the course depends on."""
    eps = np.finfo(float).eps
    return {
        "python": sys.version_info[:2],
        "numpy": np.__version__,
        "eps": eps,
        "sum_error": abs((0.1 + 0.2) - 0.3),
    }


def test_toolchain():
    r = toolchain_report()
    assert r["python"] >= (3, 10)
    assert r["eps"] == 2.0 ** -52
    # 0.1 + 0.2 misses 0.3 by a quarter of machine epsilon
    assert r["sum_error"] == r["eps"] / 4
    assert abs((0.1 + 0.2) - 0.3) < 1e-12


if __name__ == "__main__":
    test_toolchain()
    print("toolchain OK:", toolchain_report())
