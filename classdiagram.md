classDiagram
    %% Classes
    class Game {
        - List~Player~ players
        - List~Card~ deck
        - int goal
        - int current_player_index
        - List~List~ board
        - List~Card~ card_board
        - Dict~str, int~ player_positions
        - str moon_marker
        - int moon_marker_position
        - List~Tuple~ last_positions
        - List~str~ turn_order
        - Dict~str, int~ card_move_costs
        - NovaLunaGUI gui
        - bool simulation_mode
        - bool in_simulation
        - int turn_number
        - int game_number
        - bool game_over
        - Dict~str, Any~ statistics
        + __init__(int num_players, int goal=10, NovaLunaGUI gui=None, bool simulation_mode=False, int game_number=1)
        + set_gui(NovaLunaGUI gui)
        + next_round()
        + move_player(Player player, Card card)
        + check_end_game()
        + is_game_over() bool
        + end_game()
        + deal()
        + get_remaining_cards() int
        + get_number_of_cards_on_board() int
        + get_available_card_positions() List~int~
        + find_furthest_back_player() Player
        + show_end_game_window(Dict~str, int~ scores)
        + ai_play_turn()
        + apply_move(Player player, Tuple~int, Tuple~int~ move)
        + evaluate_placement(Player player, Card card, int x, int y) int
        + is_valid_placement(Player player, int x, int y) bool
        + check_inventory(Player player)
        + check_token_completion(Player player, Card card, Token token, int x, int y)
        + count_color_chain(Player player, int x, int y, str color, Tuple~int, int exclude_position)
        + simulate_game()
    }

    class NovaLunaGUI {
        - Tk root
        - Tk initialize_window
        - List~Any~ ai_vars
        - IntVar num_players_var
        - IntVar goal_var
        - BooleanVar fastmode_var
        - BooleanVar user_controls_enabled
        - Queue~Any~ ai_queue
        + __init__()
        + create_initialize_window()
        + start_game()
        + initialize_game()
        + create_widgets()
        + create_inventory_button(str player_name, int player_index) Button
        + update_board()
        + draw_player_board()
        + get_player_positions(int num_players) List~Tuple~int, int~
        + draw_card_board()
        + draw_token(Canvas canvas, int x, int y, Token token)
        + player_has_moved(Player player)
        + on_card_click(int card_position)
        + open_inventory_window(int player_index=None)
        + center_inventory_view(Canvas inventory_canvas)
        + draw_inventory(Frame inventory_frame, Canvas inventory_canvas, int player_index=None)
        + on_inventory_click(Tuple~int, int y, Canvas inventory_canvas)
        + update_inventory()
        + update_info()
        + update_deal_button_state()
        + update_card_count()
        + is_valid_placement(Player player, int x, int y) bool
        + is_first_card() bool
        + auto_place_first_card()
        + get_available_card_positions() List~int~
        + refill_card_board_if_needed()
        + deal_cards()
        + show_end_game_window(Dict~str, int~ scores)
        + start_new_game(Window window)
        + run()
        + handle_ai_turn(Player current_player)
        + process_ai_queue()
        + cancel_after_calls()
        + process_ai_move(Player current_player, Tuple~int, Tuple~int~ move)
        + continue_ai_turn(Player current_player, Tuple~int, Tuple~int~ move)
        + highlight_inventory_position(Player player, Tuple~int, int~ position)
        + clear_ai_state()
        + display_picked_card(Card card)
        + show_next_button(Function command)
        + hide_next_button()
        + disable_user_controls()
        + enable_user_controls()
        + show_thinking_message()
        + hide_thinking_message()
        + check_and_enable_user_controls()
        + check_simulation_toggle()
        + on_simulation_toggle()
        + run_simulations(int num_simulations, int goal)
        + save_per_player_data_to_csv(List~Dict~str, Any~ data)
        + save_data_to_csv(List~Dict~str, Any~ data)
        + save_per_turn_data_to_csv(List~Dict~str, Any~ data)
    }

    class Player {
        - str name
        - str color
        - Inventory inventory
        - int score
        - int total_movement
        - int total_movement_at_turn_start
        - bool is_ai
        - str ai_personality
        + __init__(str color, str player_name, int score=0, bool is_ai=False, str ai_personality="Balanced")
        + add_movement(int movement)
    }

    class Inventory {
        - Dict~Tuple~int, int~, Card~ grid
        - int center_x
        - int center_y
        + __init__()
        + add_card(Card card, int x, int y, str player_name=None)
        + get_card(int x, int y) Card
        + get_all_cards() List~Tuple~Card, int, int~
        + get_inventory_bounds() Tuple~int, int, int, int~
        + copy() Inventory
    }

    class Card {
        - str color
        - int movement
        - List~Token~ tokens
        + __init__(str color, int movement, List~Token~ tokens)
        + is_complete() bool
        + __str__() str
        + __repr__() str
    }

    class Token {
        - int red
        - int green
        - int blue
        - int yellow
        - bool is_completed
        + __init__(int red=None, int green=None, int blue=None, int yellow=None, bool is_completed=False)
    }

    class AI {
        + get_ai_move(Game game, Player ai_player, int depth=3, List~Tuple~int, Tuple~int~ possible_moves=None) Tuple~int, Tuple~int~
        + maxn(Game game, int depth, Player current_player) Dict~str, float~
        + get_possible_moves(Game game, Player player) List~Tuple~int, Tuple~int~
        + apply_move(Game game, Player player, Tuple~int, Tuple~int~ move)
        + evaluate_game_state(Game game, Player ai_player) Dict~str, float~
        + get_token_progress(Game game, Player player, Token token) int
        + get_color_counts(Game game, Player player) Dict~str, int~
        + get_consecutive_turns(Game game, Player player) int
        + get_next_player(Game game, Player current_player) Player
    }

    %% Relationships
    Game "1" --> "*" Player : has
    Player "1" --> "1" Inventory : owns
    Inventory "1" --> "*" Card : contains
    Card "1" --> "*" Token : has
    Game "1" --> "*" Card : deck
    NovaLunaGUI "1" --> "1" Game : interacts with
    Game "1" --> "1" AI : uses
    AI "1" --> "1" Game : operates on
    AI "1" --> "1" Player : interacts with
    AI "1" --> "1" Card : interacts with
    AI "1" --> "1" Token : interacts with
