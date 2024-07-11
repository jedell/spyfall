import torch
from spyfall.environment.spyfall_env import init_env
from spyfall.train import init_policy_modules

seed = 0
torch.manual_seed(seed)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

frames_per_episode = 1_000
n_episodes = 10

env = init_env(num_players=4, device=device)

policy_modules = init_policy_modules(env=env)
