from spyfall.models import GameState, Player

def initialize_game(players):
    """
    Initializes the game with a list of players, selects a spy, and assigns a location.
    """
    pass

def start_round(game_state):
    """
    Starts a new round by resetting necessary state variables.
    """
    pass

def ask_question(game_state):
    """
    Handles the logic for a player asking a question to another player.
    """
    current_player = game_state.players[game_state.current_player_idx]
    if current_player.is_ai:
        question, next_player_idx = current_player.engine.ask_question(game_state)
        print(f"{current_player.name} asks: {question}")
        game_state.current_player_idx = next_player_idx
        game_state.prev_asker_idx = game_state.current_player_idx
        game_state.history.add_action("question", {"asker": current_player.name, "question": question})
    else:
        # Handle human player asking a question
        question, 

def answer_question(game_state):
    """
    Handles the logic for a player answering a question.
    """
    answering_player = game_state.players[game_state.current_player_index]
    if answering_player.is_ai:
        answer = answering_player.engine.answer_question(game_state)
        print(f"{answering_player.name} answers: {answer}")
        game_state.history.add_action("answer", {"answerer": answering_player.name, "answer": answer})
    else:
        # Handle human player answering a question
        pass

def initiate_indictment(game_state):
    """
    Loop through players in game state, each player makes
    a decision if they want to start an indictment against another player
    If a player decides to indict another player, that player is selected as the suspect.

    If multiple players decide to indict the same player, the game state is set to a draw.
    If multiple players decide to indict different players, we resolve an order in which the
    indictment votes occur.
    """
    for player in game_state.players:
        if player.is_ai:
            player.engine.initiate_indictment(game_state)
        else:
            # Handle human player initiating an indictment
            pass

def resolve_indictments(game_state):
    """
    Resolves the indictments by voting.
    """
    for indictment_player_idx in game_state.indictments:
        target = game_state.players[indictment_player_idx]
        for player in game_state.players:
            if player.is_ai:
                game_state.votes[player.name] = player.engine.vote(game_state, target)
            else:
                # Handle human player resolving an indictment
                pass
        
        # check round end conditions
        if len(game_state.votes) == len(game_state.players):
            if all(vote for vote in game_state.votes.values()):
                game_state.game_over = True
                if game_state.spy == target:
                    # non-spy wins
                    game_state.winner = target
                else:
                    # spy wins
                    game_state.winner = game_state.spy
            else:
                # indictment failed
                game_state.indictments = set()

        game_state.votes = {}
    game_state.indictments = set()


def spy_guess_location(game_state):
    """
    Allows the spy to guess the location. Ends the round if the guess is correct.
    """
    pass

def check_round_end_conditions(game_state):
    """
    Checks if the round should end based on time left, a successful indictment, or a correct guess by the spy.
    """
    pass

def update_game_state(game_state):
    """
    Updates the game state based on actions taken during the round.
    """
    pass

def game_loop(config):
    """
    The main game loop that keeps the game running until it's over.
    """
    game_state = GameState().from_config(config)
    initialize_game(game_state.players)
    
    while not game_state.game_over:
        start_round(game_state)
        for _ in range(game_state.rounds):
            ask_question(game_state)
            answer_question(game_state)

            initiate_indictment(game_state)


            check_round_end_conditions(game_state)
            update_game_state(game_state)
        # Additional logic to check if the game should continue or end
        game_state.game_over = True

from spyfall.utils import load_game_config

config = load_game_config("config/game1.yaml")

game_loop(config)

