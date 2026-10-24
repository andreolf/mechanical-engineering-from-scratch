"""Coulomb friction: will a crate on a ramp slide or tip first? And a crate pushed sideways."""
import math


def ramp_event(theta_deg, mu, b, h):
    """Crate of width b and height h (centre of mass at the middle) on a ramp at theta.
    Slides when tan(theta) > mu; tips when the weight line passes the lower edge, tan(theta) > b / h."""
    t = math.tan(math.radians(theta_deg))
    slide, tip = t > mu, t > b / h
    if slide and tip:
        return "slides" if mu < b / h else "tips"          # whichever limit was reached first while tilting
    return "slides" if slide else "tips" if tip else "stays"


def critical_angle(mu, b, h):
    return math.degrees(math.atan(min(mu, b / h))), ("slide" if mu < b / h else "tip")


def push(W, mu, b, h_push):
    """Horizontal push at height h_push on a crate of width b resting on the floor.
    Force to slide: mu W. Force to tip about the front edge: W (b/2) / h_push. The smaller wins."""
    P_slide, P_tip = mu * W, W * b / 2 / h_push
    return (P_slide, "slides") if P_slide < P_tip else (P_tip, "tips")


if __name__ == "__main__":
    # a 0.6 m wide, 1.2 m tall fridge crate on a tilting truck ramp
    b, h = 0.6, 1.2
    for mu in (0.3, 0.6):
        ang, mode = critical_angle(mu, b, h)
        print(f"mu = {mu}: first event at {ang:.3f} deg, it will {mode}")
    assert critical_angle(0.3, b, h) == (math.degrees(math.atan(0.3)), "slide")
    assert critical_angle(0.6, b, h)[1] == "tip"
    # slides exactly when tan(theta) > mu (if tipping isn't first)
    mu = 0.3; th = math.degrees(math.atan(mu))
    assert ramp_event(th - 1e-6, mu, b, h) == "stays" and ramp_event(th + 1e-6, mu, b, h) == "slides"
    # pushing the crate: W = 900 N, mu = 0.4; low push slides, high push tips
    for hp in (0.3, 0.9):
        P, what = push(900, 0.4, b, hp)
        print(f"push at {hp} m: {P:.1f} N and it {what}")
    hp_crit = b / 2 / 0.4
    print(f"push higher than {hp_crit:.2f} m and it tips before it slides")
    assert push(900, 0.4, b, hp_crit - 0.01)[1] == "slides" and push(900, 0.4, b, hp_crit + 0.01)[1] == "tips"
