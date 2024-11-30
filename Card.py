from Token import Token

class Card:
    # A card has a maximum of 3 tokens, has color, and has a movement cost

    def __init__(self, color, movement, tokens):
        # Card constructor
        self.color = color
        self.movement = movement
        self.tokens = tokens[:3]  # Maximum 3 tokens

    def is_complete(self):
        # Checks if all tokens are completed
        return all(token.is_completed for token in self.tokens)

    def __str__(self):
        return f"Card(color={self.color}, movement={self.movement}, tokens={self.tokens})"

    def __repr__(self):
        return self.__str__()