import dspy

class Vote(dspy.Signature):
    """
    In Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
    Players are not aware of each other's roles or the identity of the spy.
    Players take turns asking each other questions to determine who knows the location and who might be the spy.
    As a non-spy, your goal is to ask and answer questions subtly to prove you know the location without giving away too much detail to the spy.
    If you identify the spy or the spy fails to guess the location before the round ends, the non-spies win.

    You are playing the game Spyfall. You are not the spy. 
    Based on the dialogue history, vote if you think the target player is the spy. Answer with "Yes" or "No".
    """

    num_players = dspy.InputField(
        desc="The number of players in the game.",
    )
    current_player = dspy.InputField(
        desc="Your identity.",
    )
    location = dspy.InputField(
        desc="The location of this round. Known to all players, except the spy.",
    )
    role = dspy.InputField(
        desc="Your role in the location.",
    )
    dialogue_history = dspy.InputField(
        desc="The dialogue history between players.",
    )
    target = dspy.InputField(
        desc="The player you are voting for.",
    )
    vote = dspy.OutputField(
        desc="Your vote on whether the target player is the spy. Answer with 'Yes' or 'No'.",
    )


if __name__ == "__main__":
    vote = dspy.Predict(Vote)

    out = vote(
        num_players="4",
        current_player="John",
        location="London",
        role="Police",
        dialogue_history="John: I'm not the spy.\nJane: I'm not the spy.\nDoe: I'm not the spy.\nJim: I'm not the spy.",
        target="Jane",
    )

    print(out)
