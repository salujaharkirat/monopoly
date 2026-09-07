from game.db_utils import DbUtils
from game.exceptions import GameNotFound, PlayerNotFound
from game.handlers.base import ws_handler
from game.service import GameService
from channels.db import database_sync_to_async


@ws_handler
async def handle_roll_dice(consumer, data: dict):
  game_id = data.get('game_id')
  player = await DbUtils.get_player(data.get('user'))
  game = await DbUtils.get_game(game_id)

  if player is None:
    raise PlayerNotFound('Player not found')
  if game is None:
    raise GameNotFound('Game not found')

  result = await roll_dice_async(game.id, player.id)

  if not result['success']:
    await consumer.send_error(result['message'])
    return

  # Broadcast dice result
  await consumer.channel_layer.group_send(
    consumer.room_group_name,
    {
        'type': 'dice_rolled',
        'data': result['data']
    }
  )


@database_sync_to_async
def roll_dice_async(game_id, player_id):
  return GameService.roll_dice(game_id, player_id)
