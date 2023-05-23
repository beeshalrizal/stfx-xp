from Simulation.User import User
from typing import List

from Simulation.helpers.seed_generator import getPnlPctgSeed, getFundsPctgSeed

# The number of samples
NUM_SAMPLES = 1000


class Environment:
    pnlPctgSeed: List[int] = []
    fundsPctgSeed: List[int] = []

    users: List[User] = []

    def __init__(self) -> None:
        self.createSeeds()

    def createUser(self) -> User:
        new_user = User()
        self.users.append(new_user)
        return new_user

    def simulate(self) -> None:
        for user in self.users:
            user.sim(self, NUM_SAMPLES)

    def createSeeds(self) -> None:
        self.pnlPctgSeed = getPnlPctgSeed(NUM_SAMPLES)
        self.fundsPctgSeed = getFundsPctgSeed(NUM_SAMPLES)
        return
