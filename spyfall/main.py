import torch
import numpy as np
from spyfall.environment.spyfall_env import init_env
from spyfall.models.policy import init_policy_modules
from spyfall.models.critic import init_critic_module
from tensordict.nn import TensorDictSequential
from torchrl.modules import (
    ProbabilisticActor,
    TanhDelta,
)
from torchrl.collectors import SyncDataCollector
from torchrl.data.replay_buffers import ReplayBuffer
from torchrl.data.replay_buffers.samplers import SamplerWithoutReplacement
from torchrl.data.replay_buffers.storages import LazyTensorStorage


seed = 0
torch.manual_seed(seed)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

frames_per_episode = 1_000
n_episodes = 10
n_agents = 4
observation_dim = 768

env = init_env(
    num_players=n_agents,
    observation_dim=observation_dim,
    device=device
)
print(env.action_spec["agent_0"]["action"].shape)
policy_modules = init_policy_modules(
    env=env,
    n_agents=n_agents,
    observation_dim=observation_dim
)

policies = {}
print(env.full_action_spec["agent_0"]["action"])
for group, _ in env.group_map.items():
    policy = ProbabilisticActor(
        module=policy_modules[group],
        spec=env.full_action_spec[group, "action"],
        in_keys=[(group, "param")],
        out_keys=[(group, "action")],
        distribution_class=TanhDelta,
        distribution_kwargs={
            "min": -1,
            "max": 1,
        },
        return_log_prob=True,
        log_prob_key=(group, "sample_log_prob")
    )
    policies[group] = policy

reset_td = env.reset()
for group, _agents in env.group_map.items():
    out = policies[group](reset_td)
    print(
        f"Running value and policy for group '{group}':",
        out,
    )
    print(out[group, "action"])

agent_policies = TensorDictSequential(
    *policies.values()
)

collector = SyncDataCollector(
    env,
    agent_policies,
    device=device,
    frames_per_batch=frames_per_episode,
    total_frames=frames_per_episode * n_episodes,
)

replay_buffer = ReplayBuffer(
    storage=LazyTensorStorage(
        frames_per_episode, device=device
    ),
    sampler=SamplerWithoutReplacement(),
    batch_size=1,
)

critic = init_critic_module(env, n_agents, observation_dim)


print("Running policy:", policy(env.reset()))
print("Running value:", critic(env.reset()))