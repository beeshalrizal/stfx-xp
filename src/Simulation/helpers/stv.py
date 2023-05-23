import numpy as np
from Simulation.helpers.seed_generator import getPnlPctgSeed
from random import randint
from typing import TypedDict

STV = TypedDict("STV", {"funds": int, "pnl": int})


def createSTV(xp: int, env: "Environment", num_samples: int) -> STV:
    value = _stvValue(xp)

    fundsPctg = _fundsPctg(env, num_samples)
    funds = np.round(np.multiply(fundsPctg / 100, value))

    pnlPctg = _pnlPctg(env, num_samples)
    pnl = np.round(np.multiply(pnlPctg / 100, funds))

    return {"funds": funds, "pnl": pnl}


def _stvValue(xp: int) -> int:
    return randint(np.round(xp / 2, 0), np.round(xp, 0))


def _pnlPctg(env: "Environment", num_samples: int) -> float:
    return env.pnlPctgSeed[randint(0, num_samples - 1)]


def _fundsPctg(env: "Environment", num_samples: int) -> float:
    return env.fundsPctgSeed[randint(0, num_samples - 1)]
