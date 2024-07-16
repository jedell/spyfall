import torch
import torch.nn as nn
import torch.nn.functional as F
from tensordict.nn import TensorDictModule
from torchrl.envs.libs.pettingzoo import PettingZooWrapper


class CriticNetwork(nn.Module):
    def __init__(self, input_dim, hidden_dim, n_agents):
        super(CriticNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, n_agents)
        self.value_head = nn.Linear(n_agents, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        value = self.value_head(x)
        return value
    
def init_critic_module(env: PettingZooWrapper, n_agents: int, observation_dim: int) -> nn.Module:
    critic_net = CriticNetwork(
        input_dim=observation_dim,
        hidden_dim=observation_dim*2,
        n_agents=n_agents
    )

    critic_module = TensorDictModule(
        module=critic_net,
        in_keys=[("agent_0", "observation")],
        out_keys=[("agent_0", "state_value")]
    )

    return critic_module