from abc import ABC, abstractmethod
from spyfall.models import GameState

class BaseEngine(ABC):
    """
    Base class for all actions taken by players in Spyfall
    """

    @abstractmethod
    def question(self, game_state: GameState):
        pass

    def answer(self, player, question):
        pass

    def initiate_indictment(self, game_state) -> bool:
        pass

    def vote(self, game_state) -> bool:
        """
        Resolve games current indictment via voting if player thinks indicted
        player is the spy.
        """
        pass

class AIEngine(BaseEngine):
    def __init__(self):
        self.game_state_history = []  # Stores snapshots of the game state
        self.interaction_history = []  # Stores all player questions and answers

    def update_game_state(self, game_state):
        # Store a copy of the game state for historical analysis
        self.game_state_history.append(game_state)

    def record_interaction(self, interaction):
        # Record a question or answer interaction
        self.interaction_history.append(interaction)

    def question(self, game_state: GameState):
        # Analyze the game state and interaction history to generate a question
        previous_asker = game_state.prev_asker

        context = self._build_context(previous_asker, "question")
        question = self._call_llm(context)
        return question

    def answer(self, player, question):
        # Analyze the game state, interaction history, and the question to generate an answer
        context = self._build_context(player, "answer", question)
        answer = self._call_llm(context)
        return answer
    
    def initiate_indictment(self, game_state) -> bool:
        # Determine if the AI should initiate an indictment based on context
        context = self._build_context("indictment")
        question = self._call_llm(context)
        return question
    
    def vote(self, game_state, target) -> bool:
        # Determine AI vote for current indictment
        context = self._build_context("vote", target)
        vote = self._call_llm(context)
        return vote

    def _build_context(self, player, interaction_type, question=None):
        # Build a context string that includes game state, interaction history, and the current question if applicable
        context = f"Player: {player.name}, Interaction Type: {interaction_type}, Game State: {self.game_state_history[-1]}, Interaction History: {self.interaction_history}"
        if question:
            context += f", Current Question: {question}"
        return context

    def _call_llm(self, context):
        # Placeholder for calling the LLM with the context
        # This function should be implemented to interact with the chosen LLM API
        return "Generated response based on context"