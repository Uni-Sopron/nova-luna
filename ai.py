import copy
import logging
import random

logger = logging.getLogger(__name__)

def get_ai_move(game, ai_player, depth=3, possible_moves=None):
    # Save the original logging level
    original_level = logging.getLogger().getEffectiveLevel()

    # Set logging level to WARNING to suppress DEBUG and INFO messages during AI simulations
    logging.getLogger().setLevel(logging.WARNING)

    try:
        if possible_moves is None:
            possible_moves = get_possible_moves(game, ai_player)

        # Handle Random AI Personality
        if ai_player.ai_personality == "Random":
            if possible_moves:
                # Select a random move from possible moves
                best_move = random.choice(possible_moves)
                return best_move
            else:
                return None  # No possible moves
        else:
            # Existing logic for other AI personalities
            best_move = None
            best_value = float('-inf')

            for move in possible_moves:
                cloned_game = copy.deepcopy(game)
                cloned_ai_player = next(p for p in cloned_game.players if p.name == ai_player.name)
                apply_move(cloned_game, cloned_ai_player, move)
                values = maxn(cloned_game, depth - 1, cloned_ai_player)
                ai_value = values[cloned_ai_player.name]
                if ai_value > best_value:
                    best_value = ai_value
                    best_move = move
            return best_move
    finally:
        # Restore the original logging level
        logging.getLogger().setLevel(original_level)

def maxn(game, depth, current_player):
    if depth == 0 or game.is_game_over():
        return evaluate_game_state(game, current_player)
    
    # Set simulation flag
    game.in_simulation = True

    values = {player.name: float('-inf') for player in game.players}
    possible_moves = get_possible_moves(game, current_player)

    if not possible_moves:
        # If no moves can be made, move to the next player
        next_player = get_next_player(game, current_player)
        return maxn(game, depth, next_player)

    for move in possible_moves:
        cloned_game = copy.deepcopy(game)
        cloned_game.in_simulation = True  # Ensure cloned game is marked as simulation
        cloned_current_player = next(p for p in cloned_game.players if p.name == current_player.name)
        apply_move(cloned_game, cloned_current_player, move)
        next_player = get_next_player(cloned_game, cloned_current_player)
        child_values = maxn(cloned_game, depth - 1, next_player)
        if child_values[current_player.name] > values[current_player.name]:
            values = child_values

    # Reset simulation flag
    game.in_simulation = False

    return values

def get_possible_moves(game, player):
    possible_moves = []
    available_positions = game.get_available_card_positions()
    min_x, max_x, min_y, max_y = player.inventory.get_inventory_bounds()

    for card_position in available_positions:
        card = game.card_board[card_position]
        # Generate legal moves
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

    # Remove moon marker from current position
    for i in range(len(game.card_board)):
        if game.card_board[i] == game.moon_marker:
            game.card_board[i] = None
            break

    # Move moon marker to new position
    game.moon_marker_position = card_position
    game.card_board[card_position] = game.moon_marker

    if game.get_number_of_cards_on_board() < 3:
        game.deal()
    game.check_inventory(player)
    game.check_end_game()

def evaluate_game_state(game, ai_player):
    values = {}
    goal_score = game.goal

    for player in game.players:
        score = player.score * 100  # Heavily weight the player's score

        tokens_completed = 0
        tokens_progress = 0

        # Collect tokens from the player's inventory
        for card, x, y in player.inventory.get_all_cards():
            tokens = card.tokens
            for token in tokens:
                if not token.is_completed:
                    # Calculate progress towards incomplete tokens
                    progress = get_token_progress(game, player, token)
                    tokens_progress += progress
                else:
                    # Token has been completed
                    tokens_completed += 1

        # Calculate movement since the start of the turn
        movement_since_turn_start = player.total_movement - player.total_movement_at_turn_start

        # Adjust the scoring based on AI personality
        if player.name == ai_player.name:
            personality = ai_player.ai_personality
            if personality == "Power":
                movement_penalty = 0  # Ignore movement cost
                # Token completion counts at least 4 times advancing tokens
                score += tokens_progress * 10
                score += tokens_completed * 50  # 5 times more than tokens_progress
            elif personality == "Combo":
                # Bonus for taking multiple consecutive turns
                consecutive_turns = get_consecutive_turns(game, player)
                score += consecutive_turns * 60
                movement_penalty = movement_since_turn_start * 0.4 # Heavy movement cost penalty
                score += tokens_progress * 10
                score += tokens_completed * 50  # 5 times more than tokens_progress
            elif personality == "Greedy":
                # Ignore token advancement
                score += tokens_completed * 50  # Only considers token completion
                movement_penalty = movement_since_turn_start * 0.1
            else:  # Balanced / Default
                movement_penalty = movement_since_turn_start * 0.1
                score += tokens_progress * 10
                score += tokens_completed * 50  # 5 times more than tokens_progress
        else:
            # Use default personality for opponents
            movement_penalty = movement_since_turn_start * 0 # Movement not considered for opponents
            # Opponents' progress and completion can be considered negatively
            score -= tokens_progress * 10
            score -= tokens_completed * 50

        if player.score >= game.goal:
            if player.name == ai_player.name:
                score += 100000  # Significant extra points for reaching goal score
            else:
                score -= 100000  # Significant penalty if opponent reaches goal

        # Subtract movement penalty from the score
        score -= movement_penalty

        values[player.name] = score
    return values

def get_token_progress(game, player, token):
    # Calculate progress towards a single token
    counts = get_color_counts(game, player)
    progress = 0
    for color in ['red', 'green', 'blue', 'yellow']:
        required_amount = getattr(token, color)
        if required_amount > 0:
            current_amount = counts.get(color, 0)
            progress += min(current_amount, required_amount)
    return progress

def get_color_counts(game, player):
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

    return counts

def get_consecutive_turns(game, player):
    count = 0
    # Check in reverse order how many times they had consecutive turns
    for player_name in reversed(game.turn_order):
        if player_name == player.name:
            count += 1
        else:
            break
    return count

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
