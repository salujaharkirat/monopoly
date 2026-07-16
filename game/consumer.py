# game/consumers.py
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from game.models import Game, Player
from game.serializer import GameDetailSerializer
from game.service import GameService

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
            token = await self.get_token(token_key)
            user = await self.get_user_from_token(token_key)
            if not token:
                await self.close(code=4001)
                return
            
            self.user = user
            
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

            if action == 'start_game':
                await self.handle_start_game()
            elif action == 'roll_dice':
                await self.handle_roll_dice(data)
            elif action == 'buy_property':
                await self.handle_buy_property(data)
            elif action == 'end_turn':
                await self.handle_end_turn()
            elif action == 'get_state':
                await self.send_game_state()
            elif action == 'leave_game':
                await self.handle_leave_game()
            else:
                await self.send_error(f"Unknown action: {action}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error(str(e))
    
    async def handle_leave_game(self):
        try:
            player = await self.get_player(self.user)
            result = await self.leave_game_async(self.game.id, player.id)

            if not result['success']:
                await self.send_error(result['message'])
                return
            
            # Broadcast to all remaining players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_left_game',
                    'data': result
                }
            )

            # Send confirmation to the leaving player
            await self.send(text_data=json.dumps({
                'type': 'leave_confirmed',
                'data': result
            }))
            
            # Close the WebSocket connection for the leaving player
            await self.close()
        except Exception as e:
            print(f"❌ Error leaving game: {e}")
            await self.send_error(str(e))

    async def handle_start_game(self):
        try:
            player = await self.get_player(self.user)
            game = await self.get_game(self.game_id)

            if not player:
                await self.send_error("Player not found")
                return
            
            if not game:
                await self.send_error("Game not found")
                return
            

            if game.created_by != player:
                await self.send_error("Only creater can start the game")
                return
            
            can_start, errors = await self.can_start_game(game, player)
            if not can_start:
                await self.send_error("".join(errors))
                return
            
            await self.start_game(game)

            game_state = await self.get_game_state()
            
            await self.broadcast_game_state(game_state)
            
        except Exception as e:
            await self.send_error(str(e))
    
    async def handle_roll_dice(self, data):
        try:
            player = await self.get_player(self.user)
            game = await self.get_game(self.game_id)

            if player is None or game is None:
                await self.send_error("Player or game not found")
                return

            result = await self.roll_dice_async(game.id, player.id)

            if not result['success']:
                await self.send_error(result['message'])
                return
            
            # Broadcast dice result
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'dice_rolled',
                    'data': result['data']
                }
            )

        except Exception as e:
            await self.send_error(str(e))
    
    async def handle_buy_property(self, data):
        try:
            property_id = data.get('property_id')
            player = await self.get_player(self.user)
            result = await GameService.buy_property(self.game_id, player.id, property_id)

            if not result['success']:
                await self.send_error(result['message'])
                return
            
            # Get updated game state
            game_state = await self.get_game_state()
            
            # Broadcast property purchase to all players
            await self.channel_layer.group_send(
                self.room_group_name,
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
            print(f"❌ Error buying property: {e}")
            await self.send_error(str(e))
        pass
    
    async def handle_end_turn(self):
        pass

    @database_sync_to_async
    def leave_game_async(self, game_id, player_id):
        return GameService.leave_game(game_id, player_id)

    @database_sync_to_async
    def roll_dice_async(self, game_id, player_id):
        return GameService.roll_dice(game_id, player_id)

    @database_sync_to_async
    def get_user_from_token(self, key):
        """Get user from token - handles all cases"""
        try:
            token = Token.objects.select_related('user').get(key=key)
            
            user = getattr(token, 'user', None)
            
            if not user:
                print("Token has no user")
                return None
                
            return user
            
        except Token.DoesNotExist:
            print(f"Token not found: {key[:20]}...")
            return None
        except Exception as e:
            print(f"Error getting user: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
    def get_game(self, game_id) -> Game | None:
        """Get game with related fields prefetched"""
        try:
            game = Game.objects.select_related('created_by', 'created_by__user').get(id=game_id)
            return game
        except Game.DoesNotExist:
            return None

    @database_sync_to_async
    def can_start_game(self, game, player):
        return game.can_start(player)

    @database_sync_to_async
    def start_game(self, game):
        game.start_game()
        game.save()
        return game
    
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

    async def broadcast_game_state(self, game_state):
        """Broadcast game state to all players in the room"""
        print(f"📡 Broadcasting game state to {self.room_group_name}")
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_state_broadcast',
                'data': game_state
            }
        )
        print("✅ Game state broadcast sent!")

    async def game_state_broadcast(self, event):
        """Handle game state broadcast from group"""
        print(f"📨 Received game_state_broadcast")
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': event['data']
        }))
        
    async def dice_rolled(self, event):
        """Handle dice rolled broadcast"""
        print(f"📨 Dice rolled event received")
        await self.send(text_data=json.dumps({
            'type': 'dice_rolled',
            'data': event['data']
        }))