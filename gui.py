import tkinter as tk
from tkinter import ttk
from main import Game

class NovaLunaGUI:
    def __init__(self):
        self.root = None  # The main game window will be created later
        self.initialize_window = tk.Tk()
        self.initialize_window.title("Game Setup")
        self.ai_vars = []
        self.num_players_var = tk.IntVar(value=4)
        self.goal_var = tk.IntVar(value=20)
        self.fastmode_var = tk.BooleanVar(value=True)  # Variable to store Fastmode status
        self.create_initialize_window()

    def create_initialize_window(self):
        # Create the initialization window
        self.initialize_window.geometry("400x350")  # Set a wider default size

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
        goal_entry = tk.Entry(self.initialize_window, textvariable=self.goal_var)
        goal_entry.pack(pady=5)

        ai_frame = tk.Frame(self.initialize_window)
        ai_frame.pack(pady=10)

        tk.Label(ai_frame, text="AI Toggle:").grid(row=0, column=0, padx=10)

        for i in range(4):
            var = tk.BooleanVar(value=False)
            self.ai_vars.append(var)
            check = tk.Checkbutton(
                ai_frame,
                text=f"Player {i + 1}",
                variable=var,
                state=tk.NORMAL if i < self.num_players_var.get() else tk.DISABLED
            )
            check.grid(row=i + 1, column=0, padx=5, sticky='w')

        def update_ai_toggle_state(*args):
            for i in range(4):
                check = ai_frame.grid_slaves(row=i + 1, column=0)[0]
                if i < self.num_players_var.get():
                    check.config(state=tk.NORMAL)
                else:
                    check.config(state=tk.DISABLED)
                    self.ai_vars[i].set(False)

        self.num_players_var.trace("w", update_ai_toggle_state)

        # Fastmode Checkbox
        fastmode_check = tk.Checkbutton(
            self.initialize_window,
            text="Fastmode",
            variable=self.fastmode_var
        )
        fastmode_check.pack(pady=10)

        start_button = tk.Button(self.initialize_window, text="Start", command=self.start_game)
        start_button.pack(pady=10)

    def start_game(self):
        num_players = self.num_players_var.get()
        goal = self.goal_var.get()
        fastmode = self.fastmode_var.get()  # Get the Fastmode status

        print(f"Fastmode is {'enabled' if fastmode else 'disabled'}")  # Debug print for Fastmode status

        self.game = Game(num_players, goal)

        for i in range(num_players):
            self.game.players[i].is_ai = self.ai_vars[i].get()

        self.initialize_window.destroy()  # Destroy the setup window
        self.initialize_game()

    def initialize_game(self):
        # Create the main game window now
        self.root = tk.Tk()
        self.root.title("Nova Luna")
        
        self.selected_card = None
        self.selected_card_position = None
        self.available_positions = []
        self.inventory_window = None
        self.all_players_moved = False  # Initialize this attribute

        # Reinitialize ai_vars based on the actual game state
        self.ai_vars = [tk.BooleanVar(value=player.is_ai) for player in self.game.players]

        self.create_widgets()
        self.update_board()
        self.update_info()
        self.game.turn_order.append(self.game.players[0].name)
        self.game.set_gui(self)
        
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

        # Initial empty labels for scores, we'll update them later
        self.score_labels = []
        for player in self.game.players:
            player_label = tk.Label(self.scores_frame, text="")
            player_label.pack(anchor='w', pady=2)
            self.score_labels.append(player_label)

        # Card shape to display remaining cards
        self.card_canvas = tk.Canvas(self.info_frame, width=100, height=150)
        self.card_canvas.pack(side=tk.RIGHT, padx=20)
        self.card_rectangle = self.card_canvas.create_rectangle(10, 10, 90, 140, outline="black", width=2)
        self.card_text = self.card_canvas.create_text(50, 75, text=str(self.game.get_remaining_cards()), font=("Arial", 20))

        # Create inventory buttons with colored outlines
        if len(self.game.players) > 0:
            self.inventory_button = self.create_inventory_button("Player1", 0)
            self.inventory_button.pack(pady=5)
        if len(self.game.players) > 1:
            self.player2_inventory_button = self.create_inventory_button("Player2", 1)
            self.player2_inventory_button.pack(pady=5, side=tk.LEFT)
        if len(self.game.players) > 2:
            self.player3_inventory_button = self.create_inventory_button("Player3", 2)
            self.player3_inventory_button.pack(pady=5, side=tk.LEFT)
        if len(self.game.players) > 3:
            self.player4_inventory_button = self.create_inventory_button("Player4", 3)
            self.player4_inventory_button.pack(pady=5, side=tk.LEFT)

        # AI toggle controls
        ai_frame = tk.Frame(self.root)
        ai_frame.pack(pady=10)

        ai_label = tk.Label(ai_frame, text="AI Toggle")
        ai_label.pack(side=tk.LEFT, padx=10)

        # Create checkbuttons for each player to toggle AI control
        for i, player in enumerate(self.game.players):
            player_check = tk.Checkbutton(
                ai_frame, 
                text=f"Player{i+1}", 
                variable=self.ai_vars[i], 
                command=lambda i=i: self.toggle_ai(i)
            )
            player_check.pack(side=tk.LEFT, padx=5)

    def toggle_ai(self, player_index):
        # Toggle the AI control for the selected player
        is_ai = self.ai_vars[player_index].get()
        self.game.players[player_index].is_ai = is_ai
        print(f"Player {player_index+1} AI status changed to {is_ai}")

    def create_inventory_button(self, player_name, player_index):
        fg_color = "black" if player_index in [0, 2] else "white"
        button = tk.Button(
            self.root,
            text=f"{player_name} Inventory",
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
        self.update_info # Update player info, including scores
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
        # Kártya tábla rajzolása
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
        # Tokenek rajzolása
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
        # Kártyára kattintás lekezelése
        if self.selected_card is None:
            self.available_positions = self.get_available_card_positions()

        if card_position not in self.available_positions:
            print("Invalid card selection. Please select a card within the first three positions from the moon marker.")
            return

        if card_position in self.available_positions:
            if self.selected_card is not None and self.selected_card_position is not None:
                self.game.card_board[self.selected_card_position] = self.selected_card
            self.selected_card_position = card_position
            self.selected_card = self.game.card_board[card_position]
            self.game.card_board[card_position] = None
            self.update_board()
            if self.is_first_card():
                self.auto_place_first_card()
            else:
                if not self.inventory_window or not self.inventory_window.winfo_exists():
                    self.open_inventory_window()
        else:
            print("Invalid card selection. Please select a card within the first three positions from the moon marker.")

    def open_inventory_window(self, player_index=None):
        # If the inventory window already exists, update its content instead of returning
        if self.inventory_window and self.inventory_window.winfo_exists():
            # Access the existing canvas and clear its content
            inventory_frame = self.inventory_window.winfo_children()[0]
            inventory_canvas = inventory_frame.winfo_children()[0]
            inventory_canvas.delete("all")
            
            # Redraw the inventory for the new player index
            self.draw_inventory(inventory_frame, inventory_canvas, player_index)
            
            # Re-center the view based on the new content
            self.center_inventory_view(inventory_canvas)
        else:
            # Create a new inventory window if it doesn't exist
            self.inventory_window = tk.Toplevel(self.root)
            self.inventory_window.title("Inventory")

            inventory_frame = ttk.Frame(self.inventory_window)
            inventory_frame.pack(fill=tk.BOTH, expand=True)

            inventory_canvas = tk.Canvas(inventory_frame)
            inventory_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Create scrollbars and attach them to the inventory frame and canvas
            scrollbar_y = ttk.Scrollbar(inventory_frame, orient=tk.VERTICAL, command=inventory_canvas.yview)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

            scrollbar_x = ttk.Scrollbar(self.inventory_window, orient=tk.HORIZONTAL, command=inventory_canvas.xview)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

            inventory_canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

            inventory_inner_frame = ttk.Frame(inventory_canvas)
            inventory_canvas.create_window((0, 0), window=inventory_inner_frame, anchor='nw')

            self.draw_inventory(inventory_inner_frame, inventory_canvas, player_index)
            self.center_inventory_view(inventory_canvas)



    def center_inventory_view(self, inventory_canvas):
        # Inventory nézet igazítása
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
        # Inventory megrajzolása
        inventory_canvas.delete("all")
        if player_index is None:
            current_player = self.game.players[self.game.current_player_index]
        else:
            current_player = self.game.players[player_index]
        
        size = 60
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
        inventory_canvas.update_idletasks()  # Ensure all pending tasks are complete before updating
        inventory_canvas.configure(scrollregion=inventory_canvas.bbox("all"))

    def on_inventory_click(self, grid_position, inventory_canvas):
        # Inventory-n belül kattintás lekezelése
        if self.selected_card is None:
            print("Select a card first")
            return
        player = self.game.players[self.game.current_player_index]
        x, y = grid_position
        if self.is_valid_placement(player, x, y):
            try:
                player.inventory.add_card(self.selected_card, x, y)
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
                self.check_inventory(player)
                self.refill_card_board_if_needed()
                if not self.game.is_game_over():
                    self.game.turn_order.append(player.name)
                    self.game.next_round()
                    self.update_info()
                    self.update_inventory()
                else:
                    self.show_end_game_window()
            except ValueError:
                print("Invalid input. Please click a valid grid position.")
        else:
            print("Invalid placement. Please place the card adjacent to an existing card.")

    def update_inventory(self):
        # Inventory frissítése
        if self.inventory_window and self.inventory_window.winfo_exists():
            inventory_canvas = self.inventory_window.winfo_children()[0].winfo_children()[0]
            self.draw_inventory(inventory_canvas, inventory_canvas)

    def update_info(self):
        # Clear the current display
        for widget in self.scores_frame.winfo_children():
            widget.destroy()

        # Update the current player's turn display
        current_player = self.game.players[self.game.current_player_index]

        # Update or create the player's token as a small oval next to the turn text
        if hasattr(self, 'turn_token_canvas'):
            # Update existing token
            self.turn_token_canvas.delete("all")
            self.turn_token_canvas.create_oval(2, 2, 18, 18, fill=current_player.color)
        else:
            # Create new token
            self.turn_token_canvas = tk.Canvas(self.turn_and_score_frame, width=20, height=20)
            self.turn_token_canvas.pack(side=tk.LEFT, padx=(0, 5))  # Add a little space between token and text
            self.turn_token_canvas.create_oval(2, 2, 18, 18, fill=current_player.color)

        # Update the player's turn label text
        self.player_turn_label.config(text=f"{current_player.name}'s turn")

        # Update scores for each player with a token next to the score
        for i, player in enumerate(self.game.players):
            # Create a frame for each player's score and token
            player_frame = tk.Frame(self.scores_frame)
            player_frame.pack(anchor='w', pady=2)

            # Draw the player's token as a small oval
            token_canvas = tk.Canvas(player_frame, width=20, height=20)
            token_canvas.pack(side=tk.LEFT)
            token_canvas.create_oval(2, 2, 18, 18, fill=player.color)

            # Display the player's score next to the token
            score_text = f"{player.name}: {player.score}/{self.game.goal}"
            player_label = tk.Label(player_frame, text=score_text)
            player_label.pack(side=tk.LEFT)

        # Ensure the card display remains on the right side
        self.card_canvas.pack(side=tk.RIGHT, padx=20)


    def update_card_count(self):
        # Update the text in the card-shaped rectangle
        self.card_canvas.itemconfig(self.card_text, text=str(self.game.get_remaining_cards()))

    def is_valid_placement(self, player, x, y):
        # Érvényes kártya letevés ellenörzése
        adjacent_positions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for ax, ay in adjacent_positions:
            if player.inventory.get_card(ax, ay) is not None:
                return True
        if len(player.inventory.get_all_cards()) == 0 and (x, y) == (player.inventory.center_x, player.inventory.center_y):
            return True
        return False

    def is_first_card(self):
        # Első kártyája-e
        current_player = self.game.players[self.game.current_player_index]
        return len(current_player.inventory.get_all_cards()) == 0

    def auto_place_first_card(self):
        # Első kártya automatikus lehelyezése
        current_player = self.game.players[self.game.current_player_index]
        if len(current_player.inventory.get_all_cards()) == 0:
            center_x = current_player.inventory.center_x
            center_y = current_player.inventory.center_y
            current_player.inventory.add_card(self.selected_card, center_x, center_y)
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
            self.check_inventory(current_player)
            self.refill_card_board_if_needed()
            if not self.game.is_game_over():
                self.game.turn_order.append(current_player.name)
                self.game.next_round()
                self.update_info()
                self.update_inventory()
            else:
                self.show_end_game_window()

    def get_available_card_positions(self):
        # Lehetséges üres kártyahelyek megkeresése
        current_position = self.game.moon_marker_position
        positions = []
        count = 0
        total_cards = sum(1 for card in self.game.card_board if card is not None and card != self.game.moon_marker)
        if total_cards < 3:
            for i in range(len(self.game.card_board)):
                if self.game.card_board[i] is not None and self.game.card_board[i] != self.game.moon_marker:
                    positions.append(i)
            return positions
        while count < 3:
            current_position = (current_position + 1) % len(self.game.card_board)
            if self.game.card_board[current_position] is not None and self.game.card_board[current_position] != self.game.moon_marker:
                positions.append(current_position)
                count += 1
        return positions

    def check_inventory(self, player):
        # Inventorik ellenőrzése küldetések teljesülésére
        for card, x, y in player.inventory.get_all_cards():
            for token in card.tokens:
                if not token.is_completed:
                    self.check_token_completion(player, card, token, x, y)

    def check_token_completion(self, player, card, token, x, y):
        # Token küldetés teljesítésének ellenőrzése
        print(f"GUI Checking token completion for {player.name}: {token.__dict__}")
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
                print(f"GUI Token not completed for {player.name}: needed {required_count} {color}, found {counts[color]}")
                return

        token.is_completed = True
        player.score += 1
        print(f"GUI {player.name} completed a token! New score: {player.score}")

    def refill_card_board_if_needed(self):
        # Kártya tábla újraosztása
        cards_on_board = sum(1 for card in self.game.card_board if card is not None and card != self.game.moon_marker)
        if cards_on_board < 3 and self.game.deck:
            for i in range(len(self.game.card_board)):
                if self.game.card_board[i] is None and self.game.deck:
                    self.game.card_board[i] = self.game.deck.pop()
            self.update_board()
        self.game.check_end_game()

    def show_end_game_window(self, scores):
        # Display the game over window
        if self.inventory_window:
            self.inventory_window.destroy()
        self.root.destroy()

        end_game_window = tk.Tk()
        end_game_window.title("Game Over")

        score_text = "Game Over\n\n"
        for name, score in scores:
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

if __name__ == "__main__":
    app = NovaLunaGUI()
    app.run()