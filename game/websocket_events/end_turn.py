from events import EventBus
from db_utils import DbUtils
from service import GameService
from channels.db import database_sync_to_async

@EventBus.subscribe('end_turn')
async def handle_end_turn(consumer, data: dict):
  try:
    game = await DbUtils.get_game(data.get('game_id'))

    if game is None:
      await consumer.send_error("Player or game not found")
      return

    result = await handle_end_turn_async(game.id)

    if not result['success']:
      await consumer.send_error(result['message'])
      return
    
    game_state = await DbUtils.get_game_state(data.get('game_id'))

    #Broadcast property purchase to all players
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
  except Exception as e:
    await consumer.send_error(str(e))

@database_sync_to_async
def handle_end_turn_async(game_id):
  return GameService.end_turn(game_id)