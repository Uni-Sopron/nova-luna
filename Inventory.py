class Inventory:
    def __init__(self):
        self.grid = [[None]]  # Kezdés egyetlen üres cellával
        self.offset_x = 0  # Az x-koordináta eltolásának nyomon követése
        self.offset_y = 0  # Az y-koordináta eltolásának nyomon követése

    def add_card(self, card, x, y):
        # A mező kiterjesztése, hogy biztosítsuk a helyet minden irányban
        self._expand_grid(x, y)
        # A kártya elhelyezése a megfelelő pozícióban az eltolások figyelembevételével
        if self.grid[x + self.offset_x][y + self.offset_y] is None:
            self.grid[x + self.offset_x][y + self.offset_y] = card
        else:
            raise ValueError("A megadott pozíció már foglalt")

    def get_card(self, x, y):
        # A koordináták eltolással történő igazítása
        real_x = x + self.offset_x
        real_y = y + self.offset_y
        # Ellenőrizzük, hogy a koordináták a mező határain belül vannak-e
        if 0 <= real_x < len(self.grid) and 0 <= real_y < len(self.grid[real_x]):
            return self.grid[real_x][real_y]
        else:
            raise IndexError("A mező index kívül esik a tartományon")

    def get_all_cards(self):
        # Az összes tárolt kártya és pozícióik lekérése
        all_cards = []
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                card = self.grid[x][y]
                if card is not None:
                    # A koordináták visszaigazítása az eltolás figyelembevételével
                    all_cards.append((card, x - self.offset_x, y - self.offset_y))
        return all_cards

    def _expand_grid(self, x, y):
        # A mező szükséges méretének kiszámítása
        required_x = x + self.offset_x
        required_y = y + self.offset_y

        # A mező bővítése balra vagy jobbra, ahogy szükséges
        if required_x < 0:
            # Oszlopok hozzáadása balra
            for row in self.grid:
                row.insert(0, None)
            self.offset_x += 1
        elif required_x >= len(self.grid):
            # Oszlopok hozzáadása jobbra
            for row in self.grid:
                row.append(None)

        # A mező bővítése felfelé vagy lefelé, ahogy szükséges
        if required_y < 0:
            # Sorok hozzáadása felülre
            self.grid.insert(0, [None] * len(self.grid[0]))
            self.offset_y += 1
        elif required_y >= len(self.grid[0]):
            # Sorok hozzáadása alulra
            for _ in range(required_y - len(self.grid[0]) + 1):
                self.grid.append([None] * len(self.grid[0]))
