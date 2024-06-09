# Card.py

from Token import Token

class Card:
    # A kártya classja, tartalmazza hogy hány lépésbe kerül a kártya, a színét, és maximum 3 token-t ami reprezentálja a küldetéseket
    def __init__(self, color, movement, tokens):
        self.color = color  # Kártya színe
        self.movement = movement  # Kártya lépés értéke
        self.tokens = tokens[:3]  # A kártyán lévő küldetés tokenek, max 3