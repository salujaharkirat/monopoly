from game.handlers.base import ws_handler


@ws_handler
async def handle_game_state(consumer, data: dict):
  await consumer.send_game_state()
