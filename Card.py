from Token import Token

class Card:
    # Egy kártyának van maximum 3 tokenje, színje, és egy mozgás értéke

    def __init__(self, color, movement, tokens):
        # Kártya konstruktor
        self.color = color
        self.movement = movement
        self.tokens = tokens[:3]  # Maximum 3 tokenje lehet

    def is_complete(self):
        # Ellenörzi hogy minden token teljesült-e
        return all(token.is_completed for token in self.tokens)

    def __str__(self):
        return f"Card(color={self.color}, movement={self.movement}, tokens={self.tokens})"

    def __repr__(self):
        return self.__str__()