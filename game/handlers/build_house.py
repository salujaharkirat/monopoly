from game.db_utils import DbUtils
from game.handlers.base import ws_handler, run_action, broadcast
from game.service import GameService


@ws_handler
async def handle_build_house(consumer, data: dict):
  result = await run_action(
    consumer, data, GameService.build_house,
    data.get('property_id'), data.get('number_of_houses')
  )
  if result is None:
    return

  game_state = await DbUtils.get_game_state(data.get('game_id'))
  await broadcast(consumer, 'house_built', {
    'message': result['message'],
    'build_data': result['data'],
    'game_state': game_state
  })
