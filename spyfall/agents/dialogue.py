from typing import List, Dict, Tuple

spyfall_rules_spy = """
In Spyfall, each player except one receives a card showing the same location.
As the spy, you do not know the location and must figure it out by listening to the questions and answers.
Your goal is to blend in by asking and answering questions without revealing you are the spy.
If you can guess the location before the round ends or avoid being identified as the spy, you win.
"""

spyfall_rules_non_spy = """
In Spyfall, each player receives a card showing the same location except one, who is the spy.
Players take turns asking each other questions to determine who knows the location and who might be the spy.
As a non-spy, your goal is to ask and answer questions subtly to prove you know the location without giving away too much detail to the spy.
If you identify the spy or the spy fails to guess the location before the round ends, the non-spies win.
"""

spyfall_question_prompt = spyfall_rules_non_spy + """
You are playing a game of Spyfall with {num_players} players. You are <Player {current_player}>. 
You are not the spy. The location is {location} and your role is {role}.

Dialogue History:
{dialogue_history}

Ask a question to <Player {target}> to deduce if they are the spy without revealing the location.
"""

spyfall_question_prompt_spy = spyfall_rules_spy + """
You are playing a game of Spyfall with {num_players} players. You are <Player {current_player}>. 
You are the spy.

Dialogue History:
{dialogue_history}

Ask a question to <Player {target}> to deduce the game's location.
"""

spyfall_answer_prompt = spyfall_rules_non_spy + """
You are playing a game of Spyfall with {num_players} players. You are <Player {current_player}>. 
You are not the spy. The location is {location} and your role is {role}.

Dialogue History:
{dialogue_history}

<Player {target}> asked you: {question}

Answer the question as to subtly prove you're not the spy without revealing the location.
"""

spyfall_answer_prompt_spy = spyfall_rules_spy + """
You are playing a game of Spyfall with {num_players} players. You are <Player {current_player}>. 
You are the spy.

Dialogue History:
{dialogue_history}

<Player {target}> asked you: {question}

Answer the question without revealing yourself.
"""

vote_prompt_non_spy = spyfall_rules_non_spy + """
You are playing a game of Spyfall with {num_players} players. You are <Player {current_player}>. 
You are not the spy. The location is {location} and your role is {role}.

Dialogue History:
{dialogue_history}

It's time to vote. Based on the dialogue, do you think <Player {target}> is the spy? Answer with "Yes" or "No".
"""

spyfall_guess_prompt = spyfall_rules_spy + """
You are playing a game of Spyfall with {num_players} players. You are <Player {current_player}>. 
You are the spy.

Dialogue History:
{dialogue_history}

Locations:
{locations}

Based on the dialogue history and the list of locations, guess the location of the game, if correct, you win.
"""

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

    def act(self, observation, action) -> str:
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
                prompt = spyfall_question_prompt_spy.format(
                    **{**observation, "dialogue_history": dialogue_history}, target=target
                )
            else:
                prompt = spyfall_question_prompt.format(
                    **{**observation, "dialogue_history": dialogue_history}, target=target
                )

            message = self.generate_response(prompt, "asked", observation["current_player"], target)
        elif current_action == 1: # Answer question

            # Get the question from the dialogue history
            if len(observation["dialogue_history"]) > 0:
                question = observation["dialogue_history"][-1][3]
                dialogue_history = self.format_dialogue_history(observation["dialogue_history"][:-1])

            if is_spy:
                prompt = spyfall_answer_prompt_spy.format(
                    **{**observation, "dialogue_history": dialogue_history}, target=target, question=question
                )
            else:
                prompt = spyfall_answer_prompt.format(
                    **{**observation, "dialogue_history": dialogue_history}, target=target, question=question
                )

            message = self.generate_response(prompt, "answered", observation["current_player"], target)

        elif current_action == 3: # vote
            # Analyze dialogue history and vote if accused player is spy or not
            dialogue_history = self.format_dialogue_history(observation["dialogue_history"])
            if is_spy:
                message = "No"
            else:
                prompt = vote_prompt_non_spy.format(
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
            prompt = spyfall_guess_prompt.format(
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

if __name__ == "__main__":
    # Test
    class MockEnv:
        def __init__(self):
            self.spy_idx = 2

    generator = OpenAIGenerator(api_key=OPENAI_API_KEY)

    # mock class
    env = MockEnv()
    agent = DialogueAgent(env, generator)


    # Location: Beach
    # Player 0: Lifeguard
    # Player 1: Surfer
    # Player 2: Spy
    # Player 3: Sunbather
    test_dialogue_history_1 = [
        (0, 0, 1, "Do you visit this place often?"),
        (1, 1, 0, "Yes, I try to come here whenever I can."),
        (1, 0, 2, "Do you need any special skills to enjoy this place?"),
        (2, 1, 1, "Not really, it's pretty accessible to everyone."),
        (2, 0, 3, "What time of day do you prefer to be here?"),
        (3, 1, 2, "I like to come early in the morning."),
        (3, 0, 0, "What's the first thing you notice when you arrive?"),
        (0, 1, 3, "The view is always stunning."),
        (0, 0, 2, "Do you come here alone or with others?"),
        (2, 1, 0, "It depends, sometimes with friends, sometimes alone."),
        (2, 0, 1, "How do you usually get here?"),
        (1, 1, 2, "I drive and park nearby."),
        (1, 0, 3, "Is there anything you dislike about this place?"),
        (3, 1, 1, "Sometimes it can be too crowded for my taste."),
        (3, 0, 0, "What's a common sound you hear here?"),
        (0, 1, 3, "The sound of people having fun and some natural background noise."),
    ]

    # Location: Bank
    # Player 0: Armored Car Driver
    # Player 1: Manager
    # Player 2: Spy
    # Player 3: Teller
    test_dialogue_history_2 = [
        (0, 0, 1, "How busy does it get here?"),
        (1, 1, 0, "It can get pretty hectic, especially at certain times of the day."),
        (1, 0, 2, "Do you have to interact with many people here?"),
        (2, 1, 1, "Yes, quite a few people, actually."),
        (2, 0, 3, "What's the dress code like here?"),
        (3, 1, 2, "We dress formally; it's important to look professional."),
        (3, 0, 0, "Do you spend a lot of time inside this place?"),
        (0, 1, 3, "Not really, I'm in and out quite frequently."),
        (0, 0, 2, "What's a typical task you might perform here?"),
        (2, 1, 0, "I handle various transactions and assist customers."),
        (2, 0, 1, "What do you think is the most challenging part of being here?"),
        (1, 1, 2, "Ensuring everything runs smoothly and dealing with any issues that arise."),
        (1, 0, 3, "What's something you might carry with you during your workday?"),
        (3, 1, 1, "I usually have a lot of paperwork and sometimes cash."),
        (3, 0, 0, "Do you need any special equipment for your job?"),
    ]

    msg = agent.act({"current_player": 0, "num_players": 4, "location": "Beach", "role": "Lifeguard", "dialogue_history": test_dialogue_history_1}, [0, 1])
    print(msg)
    print("####")
    msg = agent.act({"current_player": 0, "num_players": 4, "location": "Bank", "role": "Armored Car Driver", "dialogue_history": test_dialogue_history_2}, [1, 3])
    print(msg)
