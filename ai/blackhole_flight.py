"""
Black-hole flight simulator — gravitational lensing by ray-traced geodesics
（ブラックホール・フライトシミュレーター: 光の測地線を積分してレンズ効果を可視化）

An observer flies toward a Schwarzschild (non-rotating, uncharged) black
hole. For every pixel of the view, this program traces a light ray
BACKWARDS from the eye out into the scene, integrating the actual null
geodesic of curved spacetime, and asks where that ray came from:

  - it spirals across the event horizon      → the pixel is black (the SHADOW)
  - it whips around and escapes to the sky    → the pixel shows the lensed
                                                background, bent by gravity

Because rays are bent, the background sky grid appears warped, and rays
that graze the photon sphere pile up into a bright ring at the shadow's
edge — the Einstein ring / photon ring that the Event Horizon Telescope
imaged for M87* in 2019. As the observer approaches, the shadow grows.

Physics (geometric units G = c = 1, Schwarzschild radius r_s = 1):
  - event horizon        r = r_s = 1
  - photon sphere        r = 1.5 r_s   (unstable circular light orbits)
  - critical impact param b_crit = 3*sqrt(3)/2 * r_s ≈ 2.598
    rays with b < b_crit are captured; b > b_crit escape; b = b_crit orbits
  - orbit equation       d²u/dφ² = (3/2) u² - u,   u = r_s / r
    (the (3/2)u² term is the general-relativistic correction to a
    straight line; drop it and rays go straight, with no shadow at all)

Simplifications: static observer at each radius (no infall Doppler shift),
no accretion disk, no gravitational redshift of brightness, ASCII output.
The geodesics themselves are exact — everything visual follows from them.
"""

from __future__ import annotations

import math
from typing import Optional

R_S = 1.0                          # event horizon radius (our unit of length)
B_CRIT = 1.5 * math.sqrt(3.0)      # critical impact parameter, 3*sqrt(3)/2 ≈ 2.598
PHOTON_SPHERE = 1.5 * R_S


# ── The physics: integrate one light ray's null geodesic ──────────────────


class RayOutcome:
    """Where a back-traced light ray ended up."""

    SHADOW = "shadow"   # fell through the horizon
    SKY = "sky"         # escaped to infinity
    RING = "ring"       # grazed the photon sphere, winding many times

    def __init__(self, kind: str, sky_angle: float = 0.0, winding: float = 0.0):
        self.kind = kind
        self.sky_angle = sky_angle   # asymptotic azimuth in the orbit plane
        self.winding = winding       # total angle swept (radians)


def trace_ray(impact: float, observer_r: float) -> RayOutcome:
    """Back-trace a ray of impact parameter `impact` from radius `observer_r`.

    Integrates u(φ) with RK4, where u = r_s / r. Returns whether the ray is
    captured by the hole, escapes to the sky (and at what azimuth), or winds
    around the photon sphere.
    """
    if impact <= 1e-9:
        # Aimed straight at the center: a radial ray, swallowed whole.
        return RayOutcome(RayOutcome.SHADOW)

    u = R_S / observer_r
    # First integral of the orbit equation fixes the initial slope from b:
    #   (du/dφ)² + u²(1 - u) = (r_s / b)²
    # The incoming ray moves inward (r shrinking, u growing) so du/dφ > 0.
    slope_sq = (R_S / impact) ** 2 - u * u * (1.0 - u)
    v = math.sqrt(slope_sq) if slope_sq > 0.0 else 0.0

    def deriv(u_: float, v_: float) -> tuple[float, float]:
        return v_, 1.5 * u_ * u_ - u_

    d_phi = 0.01
    phi = 0.0
    max_phi = 6.0 * math.pi          # cap winding to keep near-critical rays finite
    u_start = u
    while phi < max_phi:
        if u >= 1.0:                 # crossed the horizon (r <= r_s)
            return RayOutcome(RayOutcome.SHADOW, winding=phi)
        if v < 0.0 and u <= u_start:  # came back out past the observer's shell
            return RayOutcome(RayOutcome.SKY, sky_angle=phi, winding=phi)

        # RK4 step in phi
        k1u, k1v = deriv(u, v)
        k2u, k2v = deriv(u + 0.5 * d_phi * k1u, v + 0.5 * d_phi * k1v)
        k3u, k3v = deriv(u + 0.5 * d_phi * k2u, v + 0.5 * d_phi * k2v)
        k4u, k4v = deriv(u + d_phi * k3u, v + d_phi * k3v)
        u += (d_phi / 6.0) * (k1u + 2 * k2u + 2 * k3u + k4u)
        v += (d_phi / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
        phi += d_phi

    return RayOutcome(RayOutcome.RING, sky_angle=phi, winding=phi)


# ── Mapping pixels to rays, and rays to characters ────────────────────────


def impact_parameter(alpha: float, observer_r: float) -> float:
    """Impact parameter of a ray seen at angle `alpha` from the hole's center,
    for a static observer at `observer_r` (exact Schwarzschild relation)."""
    return observer_r * math.sin(alpha) / math.sqrt(1.0 - R_S / observer_r)


# brightness ramp from dark to bright
_RAMP = " .:-=+*#"


def shade(outcome: RayOutcome, azimuth: float) -> str:
    """Pick a character for a pixel from its ray's fate and screen azimuth."""
    if outcome.kind == RayOutcome.SHADOW:
        return " "
    # Rays that wound far around the photon sphere before escaping (or hit the
    # winding cap) form the bright photon ring hugging the shadow's edge.
    if outcome.kind == RayOutcome.RING or outcome.winding > 1.6 * math.pi:
        return "@"

    # Escaped to the sky: draw a celestial GRID so its lensing is visible.
    # Lines of constant sky-latitude (sky_angle) and longitude (azimuth) are
    # bright; between them the sky is dim. Bending warps the grid near the hole.
    lat = outcome.sky_angle
    lon = azimuth
    d_lat = math.pi / 8.0
    d_lon = math.pi / 8.0
    near_lat = abs((lat + d_lat / 2) % d_lat - d_lat / 2) < 0.06
    near_lon = abs((lon + d_lon / 2) % d_lon - d_lon / 2) < 0.05
    strong_lensing = outcome.winding > math.pi + 0.4   # secondary/ring images

    if near_lat and near_lon:
        return "+" if not strong_lensing else "*"
    if near_lat or near_lon:
        return "." if not strong_lensing else "="
    return " " if not strong_lensing else ":"


# ── Rendering a single view ───────────────────────────────────────────────


def render_frame(
    observer_r: float, fov_deg: float, rows: int = 21, cols: int = 61
) -> str:
    """Render the view toward the black hole from radius `observer_r`."""
    fov = math.radians(fov_deg)
    half = fov / 2.0
    # A 1-D table over alpha is enough: by symmetry the ray's fate depends
    # only on the angle from center, not the screen azimuth. Precompute it.
    samples = 900
    max_alpha = half * 1.45          # cover the screen corners
    table: list[RayOutcome] = []
    for i in range(samples + 1):
        alpha = max_alpha * i / samples
        b = impact_parameter(alpha, observer_r)
        table.append(trace_ray(b, observer_r))

    def lookup(alpha: float) -> RayOutcome:
        if alpha >= max_alpha:
            alpha = max_alpha
        return table[round(alpha / max_alpha * samples)]

    lines: list[str] = []
    for row in range(rows):
        # vertical angle, corrected for the ~2:1 height:width of a text cell
        y = (row / (rows - 1) - 0.5) * fov * (rows / cols) * 2.0
        chars: list[str] = []
        for col in range(cols):
            x = (col / (cols - 1) - 0.5) * fov
            alpha = math.hypot(x, y)
            azimuth = math.atan2(y, x)
            chars.append(shade(lookup(alpha), azimuth))
        lines.append("".join(chars))
    return "\n".join(lines)


def shadow_angular_radius_deg(observer_r: float) -> float:
    """Angular radius of the shadow's edge (critical ray) from the observer."""
    s = B_CRIT * math.sqrt(1.0 - R_S / observer_r) / observer_r
    return math.degrees(math.asin(min(1.0, s)))


# ── Demo: fly in toward the horizon ───────────────────────────────────────

if __name__ == "__main__":
    print("Black-hole flight simulator — Schwarzschild geodesic ray tracing")
    print("  '@' photon ring   '+*.=:' lensed sky grid   ' ' shadow (horizon)")
    print(f"  event horizon r_s = {R_S:.0f}, photon sphere r = {PHOTON_SPHERE:.1f},"
          f" b_crit = {B_CRIT:.3f}\n")

    FOV = 80.0
    for observer_r in (20.0, 10.0, 6.0, 4.0):
        shadow = shadow_angular_radius_deg(observer_r)
        print(f"── approaching: observer at r = {observer_r:.0f} r_s "
              f"({observer_r:.0f}x the horizon) ──")
        print(f"   shadow angular radius {shadow:.1f}°   (field of view {FOV:.0f}°)")
        print(render_frame(observer_r, FOV))
        print()

    print("Note: the shadow (b < b_crit ≈ 2.598) grows as we approach, the sky")
    print("grid warps around it, and rays grazing the photon sphere form the")
    print("bright '@' ring — the same structure the EHT imaged for M87* (2019).")
