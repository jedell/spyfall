from typing import List, Dict

class Player:
    def __init__(self, name, is_ai=False, engine=None):
        self.name = name
        self.is_ai = is_ai  # Indicates if this player is controlled by an AI

class HistoryNode:
    def __init__(self, action_type, data, next_node=None, prev_node=None):
        self.action_type = action_type  # Type of action (e.g., "question", "answer", "vote_initiation", etc.)
        self.data = data  # Data associated with the action
        self.next = next_node  # Reference to the next node in the list
        self.prev = prev_node  # Reference to the previous node in the list

class ActionHistory:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_action(self, action_type, data):
        new_node = HistoryNode(action_type, data, None, self.tail)
        if self.tail:
            self.tail.next = new_node
        else:
            self.head = new_node
        self.tail = new_node

    def get_history(self):
        actions = []
        current_node = self.head
        while current_node:
            actions.append((current_node.action_type, current_node.data))
            current_node = current_node.next
        return actions

    def get_node_at_index(self, index):
        current_node = self.head
        current_index = 0
        while current_node and current_index < index:
            current_node = current_node.next
            current_index += 1
        return current_node if current_index == index else None

    def get_most_recent_action_of_type(self, action_type):
        current_node = self.tail
        while current_node:
            if current_node.action_type == action_type:
                return (current_node.action_type, current_node.data)
            current_node = current_node.prev
        return None



