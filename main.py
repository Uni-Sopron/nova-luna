import random
from Player import Player
from Card import Card
from Inventory import Inventory
from Token import Token
from card_generator import generate_cards, CARD_DATA

class Game:
    def __init__(self, num_players):
        # create players
        colors = ['white', 'red', 'blue', 'yellow']
        self.players = [Player(colors[i], f'Player{i+1}') for i in range(num_players)]  # Játékosok listája
        self.deck = generate_cards()  # Az összes kártyát tartalmazza
        self.current_player_index = 0  # Nyomon követi hogy ki a következő
        self.board = [[] for _ in range(24)]  # A játék tábla ahol a játékosok mozognak
        for player in self.players:
            self.board[0].append(player)  # Minden játékos elhelyezése a kezdő pozíción
        self.card_board = [None] * 12  # A játék tábla ahol a kártyák vannak
        self.player_positions = {p.name : 0 for p in self.players}  # Játékosok pozíciói a táblán
        self.moon_marker = "moon_marker" # Ezzel jelöljük a holdat
        self.moon_marker_position = 0
        self.card_board[0] = self.moon_marker
        self.deal()

    def next_round(self):
        # Megállapítja a következő játékost a pozíciók alapján
        if (self.is_game_over()):
            self.end_game()
        # todo
        pass

    def move_player(self, player, card):
        movement = card.movement
        current_position = self.player_positions[player.name]
        new_position = (current_position + movement) % len(self.board)
        
        self.board[current_position].remove(player)  # Játékos eltávolíttása a jelenlegi helyzetéről
        self.board[new_position].append(player)  # Játékos hozzáadása az új helyhez
        self.player_positions[player.name] = new_position  # Játékos pozíciók frissítése

    def is_game_over(self):
        # Logika megnézni hogy a játék véget ért-e a 2 lehetséges kondíció közül
        if any(player.score >= 10 for player in self.players):
            return True
        if all(position is None or position == self.moon_marker for position in self.card_board):
            return True
        return False
    
    def end_game(self):
        # Lefut ha valami megnyeri a játékot
        # todo
        pass

    def deal(self):
        # card_board feltöltése kártyákkal a paklibol
        for i in range(len(self.card_board)):
            if self.card_board[i] is None and self.deck:
                self.card_board[i] = self.deck.pop()

    def draw(self, player, card_position):
        available_positions = self.get_available_card_positions()
        if card_position < 0 or card_position >= len(self.card_board):
            raise IndexError("Position out of bounds")
        if self.card_board[card_position] is None or card_position not in available_positions:
            raise ValueError("Invalid position")

        card = self.card_board[card_position]
        player.Inventory.add_card(card, random.randint(-5, 5), random.randint(-5, 5))
        self.card_board[card_position] = None  # Kártya eltávolíttása a card board ról
        self.move_player(player, card)
        self.moon_marker_position = card_position  # A hold mozgatása a felvett kártya helyére

    def get_available_card_positions(self):
        positions = []
        current_position = self.moon_marker_position
        cards_found = 0
        start_position = self.moon_marker_position

        while cards_found < 3:
            current_position = (current_position + 1) % len(self.card_board)
            if self.card_board[current_position] is not None and self.card_board[current_position] != self.moon_marker:
                positions.append(current_position)
                cards_found += 1
            if current_position == start_position:
                break  # Megáll ha vissza érünk a holdhoz és nem talált 3 kártyát

        return positions

if __name__ == "__main__":
    num_players = 2  # Ahány játékossal szeretnénk játszani, max 4 min 1. Most 2
    game = Game(num_players)
