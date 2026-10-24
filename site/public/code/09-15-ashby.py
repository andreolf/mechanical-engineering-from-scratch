"""Material selection: performance indices for light, stiff and strong parts, checked by actually sizing a beam in each material."""
import math

DB = {   # E (GPa), density (kg/m^3), yield or failure strength (MPa), price (USD/kg, rough)
    "steel":        (210, 7850, 350, 0.8),
    "aluminium":    (70, 2700, 250, 2.5),
    "titanium":     (115, 4500, 900, 20.0),
    "CFRP":         (70, 1560, 600, 40.0),
    "GFRP":         (25, 1900, 300, 6.0),
    "bamboo":       (18, 700, 120, 1.0),
    "spruce":       (12, 450, 70, 1.5),
    "concrete":     (30, 2400, 4, 0.1),
    "ABS":          (2.3, 1050, 40, 2.5),
}


def index(name, kind):
    E, rho, s, _ = DB[name]; E *= 1e9; s *= 1e6
    return {"tie": E / rho, "beam": math.sqrt(E) / rho, "plate": E ** (1 / 3) / rho, "strong beam": s ** (2 / 3) / rho}[kind]


def beam_mass(name, L=1.0, P=1000.0, delta=0.005):
    """Square-section cantilever of length L sized so the tip deflects delta under P. Returns mass in kg."""
    E, rho, _, _ = DB[name]; E *= 1e9
    I = P * L**3 / (3 * E * delta)       # needed second moment
    b = (12 * I) ** 0.25                 # square side
    return rho * b * b * L


if __name__ == "__main__":
    print("light stiff beam, E^1/2 / rho, and the mass of a 1 m cantilever deflecting 5 mm under 1 kN:")
    order = sorted(DB, key=lambda m: -index(m, "beam"))
    for m in order:
        print(f"  {m:10s} index {index(m, 'beam'):.2f}   mass {beam_mass(m):.2f} kg   cost {beam_mass(m)*DB[m][3]:.2f} USD")
    # mass is exactly proportional to 1/index
    k = [beam_mass(m) * index(m, "beam") for m in DB]
    assert max(k) / min(k) - 1 < 1e-12
    assert order == sorted(DB, key=beam_mass)
    print("ties ranked by E/rho: " + ", ".join(sorted(DB, key=lambda m: -index(m, "tie"))[:4]))
    print("panels ranked by E^1/3/rho: " + ", ".join(sorted(DB, key=lambda m: -index(m, "plate"))[:4]))
