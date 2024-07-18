import dspy
from spyfall.agents import prompts


class NonSpyQuestion(dspy.Signature):
    f"""
    {prompts.spyfall_rules_non_spy}

    You are playing the game Spyfall. You are not the spy. 
    Ask a question to the target player to deduce if they are the spy without revealing the location.
    """

    num_players = dspy.InputField(
        desc="The number of players in the game.",
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
        desc="The player you are asking a question to.",
    )
    question = dspy.OutputField(
        desc="The question you are asking the target player.",
    )


class SpyQuestion(dspy.Signature):
    f"""
    {prompts.spyfall_rules_spy}

    You are playing the game Spyfall. You are the spy. 
    Ask a question to the target player to deduce the game's location.
    """
    num_players = dspy.InputField(
        desc="The number of players in the game.",
    )
    location = dspy.InputField(
        desc="The location of this round. Known to all players, except the spy.",
    )
    dialogue_history = dspy.InputField(
        desc="The dialogue history between players.",
    )
    target = dspy.InputField(
        desc="The player you are asking a question to.",
    )
    question = dspy.OutputField(
        desc="The question you are asking the target player.",
    )


if __name__ == "__main__":
    question = dspy.Predict(NonSpyQuestion)

    out = question(
        num_players="4",
        location="London",
        role="Police",
        dialogue_history="John: I'm not the spy.\nJane: I'm not the spy.\nDoe: I'm not the spy.\nSpy: I'm not the spy.",
        target="Spy",
    )

    print(out)