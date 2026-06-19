"""
Spike Detection — the front-end of a brain-computer interface

An implanted BCI like Neuralink records the extracellular voltage near neurons.
Buried in noise are the sharp deflections of action potentials ("spikes"). The
first job of any neural decoder is to find them: threshold the voltage, respect a
refractory window so one spike isn't counted twice, and turn the messy analog
trace into a clean spike train. Those spike rates are what a decoder then turns
into intent (see cognitive_neuroscience/population_decoding.py).

This module synthesizes a noisy recording with known spikes and recovers them,
scoring detection precision and recall.
"""

from __future__ import annotations

import math
import random
from statistics import pstdev


def generate_recording(duration: float = 1.0, fs: int = 10_000, rate: float = 40,
                       noise_std: float = 0.15, seed: int = 0
                       ) -> tuple[list[float], list[int], int]:
    """Synthesize extracellular voltage. Returns (signal, true spike indices, fs)."""
    rng = random.Random(seed)
    n = int(duration * fs)
    signal = [rng.gauss(0, noise_std) for _ in range(n)]
    template = [-math.exp(-((i - 5) ** 2) / 8) for i in range(15)]  # ~1.5 ms dip
    truth = []
    i = 0
    while i < n:
        if rng.random() < rate / fs:
            truth.append(i)
            for j, val in enumerate(template):
                if i + j < n:
                    signal[i + j] += val
            i += len(template)        # don't overlap spikes
        else:
            i += 1
    return signal, truth, fs


def detect_spikes(signal: list[float], fs: int, k: float = 4.0,
                  refractory_ms: float = 2.0) -> tuple[list[int], float]:
    """Detect spikes by negative threshold crossing with a refractory window."""
    threshold = -k * pstdev(signal)
    refractory = int(refractory_ms * fs / 1000)
    spikes, last = [], -refractory
    for i, v in enumerate(signal):
        if v < threshold and i - last > refractory:
            spikes.append(i)
            last = i
    return spikes, threshold


def score(detected: list[int], truth: list[int], fs: int,
          tol_ms: float = 1.0) -> tuple[float, float]:
    """Precision and recall, matching detections to true spikes within tol."""
    tol = int(tol_ms * fs / 1000)
    remaining = truth[:]
    hits = 0
    for d in detected:
        match = next((t for t in remaining if abs(t - d) <= tol), None)
        if match is not None:
            hits += 1
            remaining.remove(match)
    precision = hits / len(detected) if detected else 0.0
    recall = hits / len(truth) if truth else 0.0
    return precision, recall


if __name__ == "__main__":
    signal, truth, fs = generate_recording()
    detected, threshold = detect_spikes(signal, fs)
    precision, recall = score(detected, truth, fs)

    print("Neural spike detection (synthetic electrode recording)\n")
    print(f"  sampling rate     : {fs:,} Hz, 1.0 s of data")
    print(f"  detection threshold: {threshold:.3f} (4 sigma below baseline)\n")
    print(f"  true spikes       : {len(truth)}")
    print(f"  detected spikes   : {len(detected)}")
    print(f"  precision         : {precision:.1%}  (detections that were real)")
    print(f"  recall            : {recall:.1%}  (real spikes found)")
    print(f"  estimated firing rate: {len(detected)} Hz "
          f"(true {len(truth)} Hz)")
    print("\n  Clean spike trains extracted from noise — the signal-processing")
    print("  front-end every brain-computer interface depends on.")
