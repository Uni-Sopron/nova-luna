# Player.py

from Inventory import Inventory

class Player:
    def __init__(self, color, player_name, score=0, is_ai=False):
        self.name = player_name
        self.color = color
        self.inventory = Inventory()
        self.score = score
        self.total_movement = 0
        self.is_ai = is_ai  # Added attribute to identify AI players

    def add_movement(self, movement):
        self.total_movement += movement
