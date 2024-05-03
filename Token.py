class Token:
    # A token class célja hogy indikátor legyen a kártyákon, mivel több színű lehet keverve 4 adatot tartalmaz: red, green, blue, yellow
    def __init__(self, red=None, green=None, blue=None, yellow=None):
        self.red = red
        self.green = green
        self.blue = blue
        self.yellow = yellow

def get_token_with_colors(red_count=0, green_count=0, blue_count=0, yellow_count=0):
    token_dict = {
        'red': red_count,
        'green': green_count,
        'blue': blue_count,
        'yellow': yellow_count
    }
    return Token(**token_dict)

""" Használati példa:
token = get_token_with_colors(red_count=2, green_count=1, blue_count=1)
print(token.red)    # Output: 2
print(token.green)  # Output: 1
print(token.blue)   # Output: 1
print(token.yellow) # Output: None """

def generate_token_combinations():
    combinations = set()

    # Egy színű tokenek generálása
    for color in ['red', 'green', 'blue', 'yellow']:
        for i in range(1, 5):
            if i <= 4:
                token_dict = {color: i}
                token = Token(**token_dict)
                combinations.add(tuple(sorted(token_dict.items())))

    # Két színű tokenek generálása
    for color1 in ['red', 'green', 'blue', 'yellow']:
        for color2 in ['red', 'green', 'blue', 'yellow']:
            if color1 != color2:
                for i in range(1, 4):
                    for j in range(1, 4):
                        if i + j <= 4:
                            token_dict = {color1: i, color2: j}
                            token = Token(**token_dict)
                            combinations.add(tuple(sorted(token_dict.items())))

    # Három színű tokenek generálása
    for color1 in ['red', 'green', 'blue', 'yellow']:
        for color2 in ['red', 'green', 'blue', 'yellow']:
            for color3 in ['red', 'green', 'blue', 'yellow']:
                if len(set([color1, color2, color3])) == 3:
                    for i in range(1, 3):
                        for j in range(1, 3):
                            for k in range(1, 3):
                                if i + j + k <= 4:
                                    remaining = 4 - i - j - k
                                    token_dict = {color1: i, color2: j, color3: k, 'yellow': remaining}
                                    token = Token(**token_dict)
                                    combinations.add(tuple(sorted(token_dict.items())))

    # Négy színű tokenek generálása
    for color1 in ['red', 'green', 'blue', 'yellow']:
        for color2 in ['red', 'green', 'blue', 'yellow']:
            for color3 in ['red', 'green', 'blue', 'yellow']:
                for color4 in ['red', 'green', 'blue', 'yellow']:
                    if len(set([color1, color2, color3, color4])) == 4:
                        for i in range(1, 3):
                            for j in range(1, 3):
                                for k in range(1, 3):
                                    for l in range(1, 3):
                                        if i + j + k + l <= 4:
                                            token_dict = {color1: i, color2: j, color3: k, color4: l}
                                            token = Token(**token_dict)
                                            combinations.add(tuple(sorted(token_dict.items())))

    # Az adatok listává alakíttása majd sorrendbe helyezése
    sorted_combinations = [Token(**dict(comb)) for comb in sorted(list(combinations), key=lambda x: (len([color for color in dict(x).values() if color is not None]), sum(color for color in dict(x).values() if color is not None)))]
    
    return sorted_combinations




