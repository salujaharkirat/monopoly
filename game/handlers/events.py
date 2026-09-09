from game.handlers.build_house import handle_build_house
from game.handlers.buy_property import handle_buy_property
from game.handlers.end_turn import handle_end_turn
from game.handlers.game_state import handle_game_state
from game.handlers.pay_bail import handle_pay_bail
from game.handlers.roll_dice import handle_roll_dice
from game.handlers.start_game import handle_start_game
from game.handlers.use_jail_card import handle_use_jail_card

# ✅ Dictionary mapping - cleaner and faster
HANDLER_MAP = {
    'roll_dice': handle_roll_dice,
    'start_game': handle_start_game,
    'end_turn': handle_end_turn,
    'buy_property': handle_buy_property,
    'game_state': handle_game_state,
    'build_house': handle_build_house,
    'pay_bail': handle_pay_bail,
    'use_jail_card': handle_use_jail_card,
}

def get_handler(action: str):
    return HANDLER_MAP.get(action)  # Returns None if not found
