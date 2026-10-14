"""
The Mandelbrot Set — infinite complexity from one line of algebra

For each complex number c, iterate z -> z^2 + c starting from 0. If the orbit
stays bounded, c belongs to the Mandelbrot set; if it escapes to infinity, it
does not. This single quadratic rule produces one of mathematics' most intricate
objects — a fractal whose boundary is infinitely detailed at every scale, a
visual gateway to complex dynamics and chaos.
"""

from __future__ import annotations


def escape_time(c: complex, max_iter: int = 100) -> int:
    """Iterations until |z| > 2 (escape), or max_iter if it stays bounded."""
    z = 0j
    for i in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return i
    return max_iter


def render(width: int = 70, height: int = 28, max_iter: int = 100,
           x_min: float = -2.4, x_max: float = 0.8,
           y_min: float = -1.2, y_max: float = 1.2) -> str:
    palette = " .:-=+*#%@"
    lines = []
    for row in range(height):
        y = y_min + (y_max - y_min) * row / (height - 1)
        line = []
        for col in range(width):
            x = x_min + (x_max - x_min) * col / (width - 1)
            n = escape_time(complex(x, y), max_iter)
            if n == max_iter:
                line.append("@")                     # inside the set
            else:
                line.append(palette[n * (len(palette) - 1) // max_iter])
        lines.append("".join(line))
    return "\n".join(lines)


if __name__ == "__main__":
    print("The Mandelbrot set (escape-time rendering)\n")
    print(render())

    print("\nMembership test (z -> z^2 + c, bounded => in the set):")
    for c in (0 + 0j, -1 + 0j, 0.3 + 0.5j, 1 + 1j):
        n = escape_time(c)
        verdict = "in set" if n == 100 else f"escapes at iter {n}"
        print(f"  c = {c!s:>9}: {verdict}")
    print("\n  The boundary is a fractal — infinitely detailed at every zoom.")
