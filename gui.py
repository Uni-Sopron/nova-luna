import tkinter as tk
from tkinter import ttk
from main import Game

class NovaLunaGUI:
    def __init__(self, root):
        # GUI inicializálása
        self.root = root
        self.root.title("Nova Luna")
        self.game = Game(4)
        self.selected_card = None
        self.selected_card_position = None
        self.available_positions = []
        self.inventory_window = None
        self.create_widgets()
        self.update_board()
        self.update_info()
        self.game.turn_order.append(self.game.players[0].name)

    def create_widgets(self):
        # GUI elemek létrehozása
        self.canvas = tk.Canvas(self.root, width=1200, height=800)
        self.canvas.pack()

        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack()

        self.player_turn_label = tk.Label(self.info_frame, text="")
        self.player_turn_label.pack(side=tk.LEFT, padx=20)

        self.score_label = tk.Label(self.info_frame, text="")
        self.score_label.pack(side=tk.RIGHT, padx=20)

        self.inventory_button = tk.Button(self.root, text="Inventory", command=self.open_inventory_window)
        self.inventory_button.pack(pady=10)

    def update_board(self):
        # Játék tábla frissítése
        self.canvas.delete("all")
        self.draw_player_board()
        self.draw_card_board()
        self.canvas.update()

    def draw_player_board(self):
        # Játékos tábla megjelenítése
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
            for index, player in enumerate(players):
                pos_x, pos_y = positions[index]
                self.canvas.create_oval(x0 + pos_x, y0 + pos_y, x0 + pos_x + 20, y0 + pos_y + 20, fill=player.color)
                text_color = 'black' if player.name in ['Player1', 'Player4'] else 'white'
                self.canvas.create_text(x0 + pos_x + 10, y0 + pos_y + 10, text=player.name[-1], fill=text_color)

    def get_player_positions(self, num_players):
        # Játékos pozíciók meghatározása (Ezt dinamikus megjelenítéshez használjuk)
        positions = {
            1: [(20, 20)],
            2: [(5, 5), (35, 35)],
            3: [(20, 5), (5, 35), (35, 35)],
            4: [(5, 5), (35, 5), (5, 35), (35, 35)]
        }
        return positions.get(num_players, [])

    def draw_card_board(self):
        # Kártya tábla megjelenítése
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
                self.canvas.create_rectangle(x0, y0, x1, y1, outline=outline_color, width=2)
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
        # Tokenek megjelenítése
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

    def on_card_click(self, card_position):
        # Kártya felhúzásának kezelése
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

    def open_inventory_window(self):
        # Inventory ablak megnyitása
        if self.inventory_window and self.inventory_window.winfo_exists():
            return

        self.inventory_window = tk.Toplevel(self.root)
        self.inventory_window.title("Inventory")

        inventory_frame = ttk.Frame(self.inventory_window)
        inventory_frame.pack(fill=tk.BOTH, expand=True)

        inventory_canvas = tk.Canvas(inventory_frame)
        inventory_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_x = ttk.Scrollbar(inventory_frame, orient=tk.HORIZONTAL, command=inventory_canvas.xview)
        scrollbar_y = ttk.Scrollbar(inventory_frame, orient=tk.VERTICAL, command=inventory_canvas.yview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        inventory_canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
        inventory_canvas.bind('<Configure>', lambda e: inventory_canvas.configure(scrollregion=inventory_canvas.bbox('all')))

        inventory_inner_frame = ttk.Frame(inventory_canvas)
        inventory_canvas.create_window((0, 0), window=inventory_inner_frame, anchor='nw')

        self.draw_inventory(inventory_inner_frame, inventory_canvas)
        self.center_inventory_view(inventory_canvas)

    def center_inventory_view(self, inventory_canvas):
        # Inventory ablak igazíttása
        self.root.update_idletasks()
        canvas_width = inventory_canvas.winfo_width()
        canvas_height = inventory_canvas.winfo_height()

        center_x = self.game.players[self.game.current_player_index].inventory.center_x * 65 - canvas_width // 2
        center_y = self.game.players[self.game.current_player_index].inventory.center_y * 65 - canvas_height // 2

        inventory_canvas.xview_moveto(center_x / inventory_canvas.bbox("all")[2])
        inventory_canvas.yview_moveto(center_y / inventory_canvas.bbox("all")[3])

    def draw_inventory(self, inventory_frame, inventory_canvas):
        # Inventory megjelenítése
        inventory_canvas.delete("all")
        current_player = self.game.players[self.game.current_player_index]
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
                    inventory_canvas.create_rectangle(x0, y0, x1, y1, outline=card.color, width=2)
                    inventory_canvas.create_text(x0 + 10, y0 + 10, text=str(card.movement), anchor='nw', font=("Helvetica", 12))
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

    def on_inventory_click(self, grid_position, inventory_canvas):
        # Inventory klikkelés lekezelése
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
                    self.update_inventory_display()
                else:
                    self.show_end_game_window()
            except ValueError:
                print("Invalid input. Please click a valid grid position.")
        else:
            print("Invalid placement. Please place the card adjacent to an existing card.")

    def update_inventory_display(self):
        # Inventory ablak frissítése
        if self.inventory_window and self.inventory_window.winfo_exists():
            inventory_canvas = self.inventory_window.winfo_children()[0].winfo_children()[0]
            self.draw_inventory(inventory_canvas, inventory_canvas)

    def is_valid_placement(self, player, x, y):
        # Lehetséges (engedélyezett) kártya helyének ellenőrzése
        adjacent_positions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for ax, ay in adjacent_positions:
            if player.inventory.get_card(ax, ay) is not None:
                return True
        if len(player.inventory.get_all_cards()) == 0 and (x, y) == (player.inventory.center_x, player.inventory.center_y):
            return True
        return False

    def is_first_card(self):
        # Megnézi hogy ez-e az első kártyája a játékosnak
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
                self.update_inventory_display()
            else:
                self.show_end_game_window()

    def get_available_card_positions(self):
        # Lehetséges (engedélyezett) kártyapozíciók meghatározása a kártya paklin felhúzásra
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

    def update_info(self):
        # Információ gui frissítése
        current_player = self.game.players[self.game.current_player_index]
        self.player_turn_label.config(text=f"{current_player.name}'s turn")
        score_text = "Score:\n"
        for player in self.game.players:
            score_text += f"{player.name}: {player.score}\n"
        self.score_label.config(text=score_text)

    def check_inventory(self, player):
        # Token küldetések leelenörzése
        for card, x, y in player.inventory.get_all_cards():
            for token in card.tokens:
                if not token.is_completed:
                    self.check_token_completion(player, card, token, x, y)

    def check_token_completion(self, player, card, token, x, y):
        # Token küldetés teljesítésének ellenőrzése
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
                return

        token.is_completed = True
        player.score += 1
        print(f"{player.name} completed a token! New score: {player.score}")

    def refill_card_board_if_needed(self):
        # Kártya tábla újraosztása, ha teljesül a kondíció
        cards_on_board = sum(1 for card in self.game.card_board if card is not None and card != self.game.moon_marker)
        if cards_on_board < 3 and self.game.deck:
            for i in range(len(self.game.card_board)):
                if self.game.card_board[i] is None and self.game.deck:
                    self.game.card_board[i] = self.game.deck.pop()
            self.update_board()
        self.game.check_end_game()

    def show_end_game_window(self):
        # Game Over ablak megjelenítése
        if self.inventory_window:
            self.inventory_window.destroy()
        self.root.destroy()

        end_game_window = tk.Tk()
        end_game_window.title("Game Over")

        scores = sorted([(player.name, player.score) for player in self.game.players], key=lambda x: x[1], reverse=True)
        score_text = "Game Over\n\n"
        for name, score in scores:
            score_text += f"{name}: {score}\n"

        score_label = tk.Label(end_game_window, text=score_text, font=("Helvetica", 16))
        score_label.pack(pady=20)

        new_game_button = tk.Button(end_game_window, text="New Game", command=lambda: self.start_new_game(end_game_window))
        new_game_button.pack(pady=20)

        end_game_window.mainloop()

    def start_new_game(self, window):
        # New Game lekezelése
        window.destroy()
        root = tk.Tk()
        app = NovaLunaGUI(root)
        app.run()

    def run(self):
        # GUI futtatása
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = NovaLunaGUI(root)
    app.run()
