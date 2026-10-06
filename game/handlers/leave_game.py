from game.handlers.base import ws_handler, run_action, broadcast
from game.service import GameService


@ws_handler
async def handle_leave_game(consumer, data: dict):
  result = await run_action(consumer, data, GameService.leave_game)
  if result is None:
    return

  await broadcast(consumer, 'game_left', result)
