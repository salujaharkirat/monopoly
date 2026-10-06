from game.db_utils import DbUtils
from game.handlers.base import ws_handler, run_action, broadcast
from game.service import GameService


@ws_handler
async def handle_buy_property(consumer, data: dict):
  result = await run_action(consumer, data, GameService.buy_property, data.get('property_id'))
  if result is None:
    return

  game_state = await DbUtils.get_game_state(data.get('game_id'))
  await broadcast(consumer, 'property_purchased', {
    'message': result['message'],
    'purchase_data': result['data'],
    'game_state': game_state
  })
