import tkinter as tk
from game import Game
from ai import get_ai_move
import threading
import queue
import logging
import csv
from multiprocessing import Pool, cpu_count
import gc

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Default level for logging in INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NovaLunaGUI:
    def __init__(self):
        self.root = None  # The main game window will be created later
        self.initialize_window = tk.Tk()
        self.initialize_window.title("Game Setup")
        self.ai_vars = []
        self.num_players_var = tk.IntVar(value=4)
        self.goal_var = tk.IntVar(value=10)
        self.fastmode_var = tk.BooleanVar(value=True)  # Variable to store Fastmode status
        self.user_controls_enabled = True
        self.create_initialize_window()

    def create_initialize_window(self):
        # Create the initialization window
        self.initialize_window.geometry("400x500")  # Adjust the size to accommodate new widgets

        tk.Label(self.initialize_window, text="Number of Players:").pack(pady=5)
        num_players_spinbox = tk.Spinbox(
            self.initialize_window,
            from_=1,
            to=4,
            textvariable=self.num_players_var,
            wrap=False,  # Disable wrapping
            state="readonly"
        )
        num_players_spinbox.pack(pady=5)

        tk.Label(self.initialize_window, text="Goal:").pack(pady=5)
        goal_slider = tk.Scale(
            self.initialize_window,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
            variable=self.goal_var,
        )
        goal_slider.pack(pady=5)

        # AI Personality Selection
        ai_frame = tk.Frame(self.initialize_window)
        ai_frame.pack(pady=10)

        tk.Label(ai_frame, text="AI Personality:").grid(row=0, column=0, padx=10)

        # Define the AI personality options
        ai_personality_options = ["Human", "Balanced", "Power", "Combo", "Greedy", "Random"]
        self.ai_personality_vars = []

        for i in range(4):
            var = tk.StringVar(value="Human")
            self.ai_personality_vars.append(var)
            label = tk.Label(ai_frame, text=f"Player {i + 1}")
            label.grid(row=i + 1, column=0, padx=5, sticky='w')
            option_menu = tk.OptionMenu(
                ai_frame,
                var,
                *ai_personality_options,
                command=lambda value, i=i: self.check_simulation_toggle()
            )
            option_menu.grid(row=i + 1, column=1, padx=5, sticky='w')
            # Disable the OptionMenu if the player is not in the game
            if i >= self.num_players_var.get():
                option_menu.config(state=tk.DISABLED)

        def update_ai_personality_state(*args):
            for i in range(4):
                option_menu = ai_frame.grid_slaves(row=i + 1, column=1)[0]
                if i < self.num_players_var.get():
                    option_menu.config(state=tk.NORMAL)
                else:
                    option_menu.config(state=tk.DISABLED)
                    self.ai_personality_vars[i].set("Human")
            self.check_simulation_toggle()  # Update simulation toggle whenever number of players changes

        self.num_players_var.trace("w", update_ai_personality_state)

        # Simulation Mode Checkbox (Disabled by default)
        self.simulation_var = tk.BooleanVar(value=False)
        self.simulation_check = tk.Checkbutton(
            self.initialize_window,
            text="Simulation Mode",
            variable=self.simulation_var,
            command=self.on_simulation_toggle,
            state=tk.DISABLED  # Disabled by default
        )
        self.simulation_check.pack(pady=10)

        # Number of Simulations Input (Disabled initially)
        self.num_simulations_var = tk.IntVar(value=1)
        self.num_simulations_label = tk.Label(self.initialize_window, text="Number of Simulations:")
        self.num_simulations_entry = tk.Entry(self.initialize_window, textvariable=self.num_simulations_var, state='disabled')
        self.num_simulations_label.pack(pady=5)
        self.num_simulations_entry.pack(pady=5)

        # Fastmode Checkbox
        self.fastmode_check = tk.Checkbutton(
            self.initialize_window,
            text="Fastmode",
            variable=self.fastmode_var
        )
        self.fastmode_check.pack(pady=10)

        start_button = tk.Button(self.initialize_window, text="Start", command=self.start_game)
        start_button.pack(pady=10)

    def start_game(self):
        num_players = self.num_players_var.get()
        goal = self.goal_var.get()
        simulation_mode = self.simulation_var.get()
        num_simulations = self.num_simulations_var.get()

        self.game = Game(num_players, goal)

        for i in range(num_players):
            ai_personality = self.ai_personality_vars[i].get()
            if ai_personality != "Human":
                self.game.players[i].is_ai = True
                self.game.players[i].ai_personality = ai_personality
            else:
                self.game.players[i].is_ai = False
                self.game.players[i].ai_personality = None

        self.initialize_window.destroy()  # Destroy the setup window

        if simulation_mode:
            # Start simulations
            self.run_simulations(num_simulations, goal)
        else:
            self.initialize_game()

    def initialize_game(self):
        # Create the main game window
        self.root = tk.Tk()
        self.root.title("Nova Luna")
        
        self.selected_card = None
        self.selected_card_position = None
        self.available_positions = []
        self.inventory_window = None
        self.all_players_moved = False  # Check if everyone took their first turn

        self.create_widgets()
        self.update_board()
        self.update_info()
        self.game.turn_order.append(self.game.players[0].name)
        self.game.set_gui(self)
        
        # Initialize the AI queue and schedule the AI queue processing
        self.ai_queue = queue.Queue()
        self.root.after(100, self.process_ai_queue)

        # Check if Player 1 is AI and if so, trigger AI's first move
        if self.game.players[0].is_ai:
            self.game.ai_play_turn()

        self.run()


    def create_widgets(self):
        # Create widgets
        self.canvas = tk.Canvas(self.root, width=800, height=350)
        self.canvas.pack()

        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack()

        # Create a frame to hold the player's turn label and the scores
        self.turn_and_score_frame = tk.Frame(self.info_frame)
        self.turn_and_score_frame.pack(side=tk.LEFT, anchor='center', pady=20)

        # Frame for the player's turn token and label
        self.turn_token_frame = tk.Frame(self.turn_and_score_frame)
        self.turn_token_frame.pack(side=tk.LEFT, padx=10)

        # Canvas for the player's turn token
        self.turn_token_canvas = tk.Canvas(self.turn_token_frame, width=20, height=20)
        self.turn_token_canvas.pack(side=tk.LEFT)

        # Player turn label on the left
        self.player_turn_label = tk.Label(self.turn_token_frame, text="")
        self.player_turn_label.pack(side=tk.LEFT, padx=10)

        # Frame for the scores to ensure they are aligned to the right of the player's turn
        self.scores_frame = tk.Frame(self.turn_and_score_frame)
        self.scores_frame.pack(side=tk.LEFT)

        # Initial empty labels for scores
        self.score_labels = []
        for player in self.game.players:
            player_label = tk.Label(self.scores_frame, text="")
            player_label.pack(anchor='w', pady=2)
            self.score_labels.append(player_label)

        # Rectangular Card shape to display remaining cards
        self.card_canvas = tk.Canvas(self.info_frame, width=100, height=150)
        self.card_canvas.pack(side=tk.RIGHT, padx=20)
        self.card_rectangle = self.card_canvas.create_rectangle(10, 10, 90, 140, outline="black", width=2)
        self.card_text = self.card_canvas.create_text(50, 75, text=str(self.game.get_remaining_cards()), font=("Arial", 20))

        # "Deal" button next to the card size display
        self.deal_button = tk.Button(self.info_frame, text="Deal", command=self.deal_cards)
        self.deal_button.pack(side=tk.RIGHT, padx=5)
        
        self.update_deal_button_state()  # Ensure the deal button state is correct at start

        # Frame to hold the picked card canvas
        self.picked_card_frame = tk.Frame(self.info_frame)
        self.picked_card_frame.pack(side=tk.LEFT, padx=10)

        self.picked_card_label = tk.Label(self.picked_card_frame, text="Picked card:")
        self.picked_card_label.pack(side=tk.TOP, pady=5)

        self.picked_card_canvas = tk.Canvas(self.picked_card_frame, width=100, height=150)
        self.picked_card_canvas.pack(side=tk.TOP)

        # Frame to hold both inventory buttons and AI toggle controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10, side=tk.TOP, anchor='w')

        # Create inventory buttons and place them on the left side
        inventory_button_frame = tk.Frame(control_frame)
        inventory_button_frame.pack(side=tk.LEFT)

        for i, player in enumerate(self.game.players):
            inventory_button = self.create_inventory_button(f"Player{i+1}", i)
            inventory_button.pack(pady=5, side=tk.LEFT, in_=inventory_button_frame)

    def create_inventory_button(self, player_name, player_index):
        fg_color = "black" if player_index in [0, 2] else "white"
        button = tk.Button(
            self.root,
            text=f"{player_name}",  # Player's name for labeling
            command=lambda: self.open_inventory_window(player_index),
            bg=self.game.players[player_index].color,
            fg=fg_color,
            activebackground=self.game.players[player_index].color,
            borderwidth=2,
            relief="solid"
        )
        return button

    def update_board(self):
        # Update the game board in the GUI
        self.canvas.delete("all")
        self.draw_player_board()
        self.draw_card_board()
        self.update_card_count()  # Update the remaining cards count
        self.update_info() # Update player info
        self.canvas.update()

    def draw_player_board(self):
        # Draw the player board on the canvas
        size = 60
        margin = 5
        for i in range(len(self.game.board)):
            x0 = (i % 12) * (size + margin) + margin
            y0 = (i // 12) * (size + margin) + margin
            x1 = x0 + size
            y1 = y0 + size
            self.canvas.create_rectangle(x0, y0, x1, y1, outline='black')

            players = self.game.board[i]
            positions = self.get_player_positions(len(players))

            if i == 0 and not self.all_players_moved:
                # Draw in reverse order for the first square before all players have moved
                for index, player in enumerate(reversed(players)):
                    pos_x, pos_y = positions[index]
                    self.canvas.create_oval(x0 + pos_x, y0 + pos_y, x0 + pos_x + 20, y0 + pos_y + 20, fill=player.color)
                    text_color = 'black' if player.name in ['Player1', 'Player3'] else 'white'
                    self.canvas.create_text(x0 + pos_x + 10, y0 + pos_y + 10, text=player.name[-1], fill=text_color)
            else:
                # Normal drawing order for all other squares
                for index, player in enumerate(players):
                    pos_x, pos_y = positions[index]
                    self.canvas.create_oval(x0 + pos_x, y0 + pos_y, x0 + pos_x + 20, y0 + pos_y + 20, fill=player.color)
                    text_color = 'black' if player.name in ['Player1', 'Player3'] else 'white'
                    self.canvas.create_text(x0 + pos_x + 10, y0 + pos_y + 10, text=player.name[-1], fill=text_color)


    def get_player_positions(self, num_players):
        # Determine player positions based on the number of players at the spot
        positions = {
            1: [(20, 20)],
            2: [(35, 35), (5, 5)],  # Last to arrive at (5,5), first at (35,35)
            3: [(35, 35), (5, 35), (20, 5)],  # Last to arrive at (20,5), second at (5,35), first at (35,35)
            4: [(35, 35), (5, 35), (35, 5), (5, 5)]  # Last to arrive at (5,5), then (35,5), then (5,35), first at (35,35)
        }
        return positions.get(num_players, [])



    def draw_card_board(self):
        # Draw the card board
        size = 80
        margin = 5
        for i in range(len(self.game.card_board)):
            x0 = (i % 6) * (size + margin) + margin
            y0 = (i // 6) * (size + margin) + 150
            x1 = x0 + size
            y1 = y0 + size
            if i == self.game.moon_marker_position:
                self.canvas.create_oval(x0, y0, x1, y1, fill='yellow')
            elif self.game.card_board[i] is not None:
                card = self.game.card_board[i]
                if isinstance(card, str):
                    continue
                outline_color = 'black' if self.selected_card_position == i else card.color
                self.canvas.create_rectangle(x0, y0, x1, y1, outline=outline_color, width=6)
                self.canvas.create_text(x0 + 10, y0 + 10, text=str(card.movement), anchor='nw', font=("Helvetica", 14))
                if card.tokens:
                    if len(card.tokens) > 0:
                        token1 = card.tokens[0]
                        self.draw_token(self.canvas, x1 - 30, y0 + 10, token1)
                    if len(card.tokens) > 1:
                        token2 = card.tokens[1]
                        self.draw_token(self.canvas, x0 + 10, y1 - 30, token2)
                    if len(card.tokens) > 2:
                        token3 = card.tokens[2]
                        self.draw_token(self.canvas, x1 - 30, y1 - 30, token3)
                self.canvas.tag_bind(self.canvas.create_rectangle(x0, y0, x1, y1, outline=''), '<Button-1>', lambda event, i=i: self.on_card_click(i))

    def draw_token(self, canvas, x, y, token):
        # Draw the tokens
        colors = []
        if token.red:
            colors.extend(['red'] * token.red)
        if token.green:
            colors.extend(['green'] * token.green)
        if token.blue:
            colors.extend(['blue'] * token.blue)
        if token.yellow:
            colors.extend(['yellow'] * token.yellow)
        for i, color in enumerate(colors):
            row = i // 2
            col = i % 2
            canvas.create_oval(x + col * 10, y + row * 10, x + 10 + col * 10, y + 10 + row * 10, fill=color)
    
    def player_has_moved(self, player):
        # Mark that a player has moved
        self.all_players_moved = all(p.total_movement > 0 for p in self.game.players)

    def on_card_click(self, card_position):
        # Handle the card click event
        if not self.user_controls_enabled:
            return
        if self.selected_card is None:
            self.available_positions = self.get_available_card_positions()

        if card_position not in self.available_positions:
            logger.info("Invalid card selection. Please select a card within the first three positions from the moon marker.")
            return

        if card_position in self.available_positions:
            if self.selected_card is not None and self.selected_card_position is not None:
                self.game.card_board[self.selected_card_position] = self.selected_card
            self.selected_card_position = card_position
            self.selected_card = self.game.card_board[card_position]
            self.game.card_board[card_position] = None
            self.update_board()

            # Display the picked card
            self.display_picked_card(self.selected_card)

            # Disable the Deal button after a player selects a card
            self.deal_button.config(state=tk.DISABLED)

            if self.is_first_card():
                self.auto_place_first_card()
            else:
                if not self.inventory_window or not self.inventory_window.winfo_exists():
                    self.open_inventory_window()
        else:
            logger.info("Invalid card selection. Please select a card within the first three positions from the moon marker.")

    def open_inventory_window(self, player_index=None):
        # Determine the player whose inventory to open
        if player_index is None:
            current_player = self.game.players[self.game.current_player_index]
            player_index = self.game.current_player_index
        else:
            current_player = self.game.players[player_index]

        player_color = current_player.color  # Get the player's color
        logger.debug(f"Opening inventory for {current_player.name} with color {player_color}")

        # If the inventory window already exists and is open, reuse it
        if self.inventory_window and self.inventory_window.winfo_exists():
            # If the inventory window is displaying a different player's inventory, update it
            if self.inventory_window_player_index != player_index:
                # Update the window title and color line
                self.inventory_window.title(f"{current_player.name}'s Inventory")
                self.color_line.config(bg=player_color)
                # Update the current inventory window's player index
                self.inventory_window_player_index = player_index
                # Clear the inventory canvas before redrawing
                self.inventory_canvas.delete("all")
            else:
                # If it's already showing the correct player's inventory, do nothing
                pass
        else:
            # Create a new inventory window
            self.inventory_window = tk.Toplevel(self.root)
            self.inventory_window.title(f"{current_player.name}'s Inventory")
            # Store the current inventory window's player index
            self.inventory_window_player_index = player_index

            # Draw a colored line at the top to indicate the player's color
            self.color_line = tk.Frame(self.inventory_window, bg=player_color, height=5)
            self.color_line.pack(fill=tk.X, side=tk.TOP)

            # Create the main frame for the inventory contents
            inventory_frame = tk.Frame(self.inventory_window)
            inventory_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

            self.inventory_canvas = tk.Canvas(inventory_frame)
            self.inventory_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Create scrollbars and attach them to the inventory frame and canvas
            scrollbar_y = tk.Scrollbar(inventory_frame, orient=tk.VERTICAL, command=self.inventory_canvas.yview)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

            scrollbar_x = tk.Scrollbar(self.inventory_window, orient=tk.HORIZONTAL, command=self.inventory_canvas.xview)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

            self.inventory_canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

        # Update the content of the inventory
        inventory_inner_frame = tk.Frame(self.inventory_canvas)
        self.inventory_canvas.create_window((0, 0), window=inventory_inner_frame, anchor='nw')

        self.draw_inventory(inventory_inner_frame, self.inventory_canvas, player_index)
        self.center_inventory_view(self.inventory_canvas)

    def center_inventory_view(self, inventory_canvas):
        # Center the Inventory view
        self.root.update_idletasks()
        bbox = inventory_canvas.bbox("all")
        if bbox is not None:
            canvas_width = inventory_canvas.winfo_width()
            canvas_height = inventory_canvas.winfo_height()

            center_x = self.game.players[self.game.current_player_index].inventory.center_x * 65 - canvas_width // 2
            center_y = self.game.players[self.game.current_player_index].inventory.center_y * 65 - canvas_height // 2

            inventory_canvas.xview_moveto(center_x / bbox[2])
            inventory_canvas.yview_moveto(center_y / bbox[3])

    def draw_inventory(self, inventory_frame, inventory_canvas, player_index=None):
        # Clear the inventory canvas before drawing
        inventory_canvas.delete("all")
        
        if player_index is None:
            current_player = self.game.players[self.game.current_player_index]
        else:
            current_player = self.game.players[player_index]
        
        # Use the same size for inventory cards as on the card board for consistency
        size = 65  # Same size as used on the card board
        margin = 5

        grid = current_player.inventory.grid

        if not grid:
            return

        min_x = min(x for x, y in grid.keys())
        max_x = max(x for x, y in grid.keys())
        min_y = min(y for x, y in grid.keys())
        max_y = max(y for x, y in grid.keys())

        for x in range(min_x - 1, max_x + 2):
            for y in range(min_y - 1, max_y + 2):
                x0 = (x - min_x + 1) * (size + margin)
                y0 = (y - min_y + 1) * (size + margin)
                x1 = x0 + size
                y1 = y0 + size
                rect_id = inventory_canvas.create_rectangle(x0, y0, x1, y1, outline='black')
                card = current_player.inventory.get_card(x, y)
                if card:
                    inventory_canvas.create_rectangle(x0, y0, x1, y1, outline=card.color, width=4)
                    if len(card.tokens) > 0:
                        token1 = card.tokens[0]
                        self.draw_token(inventory_canvas, x1 - 30, y0 + 10, token1)
                    if len(card.tokens) > 1:
                        token2 = card.tokens[1]
                        self.draw_token(inventory_canvas, x0 + 10, y1 - 30, token2)
                    if len(card.tokens) > 2:
                        token3 = card.tokens[2]
                        self.draw_token(inventory_canvas, x1 - 30, y1 - 30, token3)
                else:
                    inventory_canvas.tag_bind(rect_id, '<Button-1>', lambda event, i=(x, y): self.on_inventory_click(i, inventory_canvas))
                    inventory_canvas.tag_bind(inventory_canvas.create_rectangle(x0, y0, x1, y1, outline=''), '<Button-1>', lambda event, i=(x, y): self.on_inventory_click(i, inventory_canvas))

        # Update the scroll region to fit the content
        inventory_canvas.update_idletasks()
        inventory_canvas.configure(scrollregion=inventory_canvas.bbox("all"))
        # Draw the highlight if the player's inventory has a highlight_position
        highlight_position = getattr(current_player.inventory, 'highlight_position', None)
        if highlight_position is not None:
            x, y = highlight_position
            # Calculate the coordinates for the highlight rectangle
            size = 65  # Match the inventory card size
            margin = 5

            min_x = min(x for x, y in grid.keys())
            min_y = min(y for x, y in grid.keys())

            x0 = (x - min_x + 1) * (size + margin)
            y0 = (y - min_y + 1) * (size + margin)
            x1 = x0 + size
            y1 = y0 + size

            # Draw the highlight
            inventory_canvas.create_rectangle(x0, y0, x1, y1, outline='orange', width=6)

    def on_inventory_click(self, grid_position, inventory_canvas):
        # Handle a click inside a player's inventory
        if not self.user_controls_enabled:
            return
        if self.selected_card is None:
            logger.info("Select a card first")
            return
        
        # Check if the inventory being clicked belongs to the current player
        if self.inventory_window_player_index != self.game.current_player_index:
            logger.info("You can only place cards on your own inventory.")
            return

        player = self.game.players[self.game.current_player_index]
        x, y = grid_position
        if self.is_valid_placement(player, x, y):
            try:
                player.inventory.add_card(self.selected_card, x, y, player.name)
                self.game.moon_marker_position = self.selected_card_position
                for i in range(len(self.game.card_board)):
                    if self.game.card_board[i] == self.game.moon_marker:
                        self.game.card_board[i] = None
                        break
                self.game.card_board[self.selected_card_position] = self.game.moon_marker
                self.game.move_player(player, self.selected_card)
                self.selected_card = None
                self.selected_card_position = None
                inventory_canvas.update_idletasks()
                self.update_inventory()
                self.update_board()
                self.game.check_inventory(player)
                self.refill_card_board_if_needed()
                if not self.game.is_game_over():
                    self.game.turn_order.append(player.name)
                    self.game.next_round()
                    self.update_info()
                    self.update_inventory()
                else:
                    self.show_end_game_window()
            except ValueError:
                logger.info("Invalid input. Please click a valid grid position.")
        else:
            logger.info("Invalid placement. Please place the card adjacent to an existing card.")

    def update_inventory(self):
        # Refresh the current inventory window if it exists
        if self.inventory_window and self.inventory_window.winfo_exists():
            player_index = self.inventory_window_player_index
            current_player = self.game.players[player_index]
            player_color = current_player.color  # Get the player's color

            # Update the color of the color line
            self.color_line.config(bg=player_color)

            # Clear the inventory canvas before redrawing
            self.inventory_canvas.delete("all")

            # Redraw the inventory contents
            self.draw_inventory(None, self.inventory_canvas, player_index=player_index)


    def update_info(self):
        # Clear the current display
        for widget in self.scores_frame.winfo_children():
            widget.destroy()

        # Update or create the player's token as a small oval next to the turn text
        current_player = self.game.players[self.game.current_player_index]

        if hasattr(self, 'turn_token_canvas'):
            self.turn_token_canvas.delete("all")
            self.turn_token_canvas.create_oval(2, 2, 18, 18, fill=current_player.color)
        else:
            self.turn_token_canvas = tk.Canvas(self.turn_and_score_frame, width=20, height=20)
            self.turn_token_canvas.pack(side=tk.LEFT, padx=(0, 5))
            self.turn_token_canvas.create_oval(2, 2, 18, 18, fill=current_player.color)

        # Update the player's turn label text
        self.player_turn_label.config(text=f"{current_player.name}'s turn")

        # Update scores for each player with a token next to the score
        for i, player in enumerate(self.game.players):
            player_frame = tk.Frame(self.scores_frame)
            player_frame.pack(anchor='w', pady=2)
            token_canvas = tk.Canvas(player_frame, width=20, height=20)
            token_canvas.pack(side=tk.LEFT)
            token_canvas.create_oval(2, 2, 18, 18, fill=player.color)
            score_text = f"{player.name}: {player.score}/{self.game.goal}"
            player_label = tk.Label(player_frame, text=score_text)
            player_label.pack(side=tk.LEFT)

        self.card_canvas.pack(side=tk.RIGHT, padx=20)
        # Update the "Deal" button state at the start of each turn
        self.update_deal_button_state()

        # Automatically open the current player's inventory
        self.open_inventory_window(player_index=self.game.current_player_index)


    def update_deal_button_state(self):
        if not self.user_controls_enabled:
            self.deal_button.config(state=tk.DISABLED)
        cards_on_board = sum(1 for card in self.game.card_board if card is not None and card != self.game.moon_marker)
        if cards_on_board >= 3 or len(self.game.deck) == 0:
            self.deal_button.config(state=tk.DISABLED)
        else:
            self.deal_button.config(state=tk.NORMAL)


    def update_card_count(self):
        # Update the text in the card-shaped rectangle
        self.card_canvas.itemconfig(self.card_text, text=str(self.game.get_remaining_cards()))

    def is_valid_placement(self, player, x, y):
        # Check if the attempted inventory placement is a valid move
        adjacent_positions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for ax, ay in adjacent_positions:
            if player.inventory.get_card(ax, ay) is not None:
                return True
        if len(player.inventory.get_all_cards()) == 0 and (x, y) == (player.inventory.center_x, player.inventory.center_y):
            return True
        return False

    def is_first_card(self):
        # Checks if its the first card picked for the player
        current_player = self.game.players[self.game.current_player_index]
        return len(current_player.inventory.get_all_cards()) == 0

    def auto_place_first_card(self):
        # Place the first card picked automatically
        current_player = self.game.players[self.game.current_player_index]
        if len(current_player.inventory.get_all_cards()) == 0:
            center_x = current_player.inventory.center_x
            center_y = current_player.inventory.center_y
            current_player.inventory.add_card(self.selected_card, center_x, center_y, current_player.name)
            self.game.moon_marker_position = self.selected_card_position
            for i in range(len(self.game.card_board)):
                if self.game.card_board[i] == self.game.moon_marker:
                    self.game.card_board[i] = None
                    break
            self.game.card_board[self.selected_card_position] = self.game.moon_marker
            self.game.move_player(current_player, self.selected_card)
            self.selected_card = None
            self.selected_card_position = None
            self.update_board()
            self.game.check_inventory(current_player)
            self.refill_card_board_if_needed()
            if not self.game.is_game_over():
                self.game.turn_order.append(current_player.name)
                self.game.next_round()
                self.update_info()
                self.update_inventory()
            else:
                self.show_end_game_window()

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

    def refill_card_board_if_needed(self):
        # Refills the card board if needed/possible
        cards_on_board = sum(1 for card in self.game.card_board if card is not None and card != self.game.moon_marker)
        if cards_on_board == 0 and self.game.deck:
            for i in range(len(self.game.card_board)):
                if self.game.card_board[i] is None and self.game.deck:
                    self.game.card_board[i] = self.game.deck.pop()
            self.update_board()
        self.game.check_end_game()

    def deal_cards(self):
        # Manually refill the card board when "Deal" is clicked
        cards_on_board = sum(1 for card in self.game.card_board if card is not None and card != self.game.moon_marker)
        if cards_on_board < 3 and self.game.deck:
            for i in range(len(self.game.card_board)):
                if self.game.card_board[i] is None and self.game.deck:
                    self.game.card_board[i] = self.game.deck.pop()
            self.update_board()
        self.update_deal_button_state()  # Update the deal button state after dealing

    def show_end_game_window(self, scores):
        """Display the game over window."""
        if hasattr(self, 'after_id') and self.after_id:
            self.root.after_cancel(self.after_id)  # Cancel the scheduled after call
            self.after_id = None

        if self.inventory_window:
            self.inventory_window.destroy()
        if self.root:
            self.root.destroy()

        end_game_window = tk.Tk()
        end_game_window.title("Game Over")

        score_text = "Game Over\n\n"
        for name, score in scores.items():
            score_text += f"{name}: {score}\n"

        score_label = tk.Label(end_game_window, text=score_text, font=("Helvetica", 16))
        score_label.pack(pady=20)

        new_game_button = tk.Button(end_game_window, text="New Game", command=lambda: self.start_new_game(end_game_window))
        new_game_button.pack(pady=20)

        end_game_window.mainloop()

    def start_new_game(self, window):
        # Close the current window and start a new game
        window.destroy()
        app = NovaLunaGUI()  # Create a new instance of the NovaLunaGUI class
        app.run()

    def run(self):
        if self.root:
            self.root.mainloop()
        else:
            self.initialize_window.mainloop()

    def handle_ai_turn(self, current_player):
        # Disable user controls and show thinking message
        self.disable_user_controls()
        self.show_thinking_message()

        # **Safety Measure**
        # Check if there are 2 or fewer cards on the card board
        cards_on_board = sum(1 for card in self.game.card_board if card is not None and card != self.game.moon_marker)
        if cards_on_board <= 2 and self.game.deck:
            self.deal_cards()

        def ai_task():
            # Perform the AI computation in a separate thread
            move = get_ai_move(self.game, current_player, depth=4)  # Adjust depth as needed, 3 for default
            # Put the result into the queue
            self.ai_queue.put((current_player, move))

        # Start the AI computation in a separate thread
        threading.Thread(target=ai_task).start()


    def process_ai_queue(self):
        if self.game.simulation_mode or self.game.game_over:  # Stop processing if the game is over
            return
        try:
            current_player, move = self.ai_queue.get_nowait()
            self.process_ai_move(current_player, move)
        except queue.Empty:
            pass
        if self.root:
            # Store the after ID to allow cancellation later
            self.after_id = self.root.after(100, self.process_ai_queue)

    def cancel_after_calls(self):
        if hasattr(self, 'after_id') and self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def process_ai_move(self, current_player, move):
        # Hide the thinking message
        self.hide_thinking_message()

        if move:
            card_position, (x, y) = move
            card = self.game.card_board[card_position]
            if not self.fastmode_var.get():
                # Store the highlight position
                self.highlight_inventory_position(current_player, (x, y))

                # Always open or update the AI's inventory window
                self.open_inventory_window(player_index=self.game.players.index(current_player))

                # Display the picked card
                self.display_picked_card(card)
                # Show the "Next" button to proceed
                self.show_next_button(lambda: self.continue_ai_turn(current_player, move))
            else:
                # Fastmode is on; apply the move immediately
                self.game.apply_move(current_player, move)
                self.game.turn_order.append(current_player.name)
                self.game.next_round()
                self.update_board()
                self.update_info()
                self.update_inventory()
                # Re-enable user controls if the next player is human
                self.check_and_enable_user_controls()
        else:
            logger.info(f"{current_player.name} has no valid moves.")
            self.game.turn_order.append(current_player.name)
            self.game.next_round()
            # Re-enable user controls if the next player is human
            self.check_and_enable_user_controls()


    def continue_ai_turn(self, current_player, move):
        if move is not None:
            self.game.apply_move(current_player, move)
            current_player.inventory.highlight_position = None
            self.hide_next_button()
            self.game.turn_order.append(current_player.name)
            self.game.next_round()
            self.update_board()
            self.update_info()
            self.update_inventory()
            # Re-enable user controls if the next player is human
            self.check_and_enable_user_controls()
        else:
            logger.info(f"{current_player.name} has no valid moves.")
            self.hide_next_button()
            self.game.turn_order.append(current_player.name)
            self.game.next_round()
            # Re-enable user controls if the next player is human
            self.check_and_enable_user_controls()

    def highlight_inventory_position(self, player, position):
        # Store the highlight position in the player's inventory
        player.inventory.highlight_position = position
        # If the inventory window is open and it's the AI's inventory, redraw it
        if self.inventory_window and self.inventory_window.winfo_exists():
            if self.inventory_window_player_index == self.game.players.index(player):
                self.draw_inventory(None, self.inventory_canvas, player_index=self.inventory_window_player_index)


    def clear_ai_state(self):
        """Clear any state that might influence the AI's decision-making process."""
        # Reset any AI-specific temporary variables or flags if necessary.

    def display_picked_card(self, card):
        # Display the picked card on the canvas
        self.picked_card_canvas.delete("all")

        # Draw the card on the canvas
        self.picked_card_canvas.create_rectangle(10, 10, 90, 90, outline=card.color, width=4)
        self.picked_card_canvas.create_text(25, 25, text=str(card.movement), font=("Arial", 14))

        # Draw the tokens on the card
        if card.tokens:
            if len(card.tokens) > 0:
                token1 = card.tokens[0]
                self.draw_token(self.picked_card_canvas, 60, 15, token1)
            if len(card.tokens) > 1:
                token2 = card.tokens[1]
                self.draw_token(self.picked_card_canvas, 20, 60, token2)
            if len(card.tokens) > 2:
                token3 = card.tokens[2]
                self.draw_token(self.picked_card_canvas, 60, 60, token3)

    def draw_token(self, canvas, x, y, token):
        # Draw the tokens on the canvas at specified (x, y) position
        colors = []
        if token.red:
            colors.extend(['red'] * token.red)
        if token.green:
            colors.extend(['green'] * token.green)
        if token.blue:
            colors.extend(['blue'] * token.blue)
        if token.yellow:
            colors.extend(['yellow'] * token.yellow)
        for i, color in enumerate(colors):
            row = i // 2
            col = i % 2
            canvas.create_oval(x + col * 10, y + row * 10, x + 10 + col * 10, y + 10 + row * 10, fill=color)

    def show_next_button(self, command):
        # Create a Next button for advancing the AI's turn
        self.next_button = tk.Button(self.info_frame, text="Next", command=command)
        self.next_button.pack(side=tk.TOP, pady=10)


    def hide_next_button(self):
        if hasattr(self, 'next_button') and self.next_button.winfo_exists():
            self.next_button.destroy()

    def disable_user_controls(self):
        self.user_controls_enabled = False

    def enable_user_controls(self):
        self.user_controls_enabled = True

    def show_thinking_message(self):
        # Display a message indicating the AI is thinking
        self.thinking_label = tk.Label(self.root, text="AI is thinking...", font=("Arial", 16))
        self.thinking_label.pack(side=tk.TOP, pady=10)

    def hide_thinking_message(self):
        if hasattr(self, 'thinking_label') and self.thinking_label.winfo_exists():
            self.thinking_label.destroy()

    def check_and_enable_user_controls(self):
        next_player = self.game.players[self.game.current_player_index]
        if not next_player.is_ai:
            self.enable_user_controls()

    def check_simulation_toggle(self):
        # Enable the Simulation Mode checkbox only if all players are AI
        num_players = self.num_players_var.get()
        all_ai = all(self.ai_personality_vars[i].get() != "Human" for i in range(num_players))
        if all_ai:
            self.simulation_check.config(state=tk.NORMAL)
        else:
            self.simulation_check.config(state=tk.DISABLED)
            self.simulation_var.set(False)
            self.on_simulation_toggle()  # The number of simulations input is disabled by default

    def on_simulation_toggle(self):
        if self.simulation_var.get():
            # Enable number of simulations input
            self.num_simulations_entry.config(state='normal')
            self.num_simulations_label.config(fg='black')
            # Disable Fastmode during simulation(it's fastmode either way during simulation)
            self.fastmode_check.config(state=tk.DISABLED)
        else:
            # Disable number of simulations input
            self.num_simulations_entry.config(state='disabled')
            self.num_simulations_label.config(fg='grey')
            # Re-enable Fastmode
            self.fastmode_check.config(state=tk.NORMAL)

    def run_simulations(self, num_simulations, goal):
        max_concurrent_simulations = min(cpu_count(), 10)  # Cap at 10 or the number of CPU cores
        num_players = self.num_players_var.get()
        ai_personalities = [var.get() for var in self.ai_personality_vars]
        is_single_simulation = num_simulations == 1

        logger.info(f"Running simulation{'...' if is_single_simulation else f's with up to {max_concurrent_simulations} processes...'}")

        per_player_data = []
        per_turn_data = []

        if is_single_simulation:
            stats = run_single_simulation(1, num_players, goal, ai_personalities, is_single_simulation)
            player_data, turn_data = stats
            per_player_data.extend(player_data)
            per_turn_data.extend(turn_data)
        else:
            with Pool(processes=max_concurrent_simulations) as pool:
                # Prepare arguments for the worker function
                simulation_args = [
                    (i, num_players, goal, ai_personalities, is_single_simulation)
                    for i in range(1, num_simulations + 1)
                ]
                # Run simulations in parallel
                for i, (player_data, turn_data) in enumerate(pool.starmap(run_single_simulation, simulation_args), 1):
                    print(f"Simulation {i}/{num_simulations} complete")
                    per_player_data.extend(player_data)
                    per_turn_data.extend(turn_data)

        # Save results to CSV
        self.save_per_player_data_to_csv(per_player_data)
        self.save_per_turn_data_to_csv(per_turn_data)

        print("Simulations complete. Data saved to simulations.csv and thinking_times.csv.")

    def save_per_player_data_to_csv(self, data):
        if not data:
            return
        keys = ['game_number', 'winner_name', 'winner_ai_type', 'game_length', 'player_name', 'player_ai_type', 'average_score_per_turn', 'average_move_cost']
        with open('simulations.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            for row in data:
                csv_row = {
                    'game_number': row['game_number'],
                    'winner_name': row['winner_name'],
                    'winner_ai_type': row['winner_ai_type'],
                    'game_length': row['game_length'],
                    'player_name': row['player_name'],
                    'player_ai_type': row['player_ai_type'],
                    'average_score_per_turn': "{:.2f}".format(row['average_score_per_turn']),
                    'average_move_cost': "{:.2f}".format(row['average_move_cost']),
                }
                dict_writer.writerow(csv_row)

    def save_data_to_csv(self, data):
        if not data:
            return
        # Define the fields explicitly
        keys = ['game_number', 'winner', 'average_score_per_turn', 'game_length', 'average_move_cost']
        with open('simulations.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            for game_data in data:
                csv_row = {
                    'game_number': game_data['game_number'],
                    'winner': str(game_data['winner']),  # Convert winner to string explicitly
                    'average_score_per_turn': f"{game_data.get('average_score_per_turn', 0):.2f}",  # Format to 2 decimals
                    'game_length': game_data['game_length'],
                    'average_move_cost': f"{game_data.get('average_move_cost', 0):.2f}",  # Format to 2 decimals
                }
                dict_writer.writerow(csv_row)

    def save_per_turn_data_to_csv(self, data):
        if not data:
            return
        keys = data[0].keys()
        with open('thinking_times.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            for row in data:
                # Format the turn time
                turn_time = float(row['turn_time'])
                if turn_time < 1:
                    row['turn_time'] = "{:.2f}".format(turn_time)
                else:
                    row['turn_time'] = "{:.0f}".format(turn_time)
                dict_writer.writerow(row)


    def run(self):
        if self.root:
            self.root.mainloop()
        else:
            self.initialize_window.mainloop()



def run_single_simulation(simulation_id, num_players, goal, ai_personalities, is_single_simulation):
    """
    Run a single simulation and return its data.
    """
    try:
        # Initialize game
        game = Game(num_players=num_players, goal=goal, gui=None, simulation_mode=True, is_single_simulation=is_single_simulation, game_number=simulation_id)
        for j, player in enumerate(game.players):
            player.is_ai = True
            player.ai_personality = ai_personalities[j]

        # Run the simulation
        game.simulate_game()

        # Collect per-player data
        winner_name = game.statistics.get('winner', 'No Winner')
        winner_ai_type = game.statistics.get('winner_ai_type', 'Unknown')
        game_length = game.statistics.get('game_length', 0)
        simulation_player_data = []
        for player in game.players:
            num_turns = len(game.statistics['turn_times'][player.name])
            avg_score_per_turn = player.score / num_turns if num_turns > 0 else 0
            avg_move_cost = (
                sum(game.statistics['move_costs'][player.name]) / num_turns if num_turns > 0 else 0
            )
            simulation_player_data.append({
                'game_number': simulation_id,
                'player_name': player.name,
                'player_ai_type': player.ai_personality,
                'winner_name': winner_name,
                'winner_ai_type': winner_ai_type,
                'game_length': game_length,
                'average_score_per_turn': round(avg_score_per_turn, 2),
                'average_move_cost': round(avg_move_cost, 2)
            })

        # Collect per-turn data
        simulation_turn_data = game.statistics['per_turn_data']

        return simulation_player_data, simulation_turn_data

    finally:
        # Cleanup game instance
        del game
        gc.collect()