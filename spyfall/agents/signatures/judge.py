import dspy
from spyfall.agents import prompts

class QuestionJudge(dspy.Signature):
    f"""
    {prompts.spyfall_rules_judge}

    You are a third-party judge who is responsible for determining the quality of questions asked by players in the game Spyfall.
    Evaluate the quality of a question based on the following criteria and assign a floating-point score.
    The score should be between 0 and 1, where 0 is the lowest quality and 1 is the highest quality.
    You do not know the role of the current player.
    Evaluation Criteria:
    - Does the question indicate the asker is aware of the location?
    - Does the question reveal too much information about the location to the spy?
    - Does the question reveal enough information to non-spy players to confirm the asker is not the spy?
    """

    question = dspy.InputField(
        desc="The question asked by a player.",
    )
    score = dspy.OutputField(
        desc="The quality of the question asked by a player.",
    )

class AnswerJudge(dspy.Signature):
    f"""
    {prompts.spyfall_rules_judge}

    You are a third-party judge who is responsible for determining the quality of answers given by players in the game Spyfall.
    Evaluate the quality of an answer based on the following criteria and assign a floating-point score.
    The score should be between 0 and 1, where 0 is the lowest quality and 1 is the highest quality.
    You do not know the role of the current player.
    Evaluation Criteria:
    - Does the answer confirm the asker is not the spy?
    - Does the answer reveal too much information about the location to the spy?
    - Does the answer reveal enough information to non-spy players to confirm the asker is not the spy?
    - Is the answer an effective response to the question in the context of the game?
    """

    question = dspy.InputField(
        desc="The question being answered by a player.",
    )
    answer = dspy.InputField(
        desc="The answer given by a player.",
    )
    score = dspy.OutputField(
        desc="The quality of the answer given by a player.",
    )