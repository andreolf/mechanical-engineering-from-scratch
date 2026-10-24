"""Corrosion: Faraday's law for metal loss, penetration rate from current density, galvanic area effects and sacrificial anode sizing."""
F = 96485.0   # C/mol

METALS = {   # molar mass g/mol, valence, density kg/m^3
    "iron": (55.845, 2, 7870.0),
    "zinc": (65.38, 2, 7140.0),
    "aluminium": (26.98, 3, 2700.0),
    "copper": (63.55, 2, 8960.0),
}


def mass_loss(I, t, metal):
    """Grams dissolved by current I (A) flowing for t seconds."""
    M, n, _ = METALS[metal]
    return I * t * M / (n * F)


def penetration_mm_per_year(i_uA_cm2, metal):
    """Uniform thinning rate from a corrosion current density in microamps per square centimetre."""
    M, n, rho = METALS[metal]
    i = i_uA_cm2 * 1e-6 / 1e-4                  # A/m^2
    v = i * (M / 1000) / (n * F * rho)          # m/s
    return v * 3600 * 24 * 365.25 * 1000


if __name__ == "__main__":
    yr = 365.25 * 24 * 3600
    print(f"1 A for a year dissolves {mass_loss(1, yr, 'iron')/1000:.2f} kg of iron")
    for m in METALS:
        print(f"  {m}: 1 uA/cm^2 thins it by {penetration_mm_per_year(1, m)*1000:.2f} um per year")
    assert abs(penetration_mm_per_year(1, "iron") - 0.0116) < 2e-4
    # galvanic couple: the same total current flows through anode and cathode, so a small anode corrodes fast
    I = 2e-3   # A, set by the cathode's oxygen reduction
    for anode_cm2 in (1000, 10):
        i = I / anode_cm2 * 1e6
        print(f"steel anode of {anode_cm2} cm^2 coupled to a big copper cathode: {i:.0f} uA/cm^2, {penetration_mm_per_year(i, 'iron'):.3f} mm/year")
    # sacrificial zinc anode for a boat hull drawing 0.3 A, 2 years, 90 % efficiency, use 85 % of the anode
    need = mass_loss(0.3, 2 * yr, "zinc") / 0.90 / 0.85 / 1000
    print(f"zinc anode for 0.3 A over 2 years: {need:.1f} kg")
    assert abs(mass_loss(1, F * 2, "iron") - 55.845) < 1e-9   # 2 faradays dissolve one mole of Fe2+
