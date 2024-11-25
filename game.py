import random
from Player import Player
from card_generator import generate_cards, CARD_DATA
import tkinter as tk
from ai import get_ai_move, get_possible_moves
import threading
import logging
import time

logger = logging.getLogger(__name__)

class Game:
    def __init__(self, num_players, goal=10, gui=None, simulation_mode=False, game_number=1):
        # Initialize Game
        colors = ['white', 'orange', 'pink', 'teal']
        self.players = [Player(colors[i], f'Player{i+1}', is_ai=(i != 0)) for i in range(num_players)]
        self.deck = generate_cards(CARD_DATA)
        self.goal = goal  # Goal score
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
        self.card_move_costs = {player.name: 0 for player in self.players} 
        self.gui = gui  # GUI reference
        self.simulation_mode = simulation_mode
        self.in_simulation = False
        self.turn_number = 1  # Initialize the turn number
        self.game_number = game_number  # Game number for tracking simulations
        self.game_over = False
        self.deal()
        self.statistics = {
        'moves_per_player': {player.name: [] for player in self.players},
        'turn_times': {player.name: [] for player in self.players},
        'game_length': 0,
        'winner': None,
        'move_costs': {player.name: [] for player in self.players},
        'scores_per_turn': {player.name: [] for player in self.players},
        'per_turn_data': []
    }


    def set_gui(self, gui):
        # GUI set
        self.gui = gui

    # Remove GUI from deepcopy:
    def __getstate__(self):
        """Prepare the state for pickling by removing non-picklable attributes."""
        state = self.__dict__.copy()
        if 'gui' in state:
            del state['gui']
        return state

    def __setstate__(self, state):
        """Restore the state after unpickling."""
        self.__dict__.update(state)
        self.gui = None  # Re-initiate GUI as None

    def next_round(self):
        # Handles a turn(round)
        self.turn_number += 1
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
        # Move the player based on movement cost
        if self.is_game_over():
            self.end_game()
            return
        movement = card.movement
        current_position = self.player_positions[player.name]
        new_position = (current_position + movement) % len(self.board)

        # Remove player from their current positon
        self.board[current_position].remove(player)

        # Add player to the new position
        self.board[new_position].append(player)

        # Update player position
        self.player_positions[player.name] = new_position
        player.add_movement(movement)
        self.last_positions.append((player.name, new_position))
        if self.gui:
            self.gui.player_has_moved(player)
        self.check_end_game()

    def check_end_game(self):
        # Checks if the game is over according to the rules
        if self.is_game_over():
            self.game_over = True
            self.end_game()

    def is_game_over(self):
        # Checks if the game is over
        if any(player.score >= self.goal for player in self.players):
            if self.in_simulation:
                return False
            else:
                return True
        if all(card is None or card == self.moon_marker for card in self.card_board) and len(self.deck) == 0:
            return True
        return False

    def end_game(self):
        logger.info("Game Over.")
        for player in self.players:
            logger.info(f"{player.name} final score: {player.score}")
        # Perform necessary end-of-game processing
        highest_score = max(player.score for player in self.players)
        tied_players = [player for player in self.players if player.score == highest_score]
        
        # Define player priority
        # In case of tie player priority takes precedence
        player_priority = {'Player1': 1, 'Player2': 2, 'Player3': 3, 'Player4': 4}
        
        # Select the winner based on priority
        winner = min(tied_players, key=lambda p: player_priority.get(p.name, float('inf')))
        
        logger.info(f"Winner: {winner.name} with score: {winner.score}")
        
        # Store the winner in statistics
        self.statistics['winner'] = winner.name
        self.statistics['final_scores'] = {player.name: player.score for player in self.players}
        
        if self.gui:
            self.show_end_game_window(self.statistics['final_scores'])

    def deal(self):
        # Filling the card board with cards from the deck
        for i in range(len(self.card_board)):
            if self.card_board[i] is None and self.deck:
                self.card_board[i] = self.deck.pop()
        self.check_end_game()

    def get_remaining_cards(self):
        # Returns the amount of cards left in the deck
        return len(self.deck)

    def draw(self, player, card_position):
        # Draw a card from the board
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
        # Counts of number of active cards on the board
        return sum(1 for card in self.card_board if card is not None and card != self.moon_marker)

    def get_available_card_positions(self):
        # Returns the drawable cards on the board
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
        # Finds the last player (in turns)
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
        # Display Game Over window
        if self.gui:
            self.gui.show_end_game_window(scores)
        else:
            # Logging in case GUI isn't present
            for name, score in scores:
                logger.info(f"{name}: {score}")

    def ai_play_turn(self):
        current_player = self.players[self.current_player_index]
        current_player.total_movement_at_turn_start = current_player.total_movement  # Update movement at turn start

        if self.gui:
            # Existing GUI handling code
            ai_thread = threading.Thread(target=self.gui.handle_ai_turn, args=(current_player,))
            ai_thread.start()
        else:
            # Simulation mode

            # Safety Measure: Deal new cards if needed
            cards_on_board = sum(1 for card in self.card_board if card is not None and card != self.moon_marker)
            if cards_on_board <= 2 and self.deck:
                self.deal()

            start_time = time.time()
            possible_moves = get_possible_moves(self, current_player)
            move = get_ai_move(self, current_player, depth=3, possible_moves=possible_moves)
            end_time = time.time()
            turn_time = end_time - start_time

            # Record statistics
            self.statistics['turn_times'][current_player.name].append(turn_time)
            self.statistics['moves_per_player'][current_player.name].append(len(possible_moves))

            # Record per-turn data
            turn_data = {
                'game_number': self.game_number,
                'turn_number': self.turn_number,
                'player_name': current_player.name,
                'ai_personality': current_player.ai_personality,
                'turn_time': turn_time
            }
            self.statistics['per_turn_data'].append(turn_data)

            if move:
                card_position, _ = move
                card = self.card_board[card_position]
                self.statistics['move_costs'][current_player.name].append(card.movement)
                self.apply_move(current_player, move)
            else:
                logger.debug(f"{current_player.name} has no valid moves.")

            # Append current player's name to turn_order for tie-breaking
            self.turn_order.append(current_player.name)

            # Determine next player
            self.next_round()


    def apply_move(self, player, move):
        card_position, (x, y) = move
        card = self.card_board[card_position]

        # Add the card's movement cost to the player's total move costs in statistics
        self.statistics['move_costs'][player.name].append(card.movement)

        player.inventory.add_card(card, x, y, player.name)
        self.card_board[card_position] = None
        self.move_player(player, card)

        # Remove Moon Marker from its current positon
        for i in range(len(self.card_board)):
            if self.card_board[i] == self.moon_marker:
                self.card_board[i] = None
                break

        # Place Moon Marker in its new position
        self.moon_marker_position = card_position
        self.card_board[card_position] = self.moon_marker

        if self.get_number_of_cards_on_board() < 3:
            self.deal()
        self.check_inventory(player)
        self.check_end_game()



    def evaluate_placement(self, player, card, x, y):
        # Score the placement of cards (legacy AI)
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
        # Checks for valid inventory placement
        if player.inventory.get_card(x, y) is not None:
            return False  # Only an empty position can be valid
        adjacent_positions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for ax, ay in adjacent_positions:
            if player.inventory.get_card(ax, ay) is not None:
                return True
        if len(player.inventory.get_all_cards()) == 0 and (x, y) == (player.inventory.center_x, player.inventory.center_y):
            return True
        return False

    def check_inventory(self, player):
        # Check the entire inventory of a player for token completion
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
    
    def simulate_game(self):
        """Run a game simulation without GUI."""
        self.turn_number = 1
        total_move_costs = 0
        total_cards_picked = 0  # Track the total number of cards picked

        while not self.is_game_over():
            current_player = self.players[self.current_player_index]
            for player in self.players:
                self.statistics['scores_per_turn'][player.name].append(player.score)

            if current_player.is_ai:
                self.ai_play_turn()
            else:
                current_player.ai_personality = 'Balanced'
                current_player.is_ai = True
                self.ai_play_turn()

            # Update move costs
            if current_player.is_ai:
                last_move_cost = (
                    self.statistics['move_costs'][current_player.name][-1]
                    if self.statistics['move_costs'][current_player.name]
                    else 0
                )
                total_move_costs += last_move_cost
                total_cards_picked += 1

            self.next_round()

        # Record the game length
        self.statistics['game_length'] = self.turn_number

        # Determine the winner based on scores and player priority
        max_score = max(player.score for player in self.players)
        tied_players = [player for player in self.players if player.score == max_score]

        # Define player priority
        player_priority = {'Player1': 1, 'Player2': 2, 'Player3': 3, 'Player4': 4}
        winner = min(tied_players, key=lambda p: player_priority.get(p.name, float('inf')))

        logger.info(f"Winner: {winner.name} with score: {winner.score}")

        # Update the statistics
        self.statistics['winner'] = winner.name
        self.statistics['winner_ai_type'] = winner.ai_personality
        self.statistics['final_scores'] = {player.name: player.score for player in self.players}