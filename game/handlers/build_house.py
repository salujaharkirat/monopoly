from game.db_utils import DbUtils
from channels.db import database_sync_to_async
from game.service import GameService

async def handle_build_house(consumer, data: dict):
  try:
    property_id = data.get('property_id')
    player = await DbUtils.get_player(data.get('user'))
    result = await build_house_async(data.get('game_id'), player.id, property_id, data.get('number_of_houses'))

    if not result['success']:
      await consumer.send_error(result['message'])
      return

    # Get updated game state
    game_state = await DbUtils.get_game_state(data.get('game_id'))
    
    # Broadcast property purchase to all players
    await consumer.channel_layer.group_send(
      consumer.room_group_name,
      {
          'type': 'property_purchased',
          'data': {
              'message': result['message'],
              'purchase_data': result['data'],
              'game_state': game_state
          }
      }
    )
  except Exception as e:
    await consumer.send_error(str(e))
  pass

@database_sync_to_async
def build_house_async(game_id, player_id, property_id, number_of_houses):
  return GameService.build_house(game_id, player_id, property_id, number_of_houses)
