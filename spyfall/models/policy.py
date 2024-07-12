from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from tensordict import TensorDict
from tensordict.nn import TensorDictModule
from torchrl.modules import MultiAgentMLP
from torchrl.envs.libs.pettingzoo import PettingZooWrapper
from torchrl.modules.models.utils import _reset_parameters_recursive


class AgentPolicyNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, num_game_actions, num_players):
        super(AgentPolicyNetwork, self).__init__()
        print("###",input_size, hidden_size, num_game_actions, num_players)
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.output_layer = nn.Linear(hidden_size, num_game_actions * num_players)
        self.num_game_actions = num_game_actions
        self.num_players = num_players

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        action_values = self.output_layer(x)
        action_values = action_values.view(-1, self.num_game_actions, self.num_players)
        return action_values

    def select_action(self, observation):
        action_values = self.policy_network(observation)
        flat_action_values = action_values.view(-1)
        max_index = torch.argmax(flat_action_values)
        action_type, target_agent = np.unravel_index(max_index, action_values.shape)
        return action_type, target_agent
    
class MultiAgentSpyfallNet(nn.Module):
    def __init__(
            self,
            env: PettingZooWrapper, 
            n_target_agents: int, 
            observation_dim: int
        ):
        super(MultiAgentSpyfallNet, self).__init__()
        self.n_target_agents = n_target_agents
        self.observation_dim = observation_dim

        self.spy_network = self._build_agent_network(env, n_target_agents)
        self.non_spy_network = self._build_agent_network(env, n_target_agents)

        # self.params = TensorDict.from_modules(
        #     *[spy_network, non_spy_network],
        #     as_module=True
        # )
        # print(self.params.keys())
        self.__dict__["_empty_net"] = self._build_agent_network(env, n_target_agents)

    @staticmethod
    def vmap_func_module(module, *args, **kwargs):
        def exec_module(params, *input):
            with params.to_module(module):
                return module(*input)

        return torch.vmap(exec_module, *args, **kwargs)

    def _build_agent_network(self, env: PettingZooWrapper, n_agents: int):
        return AgentPolicyNetwork(
            input_size=self.observation_dim,
            hidden_size=self.observation_dim * 2,
            num_game_actions=env.action_spec["agent_0"]["action"].shape[-2],
            num_players=env.action_spec["agent_0"]["action"].shape[-1]
        )
    
    def reset_parameters(self):
        """Resets the parameters of the model."""

        with self.params.to_module(self._empty_net):
            _reset_parameters_recursive(self._empty_net)

    def forward(self, *inputs: Tuple[torch.Tensor]) -> torch.Tensor:
        print(inputs[0].shape)

        if len(inputs) > 1:
            inputs = torch.cat([*inputs], -1)
        else:
            inputs = inputs[0]
        print(inputs.shape)

        # non-spys share params
        output = self.non_spy_network(inputs)

        print(output)
        return output


def init_policy_modules(env: PettingZooWrapper, n_agents: int, observation_dim: int):
    policy_modules = {}

    policy_network = MultiAgentSpyfallNet(
        env=env,
        n_target_agents=n_agents,
        observation_dim=observation_dim
    )

    for group, _ in env.group_map.items():
        policy_module = TensorDictModule(
            policy_network,
            in_keys=[(group, "observation")],
            out_keys=[(group, "param")]
        )
        policy_modules[group] = policy_module

    return policy_modules
    
if __name__ == "__main__":
    policy_network = AgentPolicyNetwork(
        input_size=10,
        hidden_size=10,
        num_game_actions=5,
        num_players=4
    )

    observation = torch.rand((1,10))
    print(observation)
    action_values = policy_network(observation)
    print(action_values)
    

