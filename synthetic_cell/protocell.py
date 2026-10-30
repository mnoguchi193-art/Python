"""
Protocell Growth and Division (原始細胞の成長と分裂) — a membrane-geometry
model

Before genes and enzymes, life may have begun as self-reproducing lipid
vesicles (protocells).  A vesicle grows by absorbing amphiphiles into its
membrane (surface area A) and by taking up solutes/water (volume V).  The
key insight (Bozic & Svetina; Chen & Szostak) is purely geometric:

  * a sphere of volume V needs surface area  A_sphere = (36*pi)^(1/3) * V^(2/3),
  * two spheres of volume V/2 need  2^(1/3)  times that area.

So when a vesicle has accumulated enough *excess* membrane to cover two
smaller spheres, it can split in two with no membrane left over — a
spontaneous division driven by surface-to-volume imbalance.

No external libraries; forward Euler integration of the growth laws.
"""

from __future__ import annotations
import math

CBRT_36PI = (36 * math.pi) ** (1 / 3)      # sphere area = CBRT_36PI * V^(2/3)
DIVISION_FACTOR = 2 ** (1 / 3)             # area for two half-spheres / one sphere


def sphere_area(volume: float) -> float:
    return CBRT_36PI * volume ** (2 / 3)


def reduced_area(area: float, volume: float) -> float:
    """area / (area of a sphere with the same volume); 1.0 = perfect sphere."""
    return area / sphere_area(volume)


class Protocell:
    def __init__(self, volume: float):
        self.volume = volume
        self.area = sphere_area(volume)    # start spherical

    def can_divide(self) -> bool:
        return reduced_area(self.area, self.volume) >= DIVISION_FACTOR

    def divide(self) -> tuple["Protocell", "Protocell"]:
        child = Protocell(self.volume / 2)  # two equal spherical daughters
        return child, Protocell(self.volume / 2)


def grow_one_cycle(cell: Protocell, k_area: float, k_vol: float, dt: float
                   ) -> tuple[int, float]:
    """Grow until the cell can divide. Return (#steps, reduced area reached)."""
    steps = 0
    while not cell.can_divide():
        cell.area += k_area * cell.area * dt       # membrane uptake ~ area
        cell.volume += k_vol * cell.volume * dt    # slower volume growth
        steps += 1
        if steps > 100000:
            break
    return steps, reduced_area(cell.area, cell.volume)


# ── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Division criterion: a vesicle can split in two once its membrane")
    print(f"  exceeds the spherical minimum by a factor of {DIVISION_FACTOR:.4f}")
    print(f"  (= 2^(1/3), the area of two half-volume spheres).\n")

    # Membrane area must grow faster than volume for excess membrane to build.
    # Equal exponential rates: over the time needed to build 2^(1/3)
    # excess membrane (area ~ V^(2/3)), the volume doubles exactly, so
    # each daughter returns to its parent's birth size — a stable cycle.
    k_area, k_vol, dt = 0.04, 0.04, 0.1
    cell = Protocell(volume=1.0)
    print(f"Start: V={cell.volume:.3f}, A={cell.area:.3f}, "
          f"reduced area={reduced_area(cell.area, cell.volume):.3f} (sphere)\n")

    print("Growth-division cycles (one daughter followed each time):")
    print("  cycle   steps   V at division   reduced area")
    for c in range(1, 7):
        steps, ra = grow_one_cycle(cell, k_area, k_vol, dt)
        v_div = cell.volume
        cell, _sibling = cell.divide()
        print(f"  {c:3d}     {steps:5d}   {v_div:10.3f}     {ra:.4f}")

    print("\n  Membrane area outpaces the area a sphere of that volume needs, so")
    print("  the vesicle becomes non-spherical and divides on reaching 2^(1/3).")
    print("  With area and volume growing at matched rates the division volume")
    print("  holds steady — a primitive, gene-free reproduction cycle from")
    print("  geometry alone.")
