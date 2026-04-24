import numpy as np
from doubledqn_agent import plot_results

r = np.load("ddqn_results/rewards.npy")
s = np.load("ddqn_results/survivals.npy")
e = np.load("ddqn_results/eliminations.npy")
l = np.load("ddqn_results/losses.npy")
ep = np.load("ddqn_results/epsilons.npy")

plot_results(list(r), list(s), list(e), list(l), list(ep), "ddqn_results")