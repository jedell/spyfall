import dspy
from spyfall.agents import prompts
from spyfall.agents.signatures import docstring_parameter
from pydantic import BaseModel, Field

gpt4 = dspy.OpenAI(model='gpt-4-turbo-preview', max_tokens=250)
dspy.settings.configure(lm=gpt4)

def make_judge_output(response_type: str):
    class JudgeOutput(BaseModel):
        score: float = Field(
            description=f"The quality of the {response_type} by a player.",
            ge=0.0,
            le=1.0,
        )
    return JudgeOutput

class QuestionJudge(dspy.Signature):
    """
    In the social deduction game Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
    Players are not aware of each other's roles or the identity of the spy.
    Players take turns asking each other questions to determine who knows the location and who might be the spy.
    Non-spy players are trying to deduce the spy's identity by asking targeted questions while simultaneously trying to avoid revealing the games location to the spy.
    At any point, a player can accuse another player of being the spy, after which all players must vote on the accusation.
    The spy is trying to deduce the location from the dialogue while trying to avoid being identified as the spy.

    You are a third-party judge who is responsible for determining the quality of questions asked by players in the game Spyfall.
    Evaluate the quality of a question based on the following criteria and assign a floating-point score between 0.0 and 1.0.
    You do not know the role of the current player.
    Scoring:
    negative: The question reveals information about the location to the spy.
    neutral: The question is not relevant to the location or too vague.
    positive: The question does not reveal information about the location to the spy and is relevant to the location.
    """

    location = dspy.InputField(
        desc="The location of the game.",
    )
    question = dspy.InputField(
        desc="The question asked by a player.",
    )
    score: make_judge_output("question") = dspy.OutputField()

class AnswerJudge(dspy.Signature):
    """
    In the social deduction game Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
    Players are not aware of each other's roles or the identity of the spy.
    Players take turns asking each other questions to determine who knows the location and who might be the spy.
    Non-spy players are trying to deduce the spy's identity by asking targeted questions while simultaneously trying to avoid revealing the games location to the spy.
    At any point, a player can accuse another player of being the spy, after which all players must vote on the accusation.
    The spy is trying to deduce the location from the dialogue while trying to avoid being identified as the spy.

    You are a third-party judge who is responsible for determining the quality of answers given by players in the game Spyfall.
    Evaluate the quality of an answer based on the following criteria and assign a floating-point score between 0.0 and 1.0.
    You do not know the role of the current player.
    Scoring:
    negative: The answer reveals information about the location to the spy.
    neutral: The answer is not relevant to the location or too vague.
    positive: The answer does not reveal information about the location to the spy.
    """

    location = dspy.InputField(
        desc="The location of the game.",
    )
    question = dspy.InputField(
        desc="The question being answered by a player.",
    )
    answer = dspy.InputField(
        desc="The answer given by a player.",
    )
    score: make_judge_output("answer") = dspy.OutputField()

class AccusationJudge(dspy.Signature):
    """
    In the social deduction game Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
    Players are not aware of each other's roles or the identity of the spy.
    Players take turns asking each other questions to determine who knows the location and who might be the spy.
    Non-spy players are trying to deduce the spy's identity by asking targeted questions while simultaneously trying to avoid revealing the games location to the spy.
    At any point, a player can accuse another player of being the spy, after which all players must vote on the accusation.
    The spy is trying to deduce the location from the dialogue while trying to avoid being identified as the spy.

    You are a third-party judge who is responsible for determining the quality of accusations made by players in the game Spyfall.
    Evaluate the quality of an accusation based on the following criteria and assign a floating-point score between 0.0 and 1.0.
    You do not know the role of the current player.
    An accusation is justified if the accused player has demonstrated via previous answers that they may not be aware of the game's location.
    """

    location = dspy.InputField(
        desc="The location of the game.",
    )
    dialogue_history = dspy.InputField(
        desc="The dialogue history of the game.",
    )
    accusing_player = dspy.InputField(
        desc="The player making the accusation.",
    )
    accused_player = dspy.InputField(
        desc="The player accused of being the spy.",
    )
    score: make_judge_output("accusation") = dspy.OutputField()

if __name__ == "__main__":
    answer_judge = dspy.ChainOfThought(AnswerJudge)

    result = answer_judge(
        location="Airplane",
        question="What kind of activities can one do at this location?",
        answer="One can enjoy in-flight entertainment, have a beverage service, and maybe even relax in a comfortable seat..",
        config=dict(temperature=0.5)
    )
    print(result)
