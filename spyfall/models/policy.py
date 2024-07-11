import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class SpyfallPolicyNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, num_game_actions, num_players):
        super(SpyfallPolicyNetwork, self).__init__()
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
    
if __name__ == "__main__":
    policy_network = SpyfallPolicyNetwork(input_size=10, hidden_size=10, num_game_actions=5, num_players=4)

    observation = torch.rand((1,10))
    print(observation)
    action_values = policy_network(observation)
    print(action_values)
    

