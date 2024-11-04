# ai.py

import copy
import logging

logger = logging.getLogger(__name__)

def get_ai_move(game, ai_player, depth=3):
    # Save the original logging level
    original_level = logging.getLogger().getEffectiveLevel()
    
    # Set logging level to WARNING to suppress DEBUG and INFO messages during AI simulations
    logging.getLogger().setLevel(logging.WARNING)
    best_move = None
    best_value = float('-inf')

    possible_moves = get_possible_moves(game, ai_player)
    for move in possible_moves:
        cloned_game = copy.deepcopy(game)
        cloned_ai_player = next(p for p in cloned_game.players if p.name == ai_player.name)
        apply_move(cloned_game, cloned_ai_player, move)
        values = maxn(cloned_game, depth - 1, cloned_ai_player)
        ai_value = values[cloned_ai_player.name]
        if ai_value > best_value:
            best_value = ai_value
            best_move = move

    # Restore the original logging level
    logging.getLogger().setLevel(original_level)

    return best_move

def maxn(game, depth, current_player):
    if depth == 0 or game.is_game_over():
        return evaluate_game_state(game)

    values = {player.name: float('-inf') for player in game.players}
    possible_moves = get_possible_moves(game, current_player)

    if not possible_moves:
        # If the current player has no moves, skip to the next player
        next_player = get_next_player(game, current_player)
        return maxn(game, depth, next_player)

    for move in possible_moves:
        cloned_game = copy.deepcopy(game)
        cloned_current_player = next(p for p in cloned_game.players if p.name == current_player.name)
        apply_move(cloned_game, cloned_current_player, move)
        next_player = get_next_player(cloned_game, cloned_current_player)
        child_values = maxn(cloned_game, depth - 1, next_player)
        if child_values[current_player.name] > values[current_player.name]:
            values = child_values

    return values

def get_possible_moves(game, player):
    possible_moves = []
    available_positions = game.get_available_card_positions()
    min_x, max_x, min_y, max_y = player.inventory.get_inventory_bounds()

    for card_position in available_positions:
        card = game.card_board[card_position]
        # Generate valid placements
        for x in range(min_x - 1, max_x + 2):
            for y in range(min_y - 1, max_y + 2):
                if game.is_valid_placement(player, x, y):
                    possible_moves.append((card_position, (x, y)))
    return possible_moves

def apply_move(game, player, move):
    card_position, (x, y) = move
    card = game.card_board[card_position]
    player.inventory.add_card(card, x, y)
    game.card_board[card_position] = None
    game.move_player(player, card)
    game.moon_marker_position = card_position
    if game.get_number_of_cards_on_board() <= 3:
        game.deal()
    game.check_inventory(player)
    game.check_end_game()

def evaluate_game_state(game):
    values = {}
    for player in game.players:
        score = player.score * 4  # Each completed token is worth 4 points

        total_advancement = 0
        tokens = []

        # Collect all tokens from the player's inventory
        for card, x, y in player.inventory.get_all_cards():
            tokens.extend(card.tokens)

        # Iterate over the tokens
        for token in tokens:
            if not token.is_completed:
                advancement = get_token_advancement(game, player, token)
                total_advancement += advancement

        score += total_advancement * 1  # Each advancement towards incomplete tokens is worth 1 point

        if player.score >= game.goal:
            score += 200  # Extra points for reaching or exceeding the goal

        # Adjust score based on total movement (lower movement is better)
        score -= player.total_movement * 0.1
        values[player.name] = score
    return values


def get_token_advancement(game, player, token):
    counts = {color: 0 for color in ['red', 'green', 'blue', 'yellow']}
    visited_positions = set()

    for position, card in player.inventory.grid.items():
        if position in visited_positions:
            continue
        color = card.color
        if color in counts:
            chain_size, visited = game.count_color_chain(
                player, position[0], position[1], color
            )
            counts[color] = max(counts[color], chain_size)
            visited_positions.update(visited)

    total_advancement = 0
    for color in ['red', 'green', 'blue', 'yellow']:
        required_amount = getattr(token, color)
        if required_amount > 0:
            advancement = min(counts[color], required_amount)
            total_advancement += advancement
    return total_advancement

def get_next_player(game, current_player):
    least_movement = min(p.total_movement for p in game.players)
    candidates = [p for p in game.players if p.total_movement == least_movement]
    if len(candidates) == 1:
        next_player = candidates[0]
    else:
        for player_name in reversed(game.turn_order):
            if player_name in [p.name for p in candidates]:
                next_player = next(p for p in game.players if p.name == player_name)
                break
    return next_player