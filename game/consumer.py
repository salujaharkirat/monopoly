import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from channels.db import database_sync_to_async
from .models import Player, Game

logger = logging.getLogger(__name__)

class GameConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    self.game_id = self.scope['url_route']['kwargs']['game_id']
    self.room_group_name = f'game_{self.game_id}'
    self.user = self.scope['user']

    if not self.user.is_authenticated:
      await self.close()
      return
    
    try:
      player = await self.get_player(self.user)
      game = await self.get_game(self.game_id)

      if not self.is_player_in_game(player, game):
        await self.close(code=4003)
        return
      
    except ObjectDoesNotExist:
      await self.close(code=4004)
      return 

    # Join game room
    await self.channel_layer.group_add(
        self.room_group_name,
        self.channel_name
    )

    await self.accept()

    await self.send_game_state()

    await self.channel_layer.group_send(
      self.room_group_name,
      {
        'type': 'player_joined',
        'username': self.user.username,
        'message': f'{self.user.username} joined the game'

      }
    )

  async def disconnect(self):
    await self.channel_layer.group_discard(
        self.room_group_name,
        self.channel_name
    )

    if self.user.is_authenticated:
      await self.channel_layer.group_send(
        self.room_group_name,
        {
            'type': 'player_left',
            'username': self.user.username,
            'message': f"{self.user.username} left the game"
        }
      )

  async def receive(self, text_data):
    try:
      data = json.loads(text_data)
      action = data.get('action')

      if action == 'start_game':
        await self.handle_start_game(data)
      if action == 'roll_dice':
        await self.handle_roll_dice(data)
      if action == 'buy_property':
        await self.handle_buy_property(data)
      if action == 'end_turn':
        await self.handle_end_turn(data)
      else:
        await self.send_error(f"Unknown action: {action}")
    except json.JSONDecodeError:
      await self.send_error("Invalid JSON")
    except Exception as e:
      logger.error(f"Error handling message: {e}")
      await self.send_error(str(e))
      pass

  async def handle_start_game(self):
    try:
      player = await self.get_player(self.user)
      result = await database_sync_to_async(GameService.start_game)(
        game_id=self.game_id,
        player_id=player.id
      )

      if result.get('success'):
        self.channel_layer.group_send(
          self.room_group_name,
          {
            'type': 'game_started',
            'data': result.get('game_state')
          }
        )
      else:
        await self.send_error(result.get('message', 'Failed to start game'))
    except Exception as e:
      await self.send_error(str(e))

  async def handle_roll_dice(self):
    pass

  async def handle_buy_property(self):
    pass

  async def handle_end_turn(self):
    pass


  # Database helpers

  @database_sync_to_async
  def get_player(self, user):
    return Player.objects.get(user=user)
  
  @database_sync_to_async
  def get_game(self, game_id):
    return Game.objects.get(id=game_id)

  @database_sync_to_async
  def is_player_in_game(self, player, game):
    """Check if player is in game"""
    return game.players.filter(id=player.id).exists()

  @database_sync_to_async
  def get_game_state(self):
    """Get current game state"""
    return GameService.get_game_state(self.game_id)


  async def send_game_state(self):
    """Send current game state to client"""
    game_state = await self.get_game_state()
    await self.send(text_data=json.dumps({
      'type': 'game_state',
      'data': game_state
    }))

  async def send_error(self, message):
    """Send error message to client"""
    await self.send(text_data=json.dumps({
      'type': 'error',
      'message': message
    }))
  
  async def game_started(self, event):
    pass

  async def player_joined(self, event):
    pass

  async def player_left(self, event):
    pass



