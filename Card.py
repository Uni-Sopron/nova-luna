# Card.py

from Token import Token

class Card:
    # Represents a card in the game with a specific color, movement cost, and up to 3 tokens.

    def __init__(self, color, movement, tokens):
        # Initialize the card with a color, movement cost, and associated tokens.
        self.color = color
        self.movement = movement
        self.tokens = tokens[:3]  # Limit tokens to a maximum of 3

    def is_complete(self):
        # Check if all tokens on the card are completed.
        return all(token.is_completed for token in self.tokens)

    def __str__(self):
        return f"Card(color={self.color}, movement={self.movement}, tokens={self.tokens})"

    def __repr__(self):
        return self.__str__()