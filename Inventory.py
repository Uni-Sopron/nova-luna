class Inventory:
    # Minden playernek megvan a játék inventoryja. itt tároljuk a kártyáikat
    def __init__(self):
        self.grid = {}
        self.center_x = 0
        self.center_y = 0

    def add_card(self, card, x, y):
        print(f"Adding card at ({x}, {y})")
        self.grid[(x, y)] = card

    def get_card(self, x, y):
        return self.grid.get((x, y), None)

    def get_all_cards(self):
        return [(card, x, y) for (x, y), card in self.grid.items()]