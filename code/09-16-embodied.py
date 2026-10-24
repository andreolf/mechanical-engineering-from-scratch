"""Embodied energy and carbon: the 09.15 cantilever in each material, and when lightweighting a car part pays back its production energy."""
import math

#            E GPa, rho, MJ/kg, kg CO2/kg (rough cradle-to-gate values, primary production)
DB = {
    "steel":     (210, 7850, 25.0, 2.0),
    "aluminium": (70, 2700, 200.0, 12.0),
    "recycled Al": (70, 2700, 30.0, 2.0),
    "titanium":  (115, 4500, 600.0, 40.0),
    "CFRP":      (70, 1560, 270.0, 25.0),
    "bamboo":    (18, 700, 3.0, 0.4),
    "spruce":    (12, 450, 8.0, 0.5),
}


def beam_mass(name, L=1.0, P=1000.0, delta=0.005):
    E, rho, _, _ = DB[name]; I = P * L**3 / (3 * E * 1e9 * delta); b = (12 * I) ** 0.25
    return rho * b * b * L


def use_phase_MJ_per_kg(km=200000, L_per_100km_per_100kg=0.35, MJ_per_L=34.2):
    """Fuel energy to carry one extra kilogram over the car's life."""
    return km / 100 * L_per_100km_per_100kg / 100 * MJ_per_L


if __name__ == "__main__":
    print("1 m cantilever, 5 mm under 1 kN:")
    res = {}
    for m, (E, rho, H, co2) in DB.items():
        mass = beam_mass(m); res[m] = (mass, mass * H, mass * co2)
        print(f"  {m:12s} {mass:6.2f} kg  {mass*H:7.1f} MJ  {mass*co2:6.2f} kg CO2")
    # stiffness-limited beam: energy index is E^1/2 / (rho H)
    for m in DB:
        E, rho, H, _ = DB[m]
        assert abs(res[m][1] * math.sqrt(E * 1e9) / (rho * H) / (res["steel"][1] * math.sqrt(210e9) / (7850 * 25)) - 1) < 1e-12
    u = use_phase_MJ_per_kg()
    print(f"carrying 1 kg in a car for 200 000 km costs {u:.0f} MJ of fuel")
    # replace a 10 kg steel panel by aluminium with 1.68x less mass (09.15 beam ratio)... panel index ratio is 2.02
    ms = 10.0; ma = ms / ((7850 / 2700) * (70 / 210) ** (1 / 3))
    extra = ma * 200 - ms * 25; saved = (ms - ma) * u
    print(f"steel panel 10 kg -> primary aluminium {ma:.2f} kg: +{extra:.0f} MJ to make, saves {saved:.0f} MJ of fuel; net {saved-extra:+.0f} MJ")
    km_even = extra / ((ms - ma) * use_phase_MJ_per_kg(km=1))
    print(f"  pays back after {km_even:.0f} km")
    rec = ma * 30 - ms * 25
    print(f"  recycled aluminium: {rec:+.0f} MJ to make, so it is ahead from the first kilometre")
    assert rec < 0
    assert km_even > 0 and saved > extra
