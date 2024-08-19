import random
from Player import Player
from card_generator import generate_cards, CARD_DATA
import tkinter as tk

class Game:
    def __init__(self, num_players, goal=20):
        # Játék inicializálása
        colors = ['white', 'orange', 'pink', 'teal']
        self.players = [Player(colors[i], f'Player{i+1}', is_ai=(i != 0)) for i in range(num_players)]
        self.deck = generate_cards(CARD_DATA)
        self.goal = goal  # Set the goal for the game
        self.current_player_index = 0
        self.board = [[] for _ in range(24)]
        for player in self.players:
            self.board[0].append(player)
        self.card_board = [None] * 12
        self.player_positions = {p.name: 0 for p in self.players}
        self.moon_marker = "moon_marker"
        self.moon_marker_position = 0
        self.card_board[0] = self.moon_marker
        self.last_positions = []
        self.turn_order = [p.name for p in reversed(self.players)]
        self.gui = None  # Hozzáadás a GUI hivatkozására
        self.deal()

    def set_gui(self, gui):
        # GUI beállítása
        self.gui = gui

    def next_round(self):
        # Körök lekezelése
        if self.is_game_over():
            self.end_game()
            return
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
        if self.players[self.current_player_index].is_ai:
            self.ai_play_turn()
        if self.gui:
            self.gui.update_board()
            self.gui.update_inventory()
            self.gui.update_info()

    def move_player(self, player, card):
        # Move player based on card movement
        if self.is_game_over():
            self.end_game()
            return
        movement = card.movement
        current_position = self.player_positions[player.name]
        new_position = (current_position + movement) % len(self.board)

        # Remove player from current position
        self.board[current_position].remove(player)

        # Add player to the new position at the end of the list
        self.board[new_position].append(player)

        # Update the player's position
        self.player_positions[player.name] = new_position
        player.add_movement(movement)
        self.last_positions.append((player.name, new_position))
        if self.gui:
            self.gui.player_has_moved(player)
        self.check_end_game()

    def check_end_game(self):
        # Nézze meg hogy véget ért-e a játék
        if self.is_game_over():
            self.end_game()

    def is_game_over(self):
        # Ellenőrzi hogy a játék véget ért-e
        if any(player.score >= self.goal for player in self.players):
            return True
        if all(card is None or card == self.moon_marker for card in self.card_board) and len(self.deck) == 0:
            return True
        return False

    def end_game(self):
        # Vége a játéknak
        print("Game Over.")
        scores = sorted([(player.name, player.score) for player in self.players], key=lambda x: x[1], reverse=True)
        self.show_end_game_window(scores)

    def deal(self):
        # Kártyák kiosztása a táblára
        for i in range(len(self.card_board)):
            if self.card_board[i] is None and self.deck:
                self.card_board[i] = self.deck.pop()
        self.check_end_game()

    def get_remaining_cards(self):
        # Return the number of remaining cards in the deck
        return len(self.deck)

    def draw(self, player, card_position):
        # Kártya kihúzása
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
        if self.get_number_of_cards_on_board() <= 3:
            self.deal()
        self.check_end_game()

    def get_number_of_cards_on_board(self):
        # Megszámolja hágy kártya van a táblán
        return sum(1 for card in self.card_board if card is not None and card != self.moon_marker)

    def get_available_card_positions(self):
        # Használható kártyák megkeresése a táblán
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
        # Megkeresi a leghátsó játékost
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
        # Game over ablak megjelenítése
        if self.gui:
            self.gui.show_end_game_window(scores)
        else:
            # Fallback to print if GUI is not available
            for name, score in scores:
                print(f"{name}: {score}")

    def ai_play_turn(self):
        # AI player's turn logic
        current_player = self.players[self.current_player_index]

        if self.gui and not self.gui.fastmode_var.get():
            # If fastmode is off and the GUI is active, handle the AI turn within the GUI context
            self.gui.handle_ai_turn(current_player)
        else:
            # Fastmode is on or GUI is not present, proceed with the AI turn normally
            available_positions = self.get_available_card_positions()
            best_score = -1
            best_card = None
            best_position = None

            for card_position in available_positions:
                card = self.card_board[card_position]
                min_x, max_x, min_y, max_y = current_player.inventory.get_inventory_bounds()
                for x in range(min_x - 1, max_x + 2):
                    for y in range(min_y - 1, max_y + 2):
                        if self.is_valid_placement(current_player, x, y):
                            score = self.evaluate_placement(current_player, card, x, y)
                            if score > best_score:
                                best_score = score
                                best_card = card
                                best_position = (x, y)

            if best_card and best_position:
                x, y = best_position
                current_player.inventory.add_card(best_card, x, y)
                self.card_board[available_positions[0]] = None
                self.move_player(current_player, best_card)
                self.moon_marker_position = available_positions[0]

                if self.get_number_of_cards_on_board() <= 3:
                    self.deal()

                self.check_inventory(current_player)  # Check AI player's inventory for completed tokens
                self.check_end_game()
                if self.gui:
                    self.gui.update_board()
                    self.gui.update_info()
                    self.gui.update_inventory()  # Update all inventories
                self.next_round()



    def evaluate_placement(self, player, card, x, y):
        # Kártya helyeinek pontozása
        score = 0
        adjacent_positions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        counts = {'red': 0, 'green': 0, 'blue': 0, 'yellow': 0}

        def count_color_chain(nx, ny, color, visited):
            if (nx, ny) in visited:
                return 0
            visited.add((nx, ny))
            count = 1
            for dx, dy in adjacent_positions:
                adj_x, adj_y = nx + dx, ny + dy
                neighbor_card = player.inventory.get_card(adj_x, adj_y)
                if neighbor_card and neighbor_card.color == color:
                    count += count_color_chain(adj_x, adj_y, color, visited)
            return count

        for ax, ay in adjacent_positions:
            adjacent_card = player.inventory.get_card(ax, ay)
            if adjacent_card:
                visited = set()
                chain_count = count_color_chain(ax, ay, adjacent_card.color, visited)
                counts[adjacent_card.color] += chain_count

        for token in card.tokens:
            if not token.is_completed:
                if token.red:
                    score += counts['red']
                if token.green:
                    score += counts['green']
                if token.blue:
                    score += counts['blue']
                if token.yellow:
                    score += counts['yellow']

        return score

    def is_valid_placement(self, player, x, y):
        # Megnézi hogy hol vannak érvényes kártya helyek
        if player.inventory.get_card(x, y) is not None:
            return False  # Csak üres helyeket ellenőriz
        adjacent_positions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for ax, ay in adjacent_positions:
            if player.inventory.get_card(ax, ay) is not None:
                return True
        if len(player.inventory.get_all_cards()) == 0 and (x, y) == (player.inventory.center_x, player.inventory.center_y):
            return True
        return False

    def check_inventory(self, player):
        # Inventory ellenőrzése (token küldetésekre)
        for card, x, y in player.inventory.get_all_cards():
            for token in card.tokens:
                if not token.is_completed:
                    self.check_token_completion(player, card, token, x, y)

    def check_token_completion(self, player, card, token, x, y):
        # Token teljesülésének ellenőrzése
        print(f"Checking token completion for {player.name}: {token.__dict__}")
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        def count_color_chain(nx, ny, color, visited):
            if (nx, ny) in visited or (nx == x and ny == y):
                return 0
            visited.add((nx, ny))
            count = 1
            for dx, dy in directions:
                adj_x, adj_y = nx + dx, ny + dy
                neighbor_card = player.inventory.get_card(adj_x, adj_y)
                if neighbor_card and neighbor_card.color == color:
                    count += count_color_chain(adj_x, adj_y, color, visited)
            return count

        counts = {color: 0 for color in ['red', 'green', 'blue', 'yellow']}
        visited = set()

        for dx, dy in directions:
            adj_x, adj_y = x + dx, y + dy
            neighbor_card = player.inventory.get_card(adj_x, adj_y)
            if neighbor_card and neighbor_card.color in counts:
                chain_count = count_color_chain(adj_x, adj_y, neighbor_card.color, visited)
                counts[neighbor_card.color] += chain_count

        for color, required_count in token.__dict__.items():
            if required_count and counts.get(color, 0) < required_count:
                print(f"Token not completed for {player.name}: needed {required_count} {color}, found {counts[color]}")
                return

        token.is_completed = True
        player.score += 1
        print(f"{player.name} completed a token! New score: {player.score}")

if __name__ == "__main__":
    num_players = 4
    game = Game(num_players)
    if not game.players[game.current_player_index].is_ai:
        from gui import NovaLunaGUI
        root = tk.Tk()
        app = NovaLunaGUI(root)
        game.set_gui(app)  # GUI hozzákötése a játékhoz
        app.run()
    else:
        while not game.is_game_over():
            game.next_round()
