from game.db_utils import DbUtils
from game.handlers.base import ws_handler, run_action, broadcast
from game.service import GameService


@ws_handler
async def handle_use_jail_card(consumer, data: dict):
  result = await run_action(consumer, data, GameService.use_jail_card)
  if result is None:
    return

  game_state = await DbUtils.get_game_state(data.get('game_id'))
  await broadcast(consumer, 'jail_card_used', {
    'message': result['message'],
    'card_data': result['data'],
    'game_state': game_state
  })
