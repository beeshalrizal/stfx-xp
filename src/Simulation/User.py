from typing import List

# from Environment import Environment
from Simulation.helpers.stv import createSTV
from Simulation.helpers.xp_calculator import runCalculator


class User:
    # Variables
    pnl: int = 0
    funds: int = 0
    num_vaults: int = 0
    achievementXP: int = 5000  # default to 5000
    stfx_staked: int = 0

    # XP data
    xp: int = 5000
    xp_history: List[int] = None

    # histories
    pnl_history: List[int] = None
    funds_history: List[int] = None

    def __init__(self) -> None:
        if self.xp_history is None:
            self.xp_history = []

        if self.pnl_history is None:
            self.pnl_history = []

        if self.funds_history is None:
            self.funds_history = []

        return

    def sim(self, env: "Environment", num_samples: int) -> "User":
        newSTV = createSTV(self.xp, env, num_samples)

        # set vals from stv
        self.pnl = self.pnl + newSTV["pnl"]
        self.funds = self.funds + newSTV["funds"]
        self.num_vaults = self.num_vaults + 1
        self.achievementXP = self.simAchievements()

        # update vals
        new_xp = self.calcNewXP()
        self.xp = new_xp
        self.xp_history.append(new_xp)

        self.pnl_history.append(newSTV["pnl"])
        self.funds_history.append(newSTV["funds"])

        return self

    """
        This is where the XP formula exists...
        P = PNL
        F = Funds Raised
        N = Number of vaults deployed
        A = Achievement XP
        S = $STFX staked
    """

    def calcNewXP(self):
        xp = runCalculator(
            self.pnl, self.funds, self.num_vaults, self.achievementXP, self.stfx_staked
        )
        # print("XP", xp)
        # print(
        #     "pnl, funds, vaults, achievements, staked",
        #     self.pnl,
        #     self.funds,
        #     self.num_vaults,
        #     self.achievementXP,
        #     self.stfx_staked,
        # )
        return xp

    # since the first achievements are easy, let's just give them 5k each vault until they get to 20k
    def simAchievements(self) -> int:
        if self.num_vaults > 3:
            return self.achievementXP

        return self.achievementXP + 5000

    def simSTFX(self) -> int:
        return 0
