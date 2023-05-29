import numpy as np

"""
    P = PNL
    F = Funds Raised
    N = Number of vaults deployed
    A = Achievement XP
    S = $STFX staked
"""


def runCalculator(P: int, F: int, N: int, A: int, S: float) -> int:
    return _v2(P, F, N, A, S)


def _v1(P, F, N, A, S):
    return 100 * np.round(np.sqrt(min(F, 50000) * N), 0) + 0.5 * P + A + S


def _v2(P, F, N, A, S):
    return 50 * np.round(np.sqrt(min(F, 50000) * N), 0) + 0.5 * P + A + S


def _v3(P, F, N, A, S):
    return 75 * np.round(np.sqrt(min(F, 100000) * N), 0) + 0.5 * P + A + S


def _v4(P, F, N, A, S):
    return 50 * np.round(np.sqrt(min(F, 100000) * N), 0) + 0.5 * P + A + S
