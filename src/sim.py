import datetime
import matplotlib.pyplot as plt

from Simulation.Environment import Environment
from numpy import mean, std, median, arange, array, percentile

"""
    Simulation Settings
"""
NUM_USERS = 50000
NUM_STVS = 150


def main():
    env = Environment()

    # generate num_users users in the environment
    for _ in range(NUM_USERS):
        env.createUser()

    # simulate the journeys of these users as they create num_stv stv's
    for j in range(NUM_STVS):
        print(f"running for stv {j}")
        env.simulate()

    # plot the output
    x = arange(1, NUM_STVS + 1)

    y = array(list(map(lambda u: u.xp_history, env.users)))
    # y = array(list(map(lambda u: u.pnl_history, env.users)))
    # y = array(list(map(lambda u: u.funds_history, env.users)))

    for i in range(NUM_USERS):
        plt.plot(x, y[i], alpha=0.1, color="blue")

    med = median(y, axis=0)
    q3 = percentile(y, 75, axis=0)
    q1 = percentile(y, 25, axis=0)

    plt.plot(x, med, alpha=1, color="red")
    plt.plot(x, q3, alpha=1, color="green")
    plt.plot(x, q1, alpha=1, color="green")

    # end = [item[-1] for item in y]
    # print('end', end)

    plt.show()

    ct = datetime.datetime.now()


if __name__ == "__main__":
    main()
