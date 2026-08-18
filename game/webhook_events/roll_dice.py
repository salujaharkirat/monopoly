from events import EventBus
from db_utils import DbUtils
from service import GameService
from channels.db import database_sync_to_async

@EventBus.subscribe('roll_dice')
async def handle_roll_dice(consumer, data: dict):
  try:
    game_id = data.get('game_id')
    player = await DbUtils.get_player(data.get('user'))
    game = await DbUtils.get_game(game_id)

    if player is None or game is None:
        await consumer.send_error("Player or game not found")
        return

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
  except Exception as e:
    await consumer.send_error(str(e))

@database_sync_to_async
def roll_dice_async(game_id, player_id):
   return GameService.roll_dice(game_id, player_id)