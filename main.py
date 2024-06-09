import random
from Player import Player
from Card import Card
from Inventory import Inventory
from Token import Token
from card_generator import generate_cards, CARD_DATA

class Game:
    def __init__(self, num_players):
        # Játékosok színei
        colors = ['white', 'red', 'blue', 'yellow']
        # Játékosok létrehozása
        self.players = [Player(colors[i], f'Player{i+1}') for i in range(num_players)]
        # Pakli generálása
        self.deck = generate_cards(CARD_DATA)
        # Első játékos indexének inicializálása
        self.current_player_index = 0
        # Játék tábla létrehozása
        self.board = [[] for _ in range(24)]
        # Játékosok elhelyezése a kezdő pozícióba
        for player in self.players:
            self.board[0].append(player)
        # Kártya tábla inicializálása
        self.card_board = [None] * 12
        # Játékos pozíciók nyomon követése
        self.player_positions = {p.name: 0 for p in self.players}
        # Holdjelző beállítása
        self.moon_marker = "moon_marker"
        self.moon_marker_position = 0
        self.card_board[0] = self.moon_marker
        # Utolsó pozíciók nyomon követése (Ez a round orderhez kell)
        self.last_positions = []
        # Játékos sorrend inicializálása (Mivel mindenki ugyanott kezd)
        self.turn_order = [p.name for p in self.players]
        self.deal()

    def next_round(self):
        # Következő kör meghatározása (Ki lesz a következő)
        if self.is_game_over():
            self.end_game()
            return
        current_player = self.players[self.current_player_index]
        # Ki lépett legkevesebbet (Logikusan ő lesz leghátul)
        least_movement = min(p.total_movement for p in self.players)
        candidates = [p for p in self.players if p.total_movement == least_movement]
        if len(candidates) == 1:
            next_player = candidates[0]
        else:
            for player_name in reversed(self.turn_order):
                if player_name in [p.name for p in candidates]:
                    next_player = next(p for p in self.players if p.name == player_name)
                    break
        self.current_player_index = self.players.index(next_player)

    def move_player(self, player, card):
        # Játékos mozgatása
        if self.is_game_over():
            self.end_game()
            return
        movement = card.movement
        current_position = self.player_positions[player.name]
        new_position = (current_position + movement) % len(self.board)

        self.board[current_position].remove(player)
        self.board[new_position].append(player)
        self.player_positions[player.name] = new_position
        player.add_movement(movement)
        self.last_positions.append((player.name, new_position))
        self.check_end_game()

    def check_end_game(self):
        # Game Over kondiciók ellenőrzése
        if self.is_game_over():
            self.end_game()

    def is_game_over(self):
        # Game Over teljesülésének ellenőrzése
        if any(player.score >= 10 for player in self.players):
            return True
        if all(card is None or card == self.moon_marker for card in self.card_board):
            return True
        return False

    def end_game(self):
        # Game Over
        print("Game Over.")
        scores = sorted([(player.name, player.score) for player in self.players], key=lambda x: x[1], reverse=True)
        self.show_end_game_window(scores)

    def deal(self):
        # Kártyák osztása a kártya táblára
        for i in range(len(self.card_board)):
            if self.card_board[i] is None and self.deck:
                self.card_board[i] = self.deck.pop()
        self.check_end_game()

    def draw(self, player, card_position):
        # Kártyahúzás
        available_positions = self.get_available_card_positions()
        if card_position < 0 or card_position >= len(self.card_board):
            raise IndexError("Position out of bounds")
        if self.card_board[card_position] is None or card_position not in available_positions:
            raise ValueError("Invalid position")

        card = self.card_board[card_position]
        player.inventory.add_card(card, random.randint(-5, 5), random.randint(-5, 5))
        self.card_board[card_position] = None
        self.move_player(player, card)
        self.moon_marker_position = card_position
        self.check_end_game()

    def get_available_card_positions(self):
        # Lehetséges (engedélyezett) kártyapozíciók meghatározása
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
                break

        return positions

    def find_furthest_back_player(self):
        # Utolsó játékos meghatározása
        furthest_back_position = min(self.player_positions.values())
        candidates = [player for player in self.players if self.player_positions[player.name] == furthest_back_position]
        if len(candidates) == 1:
            return candidates[0]
        else:
            for player_name in reversed(self.last_positions):
                for candidate in candidates:
                    if candidate.name == player_name:
                        return candidate
        return self.players[0]

    def show_end_game_window(self, scores):
        # Eredmények megjelenítése
        for name, score in scores:
            print(f"{name}: {score}")

if __name__ == "__main__":
    num_players = 4
    game = Game(num_players)
