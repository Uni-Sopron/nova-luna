import logging

# Configure logging
logging.basicConfig(level=logging.INFO)  # Default level is INFO
logger = logging.getLogger(__name__)
class Inventory:
    # Player's have their own inventories, these inventories store cards
    def __init__(self):
        self.grid = {}
        self.center_x = 0
        self.center_y = 0

    def add_card(self, card, x, y, player_name=None):
        if player_name:
            logger.info(f"{player_name} is adding card at ({x}, {y})")
        else:
            logger.info(f"Adding card at ({x}, {y})")
        self.grid[(x, y)] = card

    def get_card(self, x, y):
        return self.grid.get((x, y), None)

    def get_all_cards(self):
        return [(card, x, y) for (x, y), card in self.grid.items()]

    def get_inventory_bounds(self):
        if not self.grid:
            return 0, 0, 0, 0
        min_x = min(x for x, y in self.grid.keys())
        max_x = max(x for x, y in self.grid.keys())
        min_y = min(y for x, y in self.grid.keys())
        max_y = max(y for x, y in self.grid.keys())
        return min_x, max_x, min_y, max_y
    
    def copy(self):
        new_inventory = Inventory()
        new_inventory.grid = self.grid.copy()
        new_inventory.center_x = self.center_x
        new_inventory.center_y = self.center_y
        return new_inventory

