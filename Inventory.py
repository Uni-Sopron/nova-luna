class Inventory:
    def __init__(self):
        self.grid = []  # Üres mező létrehozása

    def add_card(self, card, x, y):
        # Kártya hozzáadása megadott koordinátához (x, y) a mezőn
        # Ha nincs elég sor/oszlop akkor bővítt
        while len(self.grid) <= x:
            self.grid.append([])
        while len(self.grid[x]) <= y:
            self.grid[x].append(None)
        self.grid[x][y] = card

    def get_card(self, x, y):
        # Egy specifikus kártya lekérése (x, y) a mezőröl
        # Üres értéket ad vissza ha nincs kártya ott
        if x < len(self.grid) and y < len(self.grid[x]):
            return self.grid[x][y]
        else:
            return None

    def get_all_cards(self):
        # Összes tárolt kártya és pozíciójának lekérése
        all_cards = []
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                card = self.grid[x][y]
                if card is not None:
                    all_cards.append((card, x, y))
        return all_cards