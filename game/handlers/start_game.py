from game.handlers.base import ws_handler, run_action, broadcast
from game.service import GameService


@ws_handler
async def handle_start_game(consumer, data: dict):
  result = await run_action(consumer, data, GameService.start_game)
  if result is None:
    return

  await broadcast(consumer, 'game_started', result['game_state'])
