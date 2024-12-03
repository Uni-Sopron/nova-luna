from Inventory import Inventory

class Player:
    # Players can be either AI or human
    def __init__(self, color, player_name, score=0, is_ai=False, ai_personality="Balanced"):
        self.name = player_name
        self.color = color
        self.inventory = Inventory()
        self.score = score
        self.total_movement = 0
        self.total_movement_at_turn_start = 0
        self.score_at_turn_start = 0
        self.token_progress_since_turn_start = 0
        self.is_ai = is_ai
        self.ai_personality = ai_personality  # Determines the variant of AI used

    def add_movement(self, movement):
        self.total_movement += movement
