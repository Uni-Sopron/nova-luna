from Card import Card
import random
from Token import Token, generate_token_combinations, get_token_with_colors

# Minden lehetséges használható tokent tartalmazó lista feltöltése
all_tokens = generate_token_combinations()

""" Használati példa:
token = get_token_with_colors(red_count=2, green_count=1, blue_count=1)
print(token.red)    # Output: 2
print(token.green)  # Output: 1
print(token.blue)   # Output: 1
print(token.yellow) # Output: None """


# Kártyák kilistázása, 3 token kártyánként maximum(igen ezt egy jó idő volt bepötyögni)
CARD_DATA = [
    {"color": "red", "movement": 1, "tokens": []}, # Az 1 lépéses kártyáknak nincs küldetés tokenje
    {"color": "red", "movement": 2, "tokens": [get_token_with_colors(red_count=4)]},
    {"color": "red", "movement": 2, "tokens": [get_token_with_colors(red_count=4)]},
    {"color": "red", "movement": 3, "tokens": [get_token_with_colors(red_count=1, green_count=1, blue_count=1)]},
    {"color": "red", "movement": 3, "tokens": [get_token_with_colors(red_count=2, blue_count=1)]},
    {"color": "red", "movement": 3, "tokens": [get_token_with_colors(green_count=2, yellow_count=1)]},
    {"color": "red", "movement": 3, "tokens": [get_token_with_colors(red_count=1, green_count=1, blue_count=1, yellow_count=1), get_token_with_colors(green_count=3)]},
    {"color": "red", "movement": 4, "tokens": [get_token_with_colors(red_count=1, green_count=1), get_token_with_colors(blue_count=1, yellow_count=1)]},
    {"color": "red", "movement": 4, "tokens": [get_token_with_colors(yellow_count=4), get_token_with_colors(yellow_count=2)]},
    {"color": "red", "movement": 4, "tokens": [get_token_with_colors(red_count=3), get_token_with_colors(green_count=1, yellow_count=1)]},
    {"color": "red", "movement": 4, "tokens": [get_token_with_colors(blue_count=3), get_token_with_colors(yellow_count=3), get_token_with_colors(green_count=2)]},
    {"color": "red", "movement": 5, "tokens": [get_token_with_colors(blue_count=3), get_token_with_colors(blue_count=1)]},
    {"color": "red", "movement": 5, "tokens": [get_token_with_colors(blue_count=2), get_token_with_colors(yellow_count=1)]},
    {"color": "red", "movement": 5, "tokens": [get_token_with_colors(green_count=2), get_token_with_colors(red_count=2), get_token_with_colors(blue_count=2)]},
    {"color": "red", "movement": 6, "tokens": [get_token_with_colors(green_count=3), get_token_with_colors(green_count=1, yellow_count=1), get_token_with_colors(yellow_count=2)]},
    {"color": "red", "movement": 6, "tokens": [get_token_with_colors(blue_count=2), get_token_with_colors(yellow_count=2), get_token_with_colors(green_count=1)]},
    {"color": "red", "movement": 7, "tokens": [get_token_with_colors(green_count=1, blue_count=1), get_token_with_colors(green_count=1, yellow_count=1), get_token_with_colors(blue_count=1, yellow_count=1)]},  
    {"color": "green", "movement": 1, "tokens": []},
    {"color": "green", "movement": 2, "tokens": [get_token_with_colors(green_count=4)]},
    {"color": "green", "movement": 2, "tokens": [get_token_with_colors(green_count=4)]},
    {"color": "green", "movement": 3, "tokens": [get_token_with_colors(red_count=1, green_count=1, yellow_count=1)]},
    {"color": "green", "movement": 3, "tokens": [get_token_with_colors(blue_count=1, yellow_count=2)]},
    {"color": "green", "movement": 3, "tokens": [get_token_with_colors(red_count=1, green_count=2)]},
    {"color": "green", "movement": 3, "tokens": [get_token_with_colors(red_count=1, green_count=1, blue_count=1, yellow_count=1), get_token_with_colors(yellow_count=3)]},
    {"color": "green", "movement": 4, "tokens": [get_token_with_colors(green_count=1, yellow_count=1), get_token_with_colors(red_count=1, blue_count=1)]},
    {"color": "green", "movement": 4, "tokens": [get_token_with_colors(blue_count=4), get_token_with_colors(blue_count=2)]},
    {"color": "green", "movement": 4, "tokens": [get_token_with_colors(green_count=3), get_token_with_colors(blue_count=1, yellow_count=1)]},
    {"color": "green", "movement": 4, "tokens": [get_token_with_colors(blue_count=3), get_token_with_colors(yellow_count=3), get_token_with_colors(red_count=2)]},
    {"color": "green", "movement": 5, "tokens": [get_token_with_colors(yellow_count=3), get_token_with_colors(yellow_count=1)]},
    {"color": "green", "movement": 5, "tokens": [get_token_with_colors(red_count=2), get_token_with_colors(blue_count=1)]},
    {"color": "green", "movement": 5, "tokens": [get_token_with_colors(green_count=2), get_token_with_colors(red_count=2), get_token_with_colors(yellow_count=2)]},
    {"color": "green", "movement": 6, "tokens": [get_token_with_colors(red_count=3), get_token_with_colors(red_count=1, blue_count=1), get_token_with_colors(blue_count=2)]},
    {"color": "green", "movement": 6, "tokens": [get_token_with_colors(blue_count=2), get_token_with_colors(yellow_count=2), get_token_with_colors(red_count=1)]},
    {"color": "green", "movement": 7, "tokens": [get_token_with_colors(red_count=1, blue_count=1), get_token_with_colors(red_count=1, yellow_count=1), get_token_with_colors(blue_count=1, yellow_count=1)]},
    {"color": "blue", "movement": 1, "tokens": []},
    {"color": "blue", "movement": 2, "tokens": [get_token_with_colors(blue_count=4)]},
    {"color": "blue", "movement": 2, "tokens": [get_token_with_colors(blue_count=4)]},
    {"color": "blue", "movement": 3, "tokens": [get_token_with_colors(green_count=1, blue_count=1, yellow_count=1)]},
    {"color": "blue", "movement": 3, "tokens": [get_token_with_colors(red_count=2, green_count=1)]},
    {"color": "blue", "movement": 3, "tokens": [get_token_with_colors(blue_count=2, yellow_count=1)]},
    {"color": "blue", "movement": 3, "tokens": [get_token_with_colors(red_count=1, green_count=1, blue_count=1, yellow_count=1), get_token_with_colors(red_count=3)]},
    {"color": "blue", "movement": 4, "tokens": [get_token_with_colors(green_count=1, yellow_count=1), get_token_with_colors(red_count=1, blue_count=1)]},
    {"color": "blue", "movement": 4, "tokens": [get_token_with_colors(red_count=4), get_token_with_colors(red_count=2)]},
    {"color": "blue", "movement": 4, "tokens": [get_token_with_colors(blue_count=3), get_token_with_colors(red_count=1, green_count=1)]},
    {"color": "blue", "movement": 4, "tokens": [get_token_with_colors(green_count=3), get_token_with_colors(red_count=3), get_token_with_colors(yellow_count=2)]},
    {"color": "blue", "movement": 5, "tokens": [get_token_with_colors(green_count=3), get_token_with_colors(green_count=1)]},
    {"color": "blue", "movement": 5, "tokens": [get_token_with_colors(yellow_count=2), get_token_with_colors(green_count=1)]},
    {"color": "blue", "movement": 5, "tokens": [get_token_with_colors(green_count=2), get_token_with_colors(blue_count=2), get_token_with_colors(yellow_count=2)]},
    {"color": "blue", "movement": 6, "tokens": [get_token_with_colors(yellow_count=3), get_token_with_colors(red_count=1, yellow_count=1), get_token_with_colors(red_count=2)]},
    {"color": "blue", "movement": 6, "tokens": [get_token_with_colors(green_count=2), get_token_with_colors(red_count=2), get_token_with_colors(yellow_count=1)]},
    {"color": "blue", "movement": 7, "tokens": [get_token_with_colors(red_count=1, green_count=1), get_token_with_colors(green_count=1, yellow_count=1), get_token_with_colors(red_count=1, yellow_count=1)]},
    {"color": "yellow", "movement": 1, "tokens": []},
    {"color": "yellow", "movement": 2, "tokens": [get_token_with_colors(yellow_count=4)]},
    {"color": "yellow", "movement": 2, "tokens": [get_token_with_colors(yellow_count=4)]},
    {"color": "yellow", "movement": 3, "tokens": [get_token_with_colors(red_count=1, blue_count=1, yellow_count=1)]},
    {"color": "yellow", "movement": 3, "tokens": [get_token_with_colors(green_count=1, yellow_count=2)]},
    {"color": "yellow", "movement": 3, "tokens": [get_token_with_colors(red_count=1, blue_count=2)]},
    {"color": "yellow", "movement": 3, "tokens": [get_token_with_colors(red_count=1, green_count=1, blue_count=1, yellow_count=1), get_token_with_colors(blue_count=3)]},
    {"color": "yellow", "movement": 4, "tokens": [get_token_with_colors(red_count=1, green_count=1), get_token_with_colors(blue_count=1, yellow_count=1)]},
    {"color": "yellow", "movement": 4, "tokens": [get_token_with_colors(green_count=4), get_token_with_colors(green_count=2),]},
    {"color": "yellow", "movement": 4, "tokens": [get_token_with_colors(yellow_count=3), get_token_with_colors(red_count=1, blue_count=1)]},
    {"color": "yellow", "movement": 4, "tokens": [get_token_with_colors(green_count=3), get_token_with_colors(red_count=3), get_token_with_colors(blue_count=2)]},
    {"color": "yellow", "movement": 5, "tokens": [get_token_with_colors(red_count=3), get_token_with_colors(red_count=1)]},
    {"color": "yellow", "movement": 5, "tokens": [get_token_with_colors(green_count=2), get_token_with_colors(red_count=1)]},
    {"color": "yellow", "movement": 5, "tokens": [get_token_with_colors(red_count=2), get_token_with_colors(blue_count=2), get_token_with_colors(yellow_count=2)]},
    {"color": "yellow", "movement": 6, "tokens": [get_token_with_colors(blue_count=3), get_token_with_colors(blue_count=1, green_count=1), get_token_with_colors(green_count=2)]},
    {"color": "yellow", "movement": 6, "tokens": [get_token_with_colors(green_count=2), get_token_with_colors(red_count=2), get_token_with_colors(blue_count=1)]},
    {"color": "yellow", "movement": 7, "tokens": [get_token_with_colors(red_count=1, green_count=1), get_token_with_colors(blue_count=1, green_count=1), get_token_with_colors(red_count=1, blue_count=1)]}  
]

def generate_cards(card_data):
    deck = []
    for card_info in card_data:
        card = Card(
            color=card_info["color"],
            movement=card_info["movement"],
            tokens=card_info["tokens"]
        )
        deck.append(card)
        random.shuffle(deck)
    return deck
