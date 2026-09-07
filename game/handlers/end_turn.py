from game.db_utils import DbUtils
from game.exceptions import GameNotFound
from game.handlers.base import ws_handler
from game.service import GameService
from channels.db import database_sync_to_async


@ws_handler
async def handle_end_turn(consumer, data: dict):
  game = await DbUtils.get_game(data.get('game_id'))

  if game is None:
    raise GameNotFound('Game not found')

  result = await handle_end_turn_async(game.id)

  if not result['success']:
    await consumer.send_error(result['message'])
    return

  game_state = await DbUtils.get_game_state(data.get('game_id'))

  # Broadcast the turn change to all players
  await consumer.channel_layer.group_send(
    consumer.room_group_name,
    {
      'type': 'turn_ended',
      'data': {
          'message': result['message'],
          'game_state': game_state,
      }
    }
  )


@database_sync_to_async
def handle_end_turn_async(game_id):
  return GameService.end_turn(game_id)
