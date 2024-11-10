import random
from Player import Player
from card_generator import generate_cards, CARD_DATA
import tkinter as tk
from ai import get_ai_move
import threading
import logging

logger = logging.getLogger(__name__)

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
        self.gui = None  # Reference to GUI
        self.deal()

    def set_gui(self, gui):
        # GUI beállítása
        self.gui = gui

    # GUI elkülönítése deepcopy-tol:
    def __getstate__(self):
        """Prepare the state for pickling by removing non-picklable attributes."""
        state = self.__dict__.copy()
        if 'gui' in state:
            del state['gui']
        return state

    def __setstate__(self, state):
        """Restore the state after unpickling."""
        self.__dict__.update(state)
        self.gui = None  # Újra inicializálja a GUI-referenciát None értékre

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
        # Játékos mozgatása kártya mozgás érték alapján
        if self.is_game_over():
            self.end_game()
            return
        movement = card.movement
        current_position = self.player_positions[player.name]
        new_position = (current_position + movement) % len(self.board)

        # Játékos eltávolítása a jelenlegi poziciójárol
        self.board[current_position].remove(player)

        # Játékos hozzá adása az új pozíciójához
        self.board[new_position].append(player)

        # Játékos pozicíojának a frissitése
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
        logger.info("Game Over.")
        scores = sorted([(player.name, player.score) for player in self.players], key=lambda x: x[1], reverse=True)
        self.show_end_game_window(scores)

    def deal(self):
        # Kártyák kiosztása a táblára
        for i in range(len(self.card_board)):
            if self.card_board[i] is None and self.deck:
                self.card_board[i] = self.deck.pop()
        self.check_end_game()

    def get_remaining_cards(self):
        # Megadja hogy mennyi kártya maradt a pakliban
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
            # Loggolás ha nem elérhető GUI
            for name, score in scores:
                logger.info(f"{name}: {score}")

    def ai_play_turn(self):
        current_player = self.players[self.current_player_index]
        if self.gui:
            # Külön szálban kezd MI számítást
            ai_thread = threading.Thread(target=self.gui.handle_ai_turn, args=(current_player,))
            ai_thread.start()
        else:
            # GUI-mentes verzió változatlan

            move = get_ai_move(self, current_player, depth=2)  # Mélység álítható hogy hány körre számoljon előre az MI
            if move:
                self.apply_move(current_player, move)
                self.turn_order.append(current_player.name)
                self.next_round()
            else:
                logger.debug(f"{current_player.name} has no valid moves.")
                self.turn_order.append(current_player.name)
                self.next_round()


    def apply_move(self, player, move):
        card_position, (x, y) = move
        card = self.card_board[card_position]
        player.inventory.add_card(card, x, y)
        self.card_board[card_position] = None
        self.move_player(player, card)

        # Hold jelző eltávlolíttása a jelenlegi poziciojáról
        for i in range(len(self.card_board)):
            if self.card_board[i] == self.moon_marker:
                self.card_board[i] = None
                break

        # Hold jelző elhelyezése az új pozícioján
        self.moon_marker_position = card_position
        self.card_board[card_position] = self.moon_marker

        if self.get_number_of_cards_on_board() < 3:
            self.deal()
        self.check_inventory(player)
        self.check_end_game()



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
        logger.debug(f"Checking token completion for {player.name}: {token.__dict__}")
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        counts = {color: 0 for color in ['red', 'green', 'blue', 'yellow']}

        for dx, dy in directions:
            adj_x, adj_y = x + dx, y + dy
            neighbor_card = player.inventory.get_card(adj_x, adj_y)
            if neighbor_card and neighbor_card.color in counts:
                chain_count, _ = self.count_color_chain(
                    player, adj_x, adj_y, neighbor_card.color, exclude_position=(x, y)
                )
                counts[neighbor_card.color] += chain_count

        for color, required_count in token.__dict__.items():
            if required_count and counts.get(color, 0) < required_count:
                logger.debug(
                    f"Token not completed for {player.name}: needed {required_count} {color}, found {counts[color]}"
                )
                return

        token.is_completed = True
        player.score += 1
        logger.info(f"{player.name} completed a token! New score: {player.score}")

            
    def count_color_chain(self, player, x, y, color, exclude_position=None):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        visited = set()
        count = self._count_color_chain_recursive(player, x, y, color, visited, directions, exclude_position)
        return count, visited


    def _count_color_chain_recursive(self, player, nx, ny, color, visited, directions, exclude_position):
        if (nx, ny) in visited or (exclude_position and (nx, ny) == exclude_position):
            return 0
        visited.add((nx, ny))
        count = 1
        for dx, dy in directions:
            adj_x, adj_y = nx + dx, ny + dy
            neighbor_card = player.inventory.get_card(adj_x, adj_y)
            if neighbor_card and neighbor_card.color == color:
                count += self._count_color_chain_recursive(player, adj_x, adj_y, color, visited, directions, exclude_position)
        return count