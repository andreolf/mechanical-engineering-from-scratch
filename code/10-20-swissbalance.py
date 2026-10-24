"""Swiss seasonal electricity balance with clearly ASSUMED round-number data: monthly demand and supply, the winter gap,
and how much seasonal storage would close it. Illustrative only, not official statistics."""
import math

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def shape(amplitude, peak_month):
    """Twelve monthly weights averaging 1, with a cosine peak at peak_month (0 = January)."""
    return [1 + amplitude * math.cos(2 * math.pi * (m - peak_month) / 12) for m in range(12)]


def monthly(annual, amplitude, peak):
    return [annual / 12 * w for w in shape(amplitude, peak)]


# ASSUMED annual values, TWh (round numbers of roughly the right size for Switzerland)
DEMAND = monthly(60.0, 0.15, 0)           # winter peak
RUN_OF_RIVER = monthly(18.0, 0.45, 6)     # snowmelt in early summer
LAKE_INFLOW = monthly(20.0, 0.80, 6)      # natural inflow to storage lakes, mostly summer
NUCLEAR = monthly(18.0, 0.10, 0)          # refuelling outages in summer
OTHER = monthly(4.0, 0.0, 0)              # biomass, waste, wind


def balance(pv_twh, nuclear=True, lake_capacity=8.8):
    pv = monthly(pv_twh, 0.60, 6)
    nuc = NUCLEAR if nuclear else [0.0] * 12
    supply = [RUN_OF_RIVER[m] + LAKE_INFLOW[m] + nuc[m] + OTHER[m] + pv[m] for m in range(12)]
    net = [supply[m] - DEMAND[m] for m in range(12)]
    annual = sum(net)
    # storage that would shift every month's surplus to cover the deficits, with any annual shortfall imported evenly
    level, levels = 0.0, []
    for m in range(12):
        level += net[m] - annual / 12
        levels.append(level)
    storage_needed = max(levels) - min(levels)
    winter = sum(net[m] for m in (0, 1, 2, 9, 10, 11))
    return dict(net=net, annual=annual, storage=storage_needed, winter=winter, beyond_lakes=max(0.0, storage_needed - lake_capacity),
                supply=supply, levels=levels)


if __name__ == "__main__":
    assert abs(sum(DEMAND) - 60.0) < 1e-9 and abs(sum(LAKE_INFLOW) - 20.0) < 1e-9
    for label, kw in (("today-like: nuclear, 6 TWh PV", dict(pv_twh=6)), ("no nuclear, 6 TWh PV", dict(pv_twh=6, nuclear=False)),
                      ("no nuclear, 24 TWh PV", dict(pv_twh=24, nuclear=False)), ("no nuclear, 34 TWh PV", dict(pv_twh=34, nuclear=False))):
        r = balance(**kw)
        print(f"{label}: annual net {r['annual']:+.2f} TWh, winter half {r['winter']:+.2f} TWh, "
              f"seasonal storage needed {r['storage']:.2f} TWh ({r['beyond_lakes']:.2f} beyond the 8.8 TWh of lakes)")
        # the balance closes: supply + imports - exports = demand, and the storage level returns to its start
        assert abs(sum(r['supply']) - r['annual'] - sum(DEMAND)) < 1e-9 and abs(r['levels'][-1]) < 1e-9
    r = balance(24, nuclear=False)
    print("month   net TWh   storage level TWh")
    for m in range(12):
        print(f"  {MONTHS[m]}  {r['net'][m]:+6.2f}   {r['levels'][m]:+6.2f}")
