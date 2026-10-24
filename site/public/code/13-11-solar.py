"""Solar geometry and clear-sky yield: sun position from declination and hour angle, checked against the noon formula and the analytic daily extraterrestrial total."""
import math

GSC = 1361.0  # solar constant, W/m^2


def declination(n):
    """Cooper's formula, degrees, day of year n."""
    return 23.45 * math.sin(math.radians(360 * (284 + n) / 365))


def elevation(lat, n, solar_hour):
    phi, d, w = math.radians(lat), math.radians(declination(n)), math.radians(15 * (solar_hour - 12))
    return math.degrees(math.asin(math.sin(phi) * math.sin(d) + math.cos(phi) * math.cos(d) * math.cos(w)))


def daily_horizontal(lat, n, clear_sky=False, steps=1440):
    """Daily energy on a horizontal square metre, kWh, by integrating over the day (1-minute steps).
    clear_sky: beam through the atmosphere by Meinel's model, DNI = 1353 * 0.7^(AM^0.678), plus 10% diffuse."""
    total = 0.0
    for i in range(steps):
        a = elevation(lat, n, (i + 0.5) * 24 / steps)
        if a <= 0: continue
        s = math.sin(math.radians(a))
        if clear_sky:
            am = 1 / s
            total += 1.1 * 1353 * 0.7 ** (am ** 0.678) * s
        else:
            total += GSC * s
    return total * 24 / steps / 1000


def daily_extraterrestrial_exact(lat, n):
    phi, d = math.radians(lat), math.radians(declination(n))
    ws = math.acos(max(-1.0, min(1.0, -math.tan(phi) * math.tan(d))))
    return 24 / math.pi * GSC * (math.cos(phi) * math.cos(d) * math.sin(ws) + ws * math.sin(phi) * math.sin(d)) / 1000


if __name__ == "__main__":
    places = {"Bali (Denpasar)": -8.65, "Zurich": 47.37}
    for name, lat in places.items():
        for n, label in ((172, "21 June"), (355, "21 December")):
            noon = elevation(lat, n, 12.0)
            peak = max(elevation(lat, n, 6 + i / 600) for i in range(7201))
            print(f"{name}, {label}: declination {declination(n):+.3f}, noon elevation {noon:.3f} deg (90 - |lat - decl| = {90 - abs(lat - declination(n)):.3f})")
            assert abs(noon - (90 - abs(lat - declination(n)))) < 1e-9 and abs(peak - noon) < 1e-6
            assert abs(daily_horizontal(lat, n) - daily_extraterrestrial_exact(lat, n)) < 1e-3
    yearly = {}
    for name, lat in places.items():
        yearly[name] = sum(daily_horizontal(lat, n, clear_sky=True, steps=288) for n in range(1, 366))
        print(f"{name}: clear-sky yearly total on a horizontal panel {yearly[name]:.0f} kWh/m^2; a 20% panel makes {0.2*yearly[name]:.0f} kWh/m^2")
    jun, dec = daily_horizontal(47.37, 172, True), daily_horizontal(47.37, 355, True)
    print(f"Zurich clear-sky day: June {jun:.3f} kWh/m^2, December {dec:.3f} kWh/m^2 (ratio {jun/dec:.2f}); Bali June {daily_horizontal(-8.65, 172, True):.3f}, December {daily_horizontal(-8.65, 355, True):.3f}")
    assert yearly["Bali (Denpasar)"] > 1.2 * yearly["Zurich"] and jun / dec > 5
