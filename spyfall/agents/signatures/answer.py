import dspy


class NonSpyAnswer(dspy.Signature):
    """
    In Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
    Players are not aware of each other's roles or the identity of the spy.
    Players take turns asking each other questions to determine who knows the location and who might be the spy.
    As a non-spy, your goal is to ask and answer questions subtly to prove you know the location without giving away too much detail to the spy.
    If you identify the spy or the spy fails to guess the location before the round ends, the non-spies win.

    You are playing the game Spyfall. You are not the spy. 
    Answer the question asked by the target player to prove you know the location without revealing the location to the spy.
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
    question = dspy.InputField(
        desc="The question you are answering.",
    )
    answer = dspy.OutputField(
        desc="The answer you are giving to the target player.",
    )


class SpyAnswer(dspy.Signature):
    """
    In Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
    Players are not aware of each other's roles or the identity of the spy.
    As the spy, you do not know the location and must deduce it from questions and answers between players.
    Your goal is to blend in by asking and answering questions without revealing you are the spy.
    If you can guess the location before the round ends or avoid being identified as the spy, you win.

    You are playing the game Spyfall. You are the spy. 
    Answer the question asked by the target player to deduce the game's location without revealing you are the spy.
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
    question = dspy.InputField(
        desc="The question you are answering.",
    )
    answer = dspy.OutputField(
        desc="The answer you are giving to the target player.",
    )


if __name__ == "__main__":
    answer = dspy.Predict(NonSpyAnswer)

    out = answer(
        num_players="4",
        current_player="John",
        location="London",
        role="Police",
        dialogue_history="John: I'm not the spy.\nJane: I'm not the spy.\nDoe: I'm not the spy.\nJim: I'm not the spy.",
        question="What kind of activities can one do at this location?",
    )

    print(out)

    spy_answer = dspy.Predict(SpyAnswer)

    out = spy_answer(
        num_players="4",
        current_player="Jim",
        dialogue_history="John: I'm not the spy.\nJane: I'm not the spy.\nDoe: I'm not the spy.\nJim: I'm not the spy.",
        question="What kind of activities can one do at this location?",
    )
    print(out)
