from Inventory import Inventory

class Player:
    # A játékosokhoz leíró class, tartalmazza a személyes scorejukat, színüket, inventoriukat, opcionálisan a board pozíciójukat
    def __init__(self, color, Inventory, player_name, score=0):
        self.player_name = player_name
        self.color = color  # Játékos színe
        self.inventory = Inventory()  # Inventory initializálása
        self.score = score  # A játékos score-ja, vagyis hogy mennyi token küldetést teljesített, ha eljut 10 ig a játékos nyer