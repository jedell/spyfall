"""
Spyfall Environment for multi-agent social deduction game.
"""
import requests
import json
import random
from typing import List, Union

import torch
import numpy as np
from gymnasium.spaces import Box
from torchrl.envs.libs.pettingzoo import PettingZooWrapper
from pettingzoo import AECEnv

from spyfall.agents.modules.dialogue import DialogueModule
from spyfall.agents.dialogue import DialogueAgent, OpenAIGenerator, OPENAI_API_KEY

class SpyfallAgent(AECEnv):
    metadata = {
        "name": "Spyfall Agent",
        "description": "Agent for the Spyfall game.",
    }


class SpyfallEnv(AECEnv):
    metadata = {
        "name": "Spyfall",
        "description": "Multi-agent social deduction game.",
    }

    def __init__(self, num_players, observation_dim, locations: List[dict]=None):
        super().__init__()
        self.num_players = num_players
        self.observation_dim = observation_dim
        self.locations = locations
        self.location = None
        self.roles = None
        self.timestep = None
        self.possible_agents = [f"agent_{i}" for i in range(num_players)]
        self.agents = self.possible_agents
        self.suspicions = None
        self.accused_agent = None
        self.votes = None
        self.spy_idx = None
        self.infos = None
        self.rewards = None
        self.terminations = None
        self.truncations = None
            
        # self.dialogue_agent = DialogueAgent(self.spy_idx, locations, OpenAIGenerator(OPENAI_API_KEY))
        self.dialogue_agent = DialogueModule(self.spy_idx, locations)
        self.dialogue_history = None
        self.player_message = None

        # observation space is encoded dialogue history
        self.observation_spaces = {
            a: Box(low=-np.inf, high=np.inf, shape=(self.observation_dim,))
            for a in self.possible_agents
        }

        self.action_spaces = {
            a: Box(
                low=-np.inf,
                high=np.inf,
                shape=(5, self.num_players)
            )  # 5 action types, num_players target agents
            for a in self.possible_agents   
        }
 
        self.action_masks = {}
        self.agent_selection = self.possible_agents[0]

    def set_player_message(self, message):
        self.player_message = message

    def _select_location(self):
        return random.choice(self.locations)
    
    def _outer_product(self, action_mask, agent_mask):
        return np.outer(action_mask, agent_mask)

    def _update_action_masks(self, action_type, last_agent, last_target, next_agent):
        agent_mask = np.zeros((self.num_players), dtype=np.int8)
        last_agent = self.agents.index(last_agent)

        if action_type == 0:  # Question asked
            # only allow answering directed at last agent
            agent_mask[last_agent] = 1
            action_mask = np.array([0, 1, 0, 0, 0], dtype=np.int8)     
            self.action_masks[next_agent] = self._outer_product(action_mask, agent_mask)

        elif action_type == 1:  # Question answered
            if next_agent == self.spy_idx:
                # only allow asking questions
                agent_mask = np.ones((self.num_players), dtype=np.int8)
                agent_mask[last_agent] = 0
                action_mask = np.array([1, 0, 1, 0, 1], dtype=np.int8)
                self.action_masks[next_agent] = self._outer_product(action_mask, agent_mask)
            else:
                # only allow asking questions
                # invert agent mask instaed of creating new array
                agent_mask = np.ones((self.num_players), dtype=np.int8)
                agent_mask[last_agent] = 0
                action_mask = np.array([1, 0, 1, 0, 0], dtype=np.int8)
                self.action_masks[next_agent] = self._outer_product(action_mask, agent_mask)
        elif action_type == 2:  # Accusation made
            # only allow voting
            agent_mask[self.accused_agent] = 1
            action_mask = np.array([0, 0, 0, 1, 0], dtype=np.int8)
            self.action_masks = {a: self._outer_product(action_mask, agent_mask) for a in self.agents}  # Only allow voting
        elif action_type == 3:  # Vote
            # only allow voting
            agent_mask[self.accused_agent] = 1
            action_mask = np.array([0, 0, 0, 1, 0], dtype=np.int8)
            self.action_masks = {a: self._outer_product(action_mask, agent_mask) for a in self.agents}  # Only allow voting
        elif action_type == 4:  # Spy guesses location
            # only allow guessing
            agent_mask[int(next_agent.replace("agent_", ""))] = 1
            action_mask = np.array([0, 0, 0, 0, 1], dtype=np.int8)
            self.action_masks = {a: self._outer_product(action_mask, agent_mask) for a in self.agents}  # Only allow guessing
        else:
            raise ValueError(f"Invalid action type: {action_type}")

    def _initiate_voting(self, accused_agent: Union[int, str]):
        self.votes = {a: None for a in self.agents}
        self.accused_agent = int(accused_agent.replace("agent_", "")) if isinstance(accused_agent, str) else accused_agent

    def _process_vote(self, voting_agent, vote):
        self.votes[voting_agent] = 1 if vote == "Yes" else 0
        if all(vote is not None for vote in self.votes.values()):
            return self._tally_votes()

    # alternative round ending: 
    # https://en.wikipedia.org/wiki/Spyfall_(card_game)#End_of_the_round
    def _tally_votes(self):
        # Exclude the spy's vote from the tally
        non_spy_votes = {agent: vote for agent, vote in self.votes.items() if agent != self.spy_idx}
        if all(vote == 1 for vote in non_spy_votes.values()):
            if self.accused_agent == self.spy_idx:
                print("Spy identified! Non-spies win.")
                # TODO reward agents
                return "non-spy-win"
            else:
                print("Wrong accusation! Spy wins.")
                # TODO reward agents
                return "spy-win"
                
        else:
            print("Not unanimous. Continue game.")
            return "continue"

    def _process_spy_guess(self, spy_agent, guess):
        assert spy_agent == self.spy_idx
        if self.location in guess:
            return True
        else:
            return False

    def _assign_roles(self, roles: List[str]):
        # assign a random role to an agent, with one role being the spy
        agent_roles = {}
        for agent in self.agents:
            agent_roles[agent] = random.choice(roles)
            roles.remove(agent_roles[agent])
        self.spy_idx = random.choice(self.agents)
        agent_roles[self.spy_idx] = "spy"
        self.dialogue_agent.set_spy_idx(self.spy_idx)
        print(f"Agent roles: {agent_roles}")
        return agent_roles

    def reset(self, seed=None):
        location_and_roles = self._select_location()
        print("Location: ", location_and_roles["title"])

        self.location = location_and_roles["title"]
        self.agents = self.possible_agents
        self.roles = self._assign_roles(location_and_roles["roles"])
        self.timestep = 0

        self.dialogue_history = []
        self.votes = {a: None for a in self.agents}
        self.accused_agent = None
        # starting ction mask for each agent is ask question
        action_mask = np.array([1, 0, 0, 0, 0], dtype=np.int8)
        for i, a in enumerate(self.agents):
            agent_mask = np.ones((self.num_players), dtype=np.int8)
            agent_mask[i] = 0
            outer_product = np.outer(action_mask, agent_mask)
            self.action_masks[a] = outer_product

        encoded_dialogue_history = torch.rand(self.observation_dim)
        self.observations = {a: {
            "observation": encoded_dialogue_history,
            # "action_mask": self.action_masks[a]
        } for a in self.agents}
        # self.observations = {a: encoded_dialogue_history for a in self.agents}

        self.infos = {a: 
            # {}
            {"action_mask": self.action_masks[a]} 
            for a in self.agents 
        }
        self.rewards = {a: 0 for a in self.agents}
        self.terminations = {a: False for a in self.agents}
        self.truncations = {a: False for a in self.agents}

        return self.observations, self.infos
    
    def _next_voting_agent(self):
        return next((a for a in self.agents if self.votes[a] is None), None)
    
    def _set_next_agent(self, agent: Union[int, str]):
        if isinstance(agent, int):
            self.agent_selection = self.agents[agent]
        else:
            self.agent_selection = agent

    def add_dialogue_history(self, current_agent, action_type, target_agent, dialogue):
        self.dialogue_history.append((current_agent, action_type, target_agent, dialogue))

    def handle_action(self, current_agent, action_type, target_agent, dialogue_template: str):
        if self.player_message is not None:
            message = self.player_message
        else:
            message = self.dialogue_agent.forward(
                {
                    "current_player": current_agent, 
                    "num_players": self.num_players, 
                    "location": self.location, 
                    "role": self.roles[current_agent], 
                    "dialogue_history": self.dialogue_history
                },
                [action_type, target_agent]
            )
            message = getattr(message, message.keys()[0])

        dialogue = dialogue_template.format(current_agent=current_agent, target_agent=target_agent, message=message)
        self.add_dialogue_history(current_agent, action_type, target_agent, dialogue)

        return message
    
    def _get_current_action(self, action: np.ndarray):
        """
        action is a numpy array of shape (len(action_types), len(self.agents))
        Current action is coordinate of max value in action array
        """
        action_type, target_agent = np.unravel_index(np.argmax(action), action.shape)
        return action_type, target_agent
    
    def _apply_action_mask(self, action_mask, action):
        return np.where(action_mask == 1, action, -np.inf)

    def step(self, action):
        self.timestep += 1
        current_action = action
        current_agent = self.agent_selection
        self.rewards = {a: 0 for a in self.agents}
        self.terminations = {a: False for a in self.agents}
        self.truncations = {a: False for a in self.agents}
        result = None
        
        current_action = self._apply_action_mask(self.action_masks[current_agent], current_action)
        action_type, target_agent = self._get_current_action(current_action)
        target_agent = self.agents[target_agent]
        if action_type == 0:  # Question asked
            # check to see if target_agent was target of last dialogue
            if len(self.dialogue_history) > 0:
                last_target = self.dialogue_history[-1][2]
                if target_agent == last_target:
                    # TODO how to handle in policy?
                    print("Target agent was target of last dialogue. Sampling a random other last target.")
                    target_agent = random.choice([a for a in self.agents if a != last_target and a != current_agent])

            self.handle_action(current_agent, action_type, target_agent,
                "<Player {current_agent}> asked <Player {target_agent}>: {message}.")
            self._set_next_agent(target_agent)
        elif action_type == 1:  # Question answered
            self.handle_action(current_agent, action_type, target_agent,                       
                "<Player {current_agent}> answered <Player {target_agent}>: {message}.")
            self._set_next_agent(current_agent)
        elif action_type == 2:  # Accusation made
            self._initiate_voting(target_agent)
            self.add_dialogue_history(current_agent, action_type, target_agent,
                f"<Player {current_agent}> accused <Player {target_agent}> of being the spy.")
            self._set_next_agent(current_agent)
        elif action_type == 3:  # Vote
            vote = self.handle_action(current_agent, action_type, target_agent,
                "<Player {current_agent}> voted for <Player {target_agent}>: {message}.")
            result = self._process_vote(current_agent, vote)
            # get next agent that has not voted
            self._set_next_agent(self._next_voting_agent())
        elif action_type == 4:  # Spy guesses location
            guess = self.handle_action(current_agent, action_type, target_agent,
                "<Player {current_agent}> guessed: {message}.")
            
            spy_correct = self._process_spy_guess(current_agent, guess)
            if spy_correct:
                self.rewards = {a: 0 for a in self.agents}
                self.rewards[current_agent] = 1
                for a in [a for a in self.agents if a != current_agent]:
                    self.rewards[a] = -1
                self.terminations = {a: True for a in self.agents}
                self.truncations = {a: True for a in self.agents}
            else:
                self.rewards = {a: 0 for a in self.agents}
                self.rewards[current_agent] = -1
                for a in [a for a in self.agents if a != current_agent]:
                    self.rewards[a] = 1
                self.terminations = {a: True for a in self.agents}
                self.truncations = {a: True for a in self.agents}
            self._set_next_agent(current_agent)
        else:
            raise ValueError(f"Invalid action type: {action_type}")
        
        self._update_action_masks(action_type, current_agent, target_agent, self.agent_selection)

        # if majority of agents have voted or spy has guessed location, game is over
        if result in ["spy-win", "non-spy-win"]:
            # if a non-spy receives majority of votes, spy wins and game is over
            if result == "spy-win":
                self.rewards = {a: 0 for a in self.agents}
                self.rewards[self.spy_idx] = 1
                for a in [a for a in self.agents if a != self.spy_idx]:
                    self.rewards[a] = -1
                self.terminations = {a: True for a in self.agents}
                self.truncations = {a: True for a in self.agents}
            elif result == "non-spy-win":
                # spy gets a chance to guess location
                agent_mask = np.zeros((self.num_players), dtype=np.int8)
                agent_mask[self.spy_idx] = 1
                action_mask = np.array([0, 0, 0, 0, 1], dtype=np.int8)
                outer_product = np.outer(action_mask, agent_mask)
                self.action_masks[self.spy_idx] = outer_product
                self._set_next_agent(self.spy_idx)
        elif result == "continue":
            # reset votes
            self.votes = {a: None for a in self.agents}
            # select next agent
            self._set_next_agent(self.accused_agent)
            self.accused_agent = None
            # reset action masks
            action_mask = np.array([1, 0, 0, 0, 0], dtype=np.int8)
            for i, a in enumerate(self.agents):
                agent_mask = np.ones((self.num_players), dtype=np.int8)
                agent_mask[i] = 0
                outer_product = np.outer(action_mask, agent_mask)
                self.action_masks[a] = outer_product

        if self.timestep > 100:
            self.terminations = {a: True for a in self.agents}
            self.truncations = {a: True for a in self.agents}

        encoded_dialogue_history = torch.rand(self.observation_dim)
        self.observations = {a: encoded_dialogue_history for a in self.agents}
        self.observation = encoded_dialogue_history
        self.infos = {a: {
            "action_mask": self.action_masks[a],
        } for a in self.agents}

        self.log_step()

        return self.observations, self.rewards, self.terminations, self.truncations, self.infos

    def log_step(self):
        last_dialogue = self.dialogue_history[-1]
        dialogue = last_dialogue[3]
        print(f"[Step {self.timestep}]: '{dialogue}'")

    def render(self):
        pass

    def observation_space(self, agent):
        return self.observation_spaces[agent]
    
    def observe(self, agent):
        # TODO encoded dialogue history as vector
        encoded_dialogue_history = torch.rand((1, self.observation_dim))
        return encoded_dialogue_history

    def action_space(self, agent):
        return self.action_spaces[agent]

def init_env(num_players: int, observation_dim: int, device: torch.device, wrapped: bool=True) -> PettingZooWrapper:
    response = requests.get("https://raw.githubusercontent.com/PepsRyuu/spyfall/master/locations.json")
    locations= json.loads(response.text)['locations']

    env = SpyfallEnv(
        num_players=num_players,
        locations=locations,
        observation_dim=observation_dim
    )

    if wrapped:
        return PettingZooWrapper(
            env=env,
            use_mask=True,
            device=device,
            categorical_actions=False,
            shared_observation_space=True
        )
    else:
        return env

if __name__ == "__main__":
    max_steps = 10
    wrapped_env = init_env(num_players=4, device='cpu')
    wrapped_env.rollout(max_steps)

