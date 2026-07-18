# game/board_data.py
"""Monopoly board configuration"""

BOARD_SQUARES = [
    # Bottom row (positions 0-10)
    {"id": 0, "name": "GO", "type": "GO", "color": None},
    {"id": 1, "name": "Mediterranean Avenue", "type": "PR", "color": "brown", "price": 60, "rent": 2},
    {"id": 2, "name": "Community Chest", "type": "CC", "color": None},
    {"id": 3, "name": "Baltic Avenue", "type": "PR", "color": "brown", "price": 60, "rent": 4},
    {"id": 4, "name": "Income Tax", "type": "TA", "color": None, "amount": 200},
    {"id": 5, "name": "Reading Railroad", "type": "RR", "color": "railroad", "price": 200, "rent": 25},
    {"id": 6, "name": "Oriental Avenue", "type": "PR", "color": "light_blue", "price": 100, "rent": 6},
    {"id": 7, "name": "Chance", "type": "CH", "color": None},
    {"id": 8, "name": "Vermont Avenue", "type": "PR", "color": "light_blue", "price": 100, "rent": 6},
    {"id": 9, "name": "Connecticut Avenue", "type": "PR", "color": "light_blue", "price": 120, "rent": 8},
    {"id": 10, "name": "Jail / Just Visiting", "type": "JA", "color": None},
    
    # Left column (positions 11-19)
    {"id": 11, "name": "St. Charles Place", "type": "PR", "color": "pink", "price": 140, "rent": 10},
    {"id": 12, "name": "Electric Company", "type": "UT", "color": "utility", "price": 150, "rent": 0},
    {"id": 13, "name": "States Avenue", "type": "PR", "color": "pink", "price": 140, "rent": 10},
    {"id": 14, "name": "Virginia Avenue", "type": "PR", "color": "pink", "price": 160, "rent": 12},
    {"id": 15, "name": "Pennsylvania Railroad", "type": "RR", "color": "railroad", "price": 200, "rent": 25},
    {"id": 16, "name": "St. James Place", "type": "PR", "color": "orange", "price": 180, "rent": 14},
    {"id": 17, "name": "Community Chest", "type": "CC", "color": None},
    {"id": 18, "name": "Tennessee Avenue", "type": "PR", "color": "orange", "price": 180, "rent": 14},
    {"id": 19, "name": "New York Avenue", "type": "PR", "color": "orange", "price": 200, "rent": 16},
    
    # Top row (positions 20-30)
    {"id": 20, "name": "Free Parking", "type": "FP", "color": None},
    {"id": 21, "name": "Kentucky Avenue", "type": "PR", "color": "red", "price": 220, "rent": 18},
    {"id": 22, "name": "Chance", "type": "CH", "color": None},
    {"id": 23, "name": "Indiana Avenue", "type": "PR", "color": "red", "price": 220, "rent": 18},
    {"id": 24, "name": "Illinois Avenue", "type": "PR", "color": "red", "price": 240, "rent": 20},
    {"id": 25, "name": "B. & O. Railroad", "type": "RR", "color": "railroad", "price": 200, "rent": 25},
    {"id": 26, "name": "Atlantic Avenue", "type": "PR", "color": "yellow", "price": 260, "rent": 22},
    {"id": 27, "name": "Ventnor Avenue", "type": "PR", "color": "yellow", "price": 260, "rent": 22},
    {"id": 28, "name": "Water Works", "type": "UT", "color": "utility", "price": 150, "rent": 0},
    {"id": 29, "name": "Marvin Gardens", "type": "PR", "color": "yellow", "price": 280, "rent": 24},
    {"id": 30, "name": "Go To Jail", "type": "GJ", "color": None},
    
    # Right column (positions 31-39)
    {"id": 31, "name": "Pacific Avenue", "type": "PR", "color": "green", "price": 300, "rent": 26},
    {"id": 32, "name": "North Carolina Avenue", "type": "PR", "color": "green", "price": 300, "rent": 26},
    {"id": 33, "name": "Community Chest", "type": "CC", "color": None},
    {"id": 34, "name": "Pennsylvania Avenue", "type": "PR", "color": "green", "price": 320, "rent": 28},
    {"id": 35, "name": "Short Line", "type": "RR", "color": "railroad", "price": 200, "rent": 25},
    {"id": 36, "name": "Chance", "type": "CH", "color": None},
    {"id": 37, "name": "Park Place", "type": "PR", "color": "dark_blue", "price": 350, "rent": 35},
    {"id": 38, "name": "Luxury Tax", "type": "TA", "color": None, "amount": 100},
    {"id": 39, "name": "Boardwalk", "type": "PR", "color": "dark_blue", "price": 400, "rent": 50},
]
