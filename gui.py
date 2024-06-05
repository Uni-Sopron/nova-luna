# gui.py

import tkinter as tk
from main import Game

class NovaLunaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nova Luna")
        self.game = Game()
        self.game.init_game(2)  # 2 játékos kezdnésnek

        self.create_widgets()
        self.update_board()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack()

        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack()

        self.player_info = tk.Label(self.info_frame, text="Player Info")
        self.player_info.pack()

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()

        self.next_turn_button = tk.Button(self.button_frame, text="Next Turn", command=self.next_turn)
        self.next_turn_button.pack()

        self.select_card_button = tk.Button(self.button_frame, text="Select Card", command=self.select_card)
        self.select_card_button.pack()

        self.x_entry = tk.Entry(self.button_frame)
        self.x_entry.pack()
        self.x_entry.insert(0, "X Coordinate")

        self.y_entry = tk.Entry(self.button_frame)
        self.y_entry.pack()
        self.y_entry.insert(0, "Y Coordinate")

    def update_board(self):
        self.canvas.delete("all")
        self.draw_player_board()
        self.draw_card_board()

    def draw_player_board(self):
        size = 20  # Minden játékos helyének a mérete
        center_x = 400
        center_y = 300
        radius = 150

        for i in range(len(self.game.board)):
            angle = 2 * 3.14159 * i / len(self.game.board)
            x0 = center_x + radius * 1.5 * (1 + 1.2 * i / len(self.game.board)) * 0.5 * 3.14159 * 1
            y0 = center_y + radius * 1.5 * (1 + 1.2 * i / len(self.game.board)) * 0.5 * 3.14159 * 1
            x1 = x0 + size
            y1 = y0 + size
            self.canvas.create_oval(x0, y0, x1, y1, fill='lightgrey')
            for player in self.game.board[i]:
                self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=player.name[0], fill=player.color)

    def draw_card_board(self):
        size = 40  # Minden kártya helyének a mérete
        center_x = 400
        center_y = 300
        radius = 200

        for i in range(len(self.game.card_board)):
            angle = 2 * 3.14159 * i / len(self.game.card_board)
            x0 = center_x + radius * (1 + 1.2 * i / len(self.game.card_board)) * 0.5 * 3.14159 * 1
            y0 = center_y + radius * (1 + 1.2 * i / len(self.game.card_board)) * 0.5 * 3.14159 * 1
            x1 = x0 + size
            y1 = y0 + size
            fill_color = 'lightblue' if self.game.card_board[i] is not None else 'white'
            if self.game.card_board[i] == self.game.moon_marker:
                fill_color = 'yellow'
            self.canvas.create_oval(x0, y0, x1, y1, fill=fill_color)
            if self.game.card_board[i] is not None and self.game.card_board[i] != self.game.moon_marker:
                self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=str(self.game.card_board[i].movement))

    def next_turn(self):
        self.game.next_round()
        self.update_board()

    def select_card(self):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            available_positions = self.game.get_available_card_positions()
            if available_positions:
                card_position = available_positions[0]  # Jelenleg csak az első kártyát válasszuk
                player = self.game.players[self.game.current_player_index]
                self.game.draw(player, card_position, x, y)
                self.update_board()
        except ValueError:
            print("Invalid input. Please enter valid coordinates.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NovaLunaGUI(root)
    root.mainloop()
