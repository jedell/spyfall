spyfall_rules_judge = """
In the social deduction game Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
Players are not aware of each other's roles or the identity of the spy.
Players take turns asking each other questions to determine who knows the location and who might be the spy.
Non-spy players are trying to deduce the spy's identity by asking targeted questions while simultaneously trying to avoid revealing the games location to the spy.
At any point, a player can accuse another player of being the spy, after which all players must vote on the accusation.
The spy is trying to deduce the location from the dialogue while trying to avoid being identified as the spy.
"""

spyfall_rules_spy = """
In Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
Players are not aware of each other's roles or the identity of the spy.
As the spy, you do not know the location and must deduce it from questions and answers between players.
Your goal is to blend in by asking and answering questions without revealing you are the spy.
If you can guess the location before the round ends or avoid being identified as the spy, you win.
"""

spyfall_rules_non_spy = """
In Spyfall, each player receives a card showing the same location and a location-based role except one, who receives the role of the spy.
Players are not aware of each other's roles or the identity of the spy.
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