"""
Motion scaling & tremor filtering / モーションスケーリングと手ぶれ除去

Two signature features of teleoperated surgical robots (e.g. master-slave
systems):

  * motion scaling — the surgeon's hand motion is scaled DOWN (e.g. 5:1), so a
    5 mm hand movement becomes a 1 mm instrument movement, improving precision.
  * tremor filtering — physiological hand tremor (~8-12 Hz) is removed with a
    low-pass filter so it never reaches the instrument.

Standard library only.
"""


class MotionScaler:
    """Scale incremental hand motion down to instrument motion."""

    def __init__(self, scale: float = 0.2) -> None:
        if scale <= 0:
            raise ValueError("scale must be positive")
        self.scale = scale

    def apply(self, delta: float) -> float:
        return delta * self.scale


class ExponentialFilter:
    """First-order low-pass (EMA): y_t = a*x_t + (1-a)*y_{t-1}.

    Smaller alpha -> heavier smoothing (more tremor removed, more lag).
    """

    def __init__(self, alpha: float = 0.3) -> None:
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self._y: float | None = None

    def update(self, x: float) -> float:
        if self._y is None:
            self._y = x
        else:
            self._y = self.alpha * x + (1 - self.alpha) * self._y
        return self._y


def process_stream(
    hand_positions: list[float], scale: float = 0.2, alpha: float = 0.3
) -> list[float]:
    """Filter tremor, then scale, producing the instrument-tip path."""
    smoother = ExponentialFilter(alpha)
    scaler = MotionScaler(scale)
    smoothed = [smoother.update(x) for x in hand_positions]
    # Scale incremental motion relative to the first smoothed sample.
    origin = smoothed[0]
    return [origin + scaler.apply(s - origin) for s in smoothed]


if __name__ == "__main__":
    # Intended slow drift from 0 to ~9, corrupted by an oscillating tremor.
    import math
    hand = [i * 0.5 + 1.5 * math.sin(i) for i in range(20)]
    instrument = process_stream(hand, scale=0.2, alpha=0.3)

    hand_range = max(hand) - min(hand)
    inst_range = max(instrument) - min(instrument)
    print(f"Hand path range:       {hand_range:.2f}")
    print(f"Instrument path range: {inst_range:.2f}  (tremor smoothed + scaled)")
    print("First 5 instrument samples:",
          [round(v, 3) for v in instrument[:5]])
