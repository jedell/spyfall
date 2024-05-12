from typing import List
from spyfall.models import ActionHistory, Player

class GameState:
    def __init__(self):
        self.players: List[Player] = []
        self.spy = None
        self.location = None
        self.rounds = 0
        self.current_player_idx = 0
        self.game_over = False
        self.votes = {}
        self.indictments = set()
        self.prev_asker_idx = None

        self.history: ActionHistory = ActionHistory()

    def from_config(self, config):
        self.players = [
            Player(
                name=player_info['name'],
                is_ai=player_info.get('is_ai', False),
            ) for player_info in config['players']
        ]
        self.location = config.get('location')
        self.rounds = config.get('rounds', 1)
        return self