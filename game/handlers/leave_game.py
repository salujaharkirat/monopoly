from game.db_utils import DbUtils
from game.exceptions import PlayerNotFound
from game.handlers.base import ws_handler
from game.service import GameService
from channels.db import database_sync_to_async


@ws_handler
async def handle_leave_game(consumer, data: dict):
  game_id = data.get('game_id')
  player = await DbUtils.get_player(data.get('user'))

  if not player:
    raise PlayerNotFound('Player not found')

  result = await leave_game_async(game_id, player.id)

  if not result['success']:
    await consumer.send_error(result['message'])
    return

  await consumer.channel_layer.group_send(
    consumer.room_group_name,
    {
      'type': 'game_left',
      'data': result['game_state']
    }
  )


@database_sync_to_async
def leave_game_async(game_id, player_id):
  return GameService.leave_game(game_id, player_id)
