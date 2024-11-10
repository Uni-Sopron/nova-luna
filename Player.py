from Inventory import Inventory

class Player:
    def __init__(self, color, player_name, score=0, is_ai=False, ai_personality="Balanced"):
        self.name = player_name
        self.color = color
        self.inventory = Inventory()
        self.score = score
        self.total_movement = 0
        self.is_ai = is_ai
        self.ai_personality = ai_personality  # MI személyiséget meghatározó változó

    def add_movement(self, movement):
        self.total_movement += movement
