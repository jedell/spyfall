import dspy

class NonSpyAccusation(dspy.Signature):
    """
    In Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
    Players are not aware of each other's roles or the identity of the spy.
    Players take turns asking each other questions to determine who knows the location and who might be the spy.
    As a non-spy, your goal is to identify the spy by observing their answers and behavior.
    If you identify the spy or the spy fails to guess the location before the round ends, the non-spies win.

    You are playing the game Spyfall. You are not the spy.
    Accuse the target player of being the spy and provide reasoning based on their previous answers and behavior.
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
        desc="The player you are accusing of being the spy.",
    )
    accusation_reasoning = dspy.OutputField(
        desc="The reasoning behind why you are accusing the target player of being the spy.",
    )


class SpyAccusation(dspy.Signature):
    """
    In Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
    Players are not aware of each other's roles or the identity of the spy.
    As the spy, you do not know the location and must deduce it from questions and answers between players.
    Your goal is to blend in by asking and answering questions without revealing you are the spy.
    If you can guess the location before the round ends or avoid being identified as the spy, you win.

    You are playing the game Spyfall. You are the spy.
    Accuse the target player of being the spy and provide reasoning based on their previous answers and behavior to deflect suspicion from yourself.
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
    target = dspy.InputField(
        desc="The player you are accusing of being the spy.",
    )
    accusation_reasoning = dspy.OutputField(
        desc="The reasoning behind why you are accusing the target player of being the spy.",
    )
