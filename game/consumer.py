# game/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Game, Player
from .serializers import GameDetailSerializer

logger = logging.getLogger(__name__)

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'game_{self.game_id}'
        
        # Get token from query string
        query_string = self.scope['query_string'].decode()
        token_key = None
        if 'token=' in query_string:
            token_key = query_string.split('token=')[1].split('&')[0]
        
        if not token_key:
            logger.error("No token provided")
            await self.close(code=4001)
            return
        
        # Authenticate user with token
        try:
            token = await self.get_token(token_key)
            if not token:
                await self.close(code=4001)
                return
            
            self.user = token.user
            
            # Check if user is in the game
            player = await self.get_player(self.user)
            game = await self.get_game(self.game_id)
            
            if not await self.is_player_in_game(player, game):
                await self.close(code=4003)
                return
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            await self.close(code=4001)
            return
        
        # Join game room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current game state
        await self.send_game_state()
        
        # Notify others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'username': self.user.username,
                'message': f"{self.user.username} joined the game"
            }
        )
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'start_game':
                await self.handle_start_game()
            elif action == 'roll_dice':
                await self.handle_roll_dice(data)
            elif action == 'buy_property':
                await self.handle_buy_property(data)
            elif action == 'end_turn':
                await self.handle_end_turn()
            else:
                await self.send_error(f"Unknown action: {action}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error(str(e))
    
    async def handle_start_game(self):
        # Implementation...
        pass
    
    async def handle_roll_dice(self, data):
        # Implementation...
        pass
    
    async def handle_buy_property(self, data):
        # Implementation...
        pass
    
    async def handle_end_turn(self):
        # Implementation...
        pass
    
    @database_sync_to_async
    def get_token(self, key):
        try:
            return Token.objects.get(key=key)
        except Token.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_player(self, user):
        return Player.objects.get(user=user)
    
    @database_sync_to_async
    def get_game(self, game_id):
        return Game.objects.get(id=game_id)
    
    @database_sync_to_async
    def is_player_in_game(self, player, game):
        return game.players.filter(id=player.id).exists()
    
    @database_sync_to_async
    def get_game_state(self):
        game = Game.objects.get(id=self.game_id)
        return GameDetailSerializer(game).data
    
    async def send_game_state(self):
        game_state = await self.get_game_state()
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': game_state
        }))
    
    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    # Group event handlers
    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'data': event['data']
        }))
    
    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'username': event['username'],
            'message': event['message']
        }))
    
    async def player_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'username': event['username'],
            'message': event['message']
        }))
    
    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'data': event['data']
        }))