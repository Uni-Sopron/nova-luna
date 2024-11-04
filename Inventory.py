# Inventory.py

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)  # Default level is INFO
logger = logging.getLogger(__name__)
class Inventory:
    # Minden playernek megvan a játék inventoryja. itt tároljuk a kártyáikat
    def __init__(self):
        self.grid = {}
        self.center_x = 0
        self.center_y = 0

    def add_card(self, card, x, y):
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
