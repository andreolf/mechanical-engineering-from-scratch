"""Detachable ski-lift grip and haul rope (educational model): friction grip capacity against the downhill pull of a loaded chair, the steepest rope angle a grip can hold, line tensions and the drive bullwheel slip check."""
import math
import numpy as np

G = 9.81


def downhill_force(m, slope):
    return m * G * math.sin(slope)


def grip_capacity(F_clamp, mu, faces=2):
    return mu * F_clamp * faces


def grip_holds(F_clamp, mu, m, slope, SF):
    return grip_capacity(F_clamp, mu) >= SF * downhill_force(m, slope)


def max_slope(F_clamp, mu, m, SF):
    s = grip_capacity(F_clamp, mu) / (SF * m * G)
    return math.asin(min(s, 1.0))


def line_tension(T0, rope_kg_m, carrier_kg, spacing, height):
    """Tension rise over a vertical height for a rope with carriers every `spacing` metres (friction ignored)."""
    w = (rope_kg_m + carrier_kg / spacing) * G
    return T0 + w * height


if __name__ == "__main__":
    m_chair, m_rider, riders = 250.0, 100.0, 4
    m = m_chair + riders * m_rider
    mu, SF, F_clamp = 0.20, 3.0, 35e3
    steep = math.radians(45)
    need = SF * downhill_force(m, steep)
    print(f"loaded chair {m:.0f} kg; downhill pull at 45 deg {downhill_force(m, steep):.0f} N; required capacity with SF {SF}: {need:.0f} N")
    print(f"grip: clamp {F_clamp/1000:.0f} kN, capacity {grip_capacity(F_clamp, mu):.0f} N -> holds: {grip_holds(F_clamp, mu, m, steep, SF)}")
    th = max_slope(F_clamp, mu, m, SF)
    print(f"steepest rope angle it holds with SF {SF}: {math.degrees(th):.2f} deg")
    # the grip holds exactly when friction capacity exceeds the slope component times SF: check across angles
    for deg in np.linspace(0, 89, 179):
        s = math.radians(deg)
        assert grip_holds(F_clamp, mu, m, s, SF) == (grip_capacity(F_clamp, mu) >= SF * m * G * math.sin(s))
        assert grip_holds(F_clamp, mu, m, s, SF) == (s <= th + 1e-12)
    F_min = need / (2 * mu)
    print(f"minimum clamp force for 45 deg: {F_min/1000:.2f} kN")
    # line: 400 m vertical, 6.5 kg/m rope, chairs every 20 m, tension at the bottom 200 kN from the tensioning weight
    H, rope, spacing, T0, v = 400.0, 6.5, 20.0, 200e3, 5.0
    T_up = line_tension(T0, rope, m, spacing, H)          # loaded chairs going up
    T_down = line_tension(T0, rope, m_chair, spacing, H)  # empty chairs coming down
    ratio = T_up / T_down
    capstan = math.exp(0.25 * math.pi)                    # lined bullwheel, 180 degree wrap
    print(f"top tensions: uphill {T_up/1000:.1f} kN, downhill {T_down/1000:.1f} kN; ratio {ratio:.3f} vs capstan limit {capstan:.3f}")
    assert ratio < capstan
    print(f"drive power ignoring friction: {(T_up - T_down) * v / 1000:.0f} kW at {v} m/s")
    breaking = 1.6e6
    print(f"rope safety factor on breaking load: {breaking / T_up:.2f}")
