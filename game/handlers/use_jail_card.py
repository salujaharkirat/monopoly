from game.db_utils import DbUtils
from game.exceptions import PlayerNotFound
from game.handlers.base import ws_handler
from game.service import GameService
from channels.db import database_sync_to_async


@ws_handler
async def handle_use_jail_card(consumer, data: dict):
  player = await DbUtils.get_player(data.get('user'))

  if not player:
    raise PlayerNotFound('Player not found')

  result = await use_jail_card_async(data.get('game_id'), player.id)

  if not result['success']:
    await consumer.send_error(result['message'])
    return

  game_state = await DbUtils.get_game_state(data.get('game_id'))

  await consumer.channel_layer.group_send(
    consumer.room_group_name,
    {
        'type': 'jail_card_used',
        'data': {
            'message': result['message'],
            'card_data': result['data'],
            'game_state': game_state
        }
    }
  )


@database_sync_to_async
def use_jail_card_async(game_id, player_id):
  return GameService.use_jail_card(game_id, player_id)
