"""
The Landing Burn — how Starship sticks the landing ("hoverslam")

A returning booster like SpaceX's Starship falls under gravity and must arrive at
the pad with zero velocity. But its engines, even at minimum throttle, push harder
than the rocket's weight (thrust-to-weight ratio > 1), so it *cannot hover*. The
only solution is a "suicide burn": fall freely, then ignite at exactly the
altitude where the remaining distance equals the stopping distance,

    ignition altitude = v^2 / (2 * net deceleration),

so the rocket decelerates to a stop precisely at the ground. Ignite too late and
it craters; too early and it stops short and falls again. Timing is everything.
"""

from __future__ import annotations


G = 9.81


def ignition_altitude(speed: float, twr: float) -> float:
    """Altitude at which to start the burn to stop exactly at the ground."""
    net_decel = G * (twr - 1)
    return speed ** 2 / (2 * net_decel)


def simulate(h0: float, v0: float, twr: float, fixed_ignition: float | None = None,
             dt: float = 0.005) -> tuple[float, float]:
    """Drop from h0 at downward speed v0. Returns (ignition altitude, touchdown speed)."""
    net_decel = G * (twr - 1)
    h, v, ignited = h0, v0, False
    ignite_h = fixed_ignition if fixed_ignition is not None else 0.0
    while h > 0:
        if not ignited:
            trigger = (fixed_ignition if fixed_ignition is not None
                       else ignition_altitude(v, twr))
            if h <= trigger:
                ignited, ignite_h = True, h
        a = -net_decel if ignited else G        # accel of downward speed
        v += a * dt
        h -= v * dt
        if ignited and v <= 0:                  # stopped above ground -> hovers down? no thrust cut
            return ignite_h, 0.0
    return ignite_h, max(0.0, v)


if __name__ == "__main__":
    h0, v0, twr = 2000.0, 120.0, 2.5            # 2 km up, 120 m/s down, TWR 2.5

    print("Starship landing burn (hoverslam)\n")
    print(f"  start: {h0:.0f} m altitude, {v0:.0f} m/s descent, TWR {twr}")
    print(f"  engines give net deceleration {G * (twr - 1):.1f} m/s^2 "
          f"(cannot hover: TWR > 1)\n")

    ignite, touchdown = simulate(h0, v0, twr)
    print("  Optimal suicide burn:")
    print(f"    ignition altitude : {ignite:.0f} m")
    print(f"    touchdown speed   : {touchdown:.1f} m/s  (soft landing)\n")

    # Igniting too late: the burn can't arrest the fall in time.
    _, late = simulate(h0, v0, twr, fixed_ignition=200.0)
    print("  Igniting too late (fixed 200 m):")
    print(f"    touchdown speed   : {late:.1f} m/s  (crash)")
    print("\n  One shot, no hover — the engine must light at exactly the right")
    print("  height. That is why propulsive landing is a guidance problem.")
