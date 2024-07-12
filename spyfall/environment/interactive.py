import numpy as np
import torch
from spyfall.environment.spyfall_env import init_env

def interactive_simulation(env):
    env.reset()
    player = env.agent_selection = np.random.choice(list(env.agents))
    print(f"Player: {player}")
    while True:
        current_agent = env.agent_selection
        if current_agent == player:
            print(f"\nCurrent Agent: {current_agent}")
            print(f"Dialogue History: {env.dialogue_history}")
        
            action_mask = env.action_masks[current_agent]
            action_types = ["Ask Question", "Answer Question", "Make Accusation", "Vote", "Spy Guesses Location"]
            for action_type in range(action_mask.shape[0]):
                for target_agent in range(action_mask.shape[1]):
                    if action_mask[action_type, target_agent] == 1:
                        print(f"{action_type}: {action_types[action_type]} -> Target Agent {target_agent}")

            action_type = int(input("Select an action type: "))
            target_agent = int(input(f"Select a target agent (0 to {env.num_players - 1}): "))

            action = np.full((5, env.num_players), -np.inf)
            action[action_type, target_agent] = 1

        observations, rewards, terminations, truncations, infos = env.step(action)

        if all(terminations.values()):
            print("Game over!")
            break

        print(f"Observations: {observations}")
        print(f"Rewards: {rewards}")
        print(f"Terminations: {terminations}")
        print(f"Truncations: {truncations}")

if __name__ == "__main__":
    num_players = 4
    observation_dim = 128
    device = torch.device('cpu')

    env = init_env(num_players, observation_dim, device, wrapped=False)

    interactive_simulation(env)