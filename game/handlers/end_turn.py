from game.db_utils import DbUtils
from game.handlers.base import ws_handler, run_action, broadcast
from game.service import GameService


@ws_handler
async def handle_end_turn(consumer, data: dict):
  result = await run_action(consumer, data, GameService.end_turn)
  if result is None:
    return

  game_state = await DbUtils.get_game_state(data.get('game_id'))
  await broadcast(consumer, 'turn_ended', {
    'message': result['message'],
    'game_state': game_state
  })
