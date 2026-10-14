"""
Kalman Filter — optimal state estimation (the "sense" of a robot)

Every sensor is noisy. The Kalman filter fuses a motion model with noisy
measurements to track a system's hidden state (here position and velocity from
noisy position readings alone). It is the optimal linear estimator and the
workhorse of robot localization, navigation and tracking — predicting the state
forward, then correcting it by the measurement, weighted by their uncertainties.
"""

from __future__ import annotations

import random


# ---- minimal matrix helpers (lists of lists) ----
def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def transpose(a):
    return [list(row) for row in zip(*a)]


def mat_add(a, b):
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def mat_sub(a, b):
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def identity(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def kalman_step(x, P, z, F, H, Q, R):
    """One predict-update cycle. z is a scalar position measurement."""
    # Predict.
    x = mat_mul(F, x)
    P = mat_add(mat_mul(mat_mul(F, P), transpose(F)), Q)
    # Update.
    y = [[z - mat_mul(H, x)[0][0]]]                       # innovation (1x1)
    S = mat_add(mat_mul(mat_mul(H, P), transpose(H)), R)  # innovation cov (1x1)
    K = mat_mul(mat_mul(P, transpose(H)), [[1.0 / S[0][0]]])  # gain (2x1)
    x = mat_add(x, mat_mul(K, y))
    P = mat_mul(mat_sub(identity(2), mat_mul(K, H)), P)
    return x, P


if __name__ == "__main__":
    random.seed(1)
    dt, true_v, meas_std, steps = 1.0, 1.0, 4.0, 50

    F = [[1, dt], [0, 1]]              # constant-velocity motion model
    H = [[1, 0]]                       # we observe position only
    Q = [[0.001, 0], [0, 0.001]]      # small process noise
    R = [[meas_std ** 2]]             # measurement noise

    x = [[0.0], [0.0]]                # initial state estimate
    P = [[10.0, 0], [0, 10.0]]        # initial uncertainty

    meas_err2 = est_err2 = 0.0
    print("Kalman filter tracking position from noisy measurements\n")
    print(f"  {'t':>3}  {'true':>7}  {'measured':>9}  {'estimate':>9}")
    for t in range(1, steps + 1):
        true_pos = true_v * t
        z = true_pos + random.gauss(0, meas_std)
        x, P = kalman_step(x, P, z, F, H, Q, R)
        est = x[0][0]
        meas_err2 += (z - true_pos) ** 2
        est_err2 += (est - true_pos) ** 2
        if t % 10 == 0:
            print(f"  {t:>3}  {true_pos:>7.2f}  {z:>9.2f}  {est:>9.2f}")

    print(f"\n  RMSE of raw measurements: {(meas_err2 / steps) ** 0.5:.2f}")
    print(f"  RMSE of Kalman estimate : {(est_err2 / steps) ** 0.5:.2f}")
    print(f"  estimated velocity      : {x[1][0]:.3f}  (true {true_v})")
    print("\nThe filter is far more accurate than the sensor it listens to.")
