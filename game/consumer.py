# game/consumers.py
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from game.db_utils import DbUtils
from game.handlers.events import get_handler

logger = logging.getLogger(__name__)

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope.get('url_route', {}).get('kwargs', {}).get('game_id')
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
            token = await DbUtils.get_token(token_key)
            user = await DbUtils.get_user_from_token(token_key)
            if not token:
                await self.close(code=4001)
                return
            
            self.user = user
            
            # Check if user is in the game
            player = await DbUtils.get_player(self.user)
            game = await DbUtils.get_game(self.game_id)

            if not await DbUtils.is_player_in_game(player, game):
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
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None, bytes_data=None):
        try:
            if not text_data:
                await self.send_error("Missing text data")
                return
            data = json.loads(text_data)
            action = data.get('action')
            data['user'] = self.user
            data['game_id'] = self.game_id

            print("reached here", self.user, action)
            handler = get_handler(action)

            if handler:
                await handler(self, data)
            else:
                await self.send_error(f"Unkown action {action}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error(str(e))

    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'data': event['data']
        }))

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'data': event['data']
        }))
        
    async def dice_rolled(self, event):
        """Handle dice rolled broadcast"""
        print(f"📨 Dice rolled event received")
        await self.send(text_data=json.dumps({
            'type': 'dice_rolled',
            'data': event['data']
        }))
    
    async def property_purchased(self, event):
        await self.send(text_data=json.dumps({
            'type': 'property_purchased',
            'data': event['data']
        }))
    
    async def turn_ended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'turn_ended',
            'data': event['data']
        }))

    async def send_game_state(self):
        game_state = await DbUtils.get_game_state(self.game_id)
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': game_state
        }))