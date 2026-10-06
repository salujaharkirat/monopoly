from game.handlers.base import ws_handler, run_action, broadcast
from game.service import GameService


@ws_handler
async def handle_roll_dice(consumer, data: dict):
  result = await run_action(consumer, data, GameService.roll_dice)
  if result is None:
    return

  await broadcast(consumer, 'dice_rolled', result['data'])
