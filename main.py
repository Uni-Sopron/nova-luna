import random
from Player import Player
from Card import Card
from Inventory import Inventory
from Token import Token, generate_token_combinations

class Game:
    def __init__(self):
        self.players = []  # Játékosok listája
        self.inventory = Inventory()  # Inventory initializálása
        self.deck = []  # Az összes kártyát tartalmazza
        self.deck_size = 0  # Lehet redundáns mert más módon is lehet a pakli méretét nyomon követni
        
    def init_game(self, num_players):
        # Létrehozza a játékhoz szükséges elemeket
        self.create_players(2)
        self.create_deck()
        # A játékos mező létrehozása
        self.set_board()
        
    def create_players(self, num_players):
        # Játékosok létrehozása
        colors = ['white', 'red', 'blue', 'yellow']  # Most csak 2 játékossal lesz
        for i in range(num_players):
            player = Player(colors[i], Inventory)
            self.players.append(player)

    def create_deck(self):
        # Logika a pakli létrehozására
        # Elösször a kártyán lévő lehetséges tokeneket hozzuk létre
        # Pakli létrehozása és megkeverése
        token_combinations = generate_token_combinations()
        for i, token in enumerate(token_combinations):
            print(f"Combination {i+1}: Red={token.red}, Green={token.green}, Blue={token.blue}, Yellow={token.yellow}")
        random.shuffle(self.deck)
        self.deck_size = len(self.deck)

    
    def set_board(self):
        # Logika a játékosmező létrehozására
        pass
    
    def next_round(self):
        # Logika amikor egy játékos befejezi a körét
        self.is_game_over()
        pass
    
    def is_game_over(self):
        # Logika megnézni hogy a játék véget ért el a 2 lehetséges kondició közül
        pass
    
    def deal(self):
        # Logika újratölteni a táblát kártyákkal
        pass


def main():
    num_players = 2  # Ahány játékossal szeretnénk játszani, max 4 min 1
    game = Game()
    game.init_game(num_players)

if __name__ == "__main__":
    main()