
from Inventory import Inventory
# A játékosok classja. tárolja a játékos szükséges adatait
class Player:
    def __init__(self, color, player_name, score=0):
        self.name = player_name
        self.color = color
        self.inventory = Inventory()
        self.score = score
        self.total_movement = 0  # Mennyi lépést tett összesen

    def add_movement(self, movement):
        self.total_movement += movement
