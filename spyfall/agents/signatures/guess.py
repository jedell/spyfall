import dspy
from spyfall.agents import prompts

class Guess(dspy.Signature):
    """
    In the social deduction game Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
    Players are not aware of each other's roles or the identity of the spy.
    As the spy, you do not know the location and must deduce it from questions and answers between players.
    Your goal is to blend in by asking and answering questions without revealing you are the spy.
    If you can guess the location before the round ends or avoid being identified as the spy, you win.

    You are playing the game Spyfall. You are the spy. 
    Based on the dialogue history and the list of locations, guess the location of the game. If correct, you win.
    """

    num_players = dspy.InputField(
        desc="The number of players in the game.",
    )
    current_player = dspy.InputField(
        desc="Your identity.",
    )
    dialogue_history = dspy.InputField(
        desc="The dialogue history between players.",
    )
    locations = dspy.InputField(
        desc="The list of possible locations in the game.",
    )
    guess = dspy.OutputField(
        desc="Your guess of the game's location.",
    )


if __name__ == "__main__":
    guess = dspy.Predict(Guess)

    out = guess(
        num_players="4",
        current_player="John",
        dialogue_history="John: I'm not the spy.\nJane: I'm not the spy.\nDoe: I'm not the spy.\nJim: I'm not the spy.",
        locations="London, Paris, New York, Tokyo",
    )

    print(out)
