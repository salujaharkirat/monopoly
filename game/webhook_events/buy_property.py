from events import EventBus
from db_utils import DbUtils
from service import GameService
from channels.db import database_sync_to_async

@EventBus.subscribe('buy_property')
async def handle_buy_property(consumer, data: dict):
  try:
    property_id = data.get('property_id')
    player = await DbUtils.get_player(data.get('user'))
    result = await buy_property_async(data.get('game_id'), player.id, property_id)

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

@database_sync_to_async
def buy_property_async(game_id, player_id, property_id):
  return GameService.buy_property(game_id, player_id, property_id)
