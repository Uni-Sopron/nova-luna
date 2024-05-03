from Inventory import Inventory

class Player:
    # A játékosokhoz leíró class, tartalmazza a személyes scorejukat, színüket, inventoriukat, opcionálisan a board pozíciójukat
    def __init__(self, color, Inventory, score=0):
        self.color = color  # Játékos színe
        self.inventory = Inventory()  # Inventory initializálása
        self.score = score  # A játékos score-ja, vagyis hogy mennyi tokenje van megszerezve, ha eljut 20 ig a játékos nyer