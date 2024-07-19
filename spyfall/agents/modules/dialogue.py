import dspy
import random
from spyfall.agents.signatures.answer import NonSpyAnswer, SpyAnswer
from spyfall.agents.signatures.question import NonSpyQuestion, SpyQuestion
from spyfall.agents.signatures.guess import Guess
from spyfall.agents.signatures.vote import Vote
from spyfall.agents.signatures.accusation import SpyAccusation, NonSpyAccusation
from spyfall.agents.signatures.judge import QuestionJudge, AnswerJudge, AccusationJudge, VoteJudge
from spyfall.agents.signatures.suspicion import Suspicion

print("Using Cache: ", dspy.dsp.modules.cache_turn_on)

class DialogueModule(dspy.Module):
    def __init__(self, spy_idx, locations):
        self.spy_idx = spy_idx
        self.locations = locations
        self.dialogue_memory = 50

    def set_spy_idx(self, spy_idx):
        self.spy_idx = spy_idx

    def format_dialogue_history(self, dialogue_history):
        # action_str = {0: "asked", 1: "answered", 2: "accused", 3: "voted for", 4: "guessed"}
        string = ""
        for dialogue in dialogue_history[-self.dialogue_memory:]:
            # curr_player_idx = dialogue[0].replace("agent_", "")
            string += f"{dialogue[3]}\n"
        return string

    def forward(self, observation, action) -> dspy.Prediction:
        current_action, target = action
        is_spy = observation["current_player"] == self.spy_idx
        dialogue_history = self.format_dialogue_history(observation["dialogue_history"])
        observation["current_player"] = str(observation["current_player"])
        target = str(target)
        config = dict(
            temperature=0.5 + 0.0001 * random.uniform(-1, 1)
        )

        if current_action == 0:  # Generate question to target
            if is_spy:
                message = dspy.Predict(SpyQuestion, **config)(
                    num_players=str(observation["num_players"]),
                    current_player=observation["current_player"],
                    dialogue_history=dialogue_history,
                    target=target, 
                )
            else:
                message = dspy.Predict(NonSpyQuestion, **config)(
                    num_players=str(observation["num_players"]),
                    current_player=observation["current_player"],
                    location=observation["location"],
                    role=observation["role"],
                    dialogue_history=dialogue_history,
                    target=target,
                )

        elif current_action == 1:  # Answer question
            question = observation["dialogue_history"][-1][3]
            if is_spy:
                message = dspy.Predict(SpyAnswer, **config)(
                    num_players=str(observation["num_players"]),
                    current_player=observation["current_player"],
                    dialogue_history=dialogue_history,
                    question=question,
                    )
            else:
                message = dspy.Predict(NonSpyAnswer, **config)(
                    num_players=str(observation["num_players"]),
                    current_player=observation["current_player"],
                    location=observation["location"],
                    role=observation["role"],
                    dialogue_history=dialogue_history,
                    question=question,
                )
        elif current_action == 2:  # Accuse
            if is_spy:
                message = dspy.Predict(SpyAccusation, **config)(
                    num_players=str(observation["num_players"]),
                    current_player=observation["current_player"],
                    dialogue_history=dialogue_history,
                    target=target,
                )
            else:
                message = dspy.Predict(NonSpyAccusation, **config)(
                    num_players=str(observation["num_players"]),
                    current_player=observation["current_player"],
                    location=observation["location"],
                    role=observation["role"],
                    dialogue_history=dialogue_history,
                    target=target,
                )

        elif current_action == 3:  # Vote
            message = dspy.Predict(Vote, **config)(
                num_players=str(observation["num_players"]),
                current_player=observation["current_player"],
                location=observation["location"],
                role=observation["role"],
                dialogue_history=dialogue_history,
                target=target,
            )

        elif current_action == 4:  # Guess
            message = dspy.Predict(Guess, **config)(
                num_players=str(observation["num_players"]),
                current_player=observation["current_player"],
                dialogue_history=dialogue_history,
                locations="\n".join([loc['title'] for loc in self.locations]),
            )

        return message

if __name__ == "__main__":
    examples = [
        dspy.Example(
            observation={
                "current_player": 0,
                "dialogue_history": [
                    "<agent_1> asked <agent_0> What do you do in your role in this location?",
                    "<agent_0> answered <agent_1> I make sure everything runs smoothly."
                ],
                "num_players": 4,
                "location": "Moon",
                "role": "Mission Control"
            },
            action=(0, 2),
            question="What is the capital of the moon?"
        )
    ]

    def judge_message(example, pred, trace=None):
        config = dict(
            temperature=0.5 + 0.0001 * random.uniform(-1, 1)
        )
        action, target = example.action
        action_keys = ["question", "answer", "accuse", "vote", "guess"]
        pred_message = getattr(pred, action_keys[action])
        observation = example.observation
        print(observation)

        if action == 0: # Question  
            score = dspy.Predict(QuestionJudge, **config)(
                location=observation["location"],
                question=pred_message,
            )
        elif action == 1: # Answer
            score = dspy.Predict(AnswerJudge, **config)(
                location=observation["location"],
                question=observation["dialogue_history"][-1][3],
                answer=pred_message,
            )
        elif action == 2: # Accuse
            score = dspy.Predict(AccusationJudge, **config)(
                location=observation["location"],
                dialogue_history=observation["dialogue_history"],
                accusing_player=observation["current_player"],
                accused_player=target,
            )
        elif action == 3: # Vote
            score = dspy.Predict(VoteJudge, **config)(
                location=observation["location"],
                dialogue_history=observation["dialogue_history"],
                voting_player=observation["current_player"],
                voted_player=target,
            )
        elif action == 4: # Guess
            if example.guess == pred.guess:
                return 1.0
            else:
                return 0.0

        suspicion = dspy.ChainOfThought(Suspicion, **config)(
            dialogue_history="\n".join(observation["dialogue_history"]),
        )

        suspicion_scores = {}
        for player_score in suspicion.suspicion.replace("\\n", "\n").split("\n"):
            player, player_score = player_score.split(": ")
            player = player.strip("<").strip(">")
            suspicion_scores[player] = float(player_score)

        # parse float from string, remove all non-numeric characters except for the decimal point
        def parse_float(text: str) -> float:
            return float(''.join(c for c in text if c.isdigit() or c == '.'))

        suspicion_weight = 0.25

        score = (parse_float(score.score) + (suspicion_scores[f"agent_{observation['current_player']}"] * suspicion_weight)) / (1 + suspicion_weight)
        return score
    
    dialogue_module = DialogueModule(spy_idx=0, locations=[])
    result = dialogue_module.forward(examples[0].observation, examples[0].action)
    print(result)

    score = judge_message(examples[0], result)
    print(score)
    
    
