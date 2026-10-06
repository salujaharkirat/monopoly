from game.db_utils import DbUtils
from game.handlers.base import ws_handler, run_action, broadcast
from game.service import GameService


@ws_handler
async def handle_pay_bail(consumer, data: dict):
  result = await run_action(consumer, data, GameService.pay_bail)
  if result is None:
    return

  game_state = await DbUtils.get_game_state(data.get('game_id'))
  await broadcast(consumer, 'bail_paid', {
    'message': result['message'],
    'bail_data': result['data'],
    'game_state': game_state
  })
