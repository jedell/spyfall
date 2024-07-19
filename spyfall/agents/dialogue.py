from typing import List, Dict, Tuple
from spyfall.agents import prompts

class GeneratorInterface:

    def __init__(self):
        self.generation_fn = None

    def set_generation_fn(self, generation_fn):
        self.generation_fn = generation_fn

    def generate(self, prompt):
        """
        Wrapper function around LLM generation.
        """
        return self.generation_fn(prompt)

class DialogueAgent:
    def __init__(self, spy_idx, locations, generator):
        self.spy_idx = spy_idx
        self.locations = locations
        self.generator: GeneratorInterface = generator

    def set_spy_idx(self, spy_idx):
        self.spy_idx = spy_idx

    def format_dialogue_history(self, dialogue_history):
        action_str = {0: "asked", 1: "answered", 2: "accused", 3: "voted for", 4: "guessed"}
        string = ""
        for dialogue in dialogue_history:
            curr_player_idx = dialogue[0].replace("agent_", "")
            string += f"<Player {curr_player_idx}>: {action_str[dialogue[1]]} <Player {dialogue[2]}>: {dialogue[3]}\n"
        return string

    def forward(self, observation, action) -> str:
        """
        Generates messages based on the action and observation.
        observation: dict, dialogue_history: list, current_agent: int, location: str, role: str
        action: action taken by the current agent and the target agent of 
            the action, MultiDiscrete([num_actions, num_targets])
        returns: message
        """
        current_action, target = action
        is_spy = observation["current_player"] == self.spy_idx
        dialogue_history = ""
        
        if current_action == 0: # Generate question to target
            dialogue_history = self.format_dialogue_history(observation["dialogue_history"])

            if is_spy:
                prompt = prompts.spyfall_question_prompt_spy.format(
                    **{**observation, "dialogue_history": dialogue_history}, target=target
                )
            else:
                prompt = prompts.spyfall_question_prompt.format(
                    **{**observation, "dialogue_history": dialogue_history}, target=target
                )

            message = self.generate_response(prompt, "asked", observation["current_player"], target)
        elif current_action == 1: # Answer question

            # Get the question from the dialogue history
            if len(observation["dialogue_history"]) > 0:
                question = observation["dialogue_history"][-1][3]
                dialogue_history = self.format_dialogue_history(observation["dialogue_history"][:-1])

            if is_spy:
                prompt = prompts.spyfall_answer_prompt_spy.format(
                    **{**observation, "dialogue_history": dialogue_history}, target=target, question=question
                )
            else:
                prompt = prompts.spyfall_answer_prompt.format(
                    **{**observation, "dialogue_history": dialogue_history}, target=target, question=question
                )

            message = self.generate_response(prompt, "answered", observation["current_player"], target)

        elif current_action == 3: # vote
            # Analyze dialogue history and vote if accused player is spy or not
            dialogue_history = self.format_dialogue_history(observation["dialogue_history"])
            if is_spy:
                message = "No"
            else:
                prompt = prompts.vote_prompt_non_spy.format(
                    **{**observation, "dialogue_history": dialogue_history}, target=target
                )
                message = self.generate_response(prompt, "vote the following for", observation["current_player"], target)
                # find first Yes or No in message
                if "Yes" in message:
                    message = "Yes"
                elif "No" in message:
                    message = "No"
                else:
                    raise ValueError("Message does not contain Yes or No")
            
        elif current_action == 4: # guess
            
            dialogue_history = self.format_dialogue_history(observation["dialogue_history"])
            prompt = prompts.spyfall_guess_prompt.format(
                **{**observation, "dialogue_history": dialogue_history},
                target=target,
                locations="\n".join([loc['title'] for loc in self.locations])
            )
            message = self.generate_response(prompt, "guessed", observation["current_player"], target)

        return message
    
    def generate_response(self, prompt, action_type, current_player, target):
        """
        Returns the generated response.
        Performs some processing steps on the prompt and completion.
        """
        message_meta = f"You {action_type} <Player {target}>:"
        prompt_format = "{prompt}\n{message_meta}"
        return self.generator.generate(prompt_format.format(prompt=prompt, message_meta=message_meta))        


from openai import OpenAI
import os

# load .env
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class OpenAIGenerator(GeneratorInterface):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.set_generation_fn(self.generate_fn)

    def generate_fn(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
