# from rest_framework import status, permissions
# from rest_framework.response import Response
# from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.contrib.auth import login
# from django.shortcuts import render, get_object_or_404
# from channels.layers import get_channel_layer
# from django.contrib.auth.decorators import login_required
# from asgiref.sync import async_to_sync
# from django.contrib.auth.models import User
from django.contrib import messages
# from rest_framework.authentication import SessionAuthentication, TokenAuthentication

# from .models import Player, Game
# from .serializer import CreateGameSerializer, GameDetailSerializer, JoinGameSerializer, StartGameSerializer
# from .service import GameService

# class CreateGameView(APIView):
#   permission_classes = [permissions.IsAuthenticated]
  
#   def post(self, request):
#       # Get or create player
#       player, created = Player.objects.get_or_create(
#           user=request.user,
#           defaults={'money': 2000}
#       )
      
#       # Check if player already in an active game
#       if player.games.filter(
#           state__in=[Game.GameState.WAITING, Game.GameState.PLAYING]
#       ).exists():
#           return Response(
#               {"detail": "You are already in an active game"},
#               status=status.HTTP_400_BAD_REQUEST
#           )
      
#       # Validate and create game using serializer
#       serializer = CreateGameSerializer(
#           data=request.data,
#           context={'player': player, 'request': request}  # Pass player to serializer
#       )
#       serializer.is_valid(raise_exception=True)
      
#       # ✅ Serializer's create method handles the game creation
#       game = serializer.save()
      
#       # Return game details
#       response_serializer = GameDetailSerializer(
#           game, 
#           context={'request': request}
#       )
#       return Response(
#           response_serializer.data,
#           status=status.HTTP_201_CREATED
#       )
# class JoinGameView(APIView):
#   """
#   API to join an existing game by ID
#   POST /api/games/join/
#   """
#   permission_classes = [permissions.IsAuthenticated]
  
#   def post(self, request, game_id):
#     # Validate request
#     player, created = Player.objects.get_or_create(
#         user=request.user,
#         defaults={
#             'money': 2000,
#             'position': 0,
#             'is_in_jail': False,
#             'is_active': True
#         }
#     )
#     game = get_object_or_404(Game, id=game_id)

#     serializer = JoinGameSerializer(
#         data={},
#         context={
#           'request': request,
#           'game': game
#         }
#     )
#     serializer.is_valid(raise_exception=True)
    
#     # Get validated data
#     game = serializer.context['game']
#     player = serializer.context['player']
    
#     # Add player to game
#     game.players.add(player)
#     game.save()
    
#     # Return updated game details
#     response_serializer = GameDetailSerializer(
#         game,
#         context={'request': request}
#     )

#     return Response(
#         response_serializer.data,
#         status=status.HTTP_200_OK
#     )


# class StartGameView(APIView):
#     """Start a game with WebSocket broadcast"""
#     permission_classes = [permissions.IsAuthenticated]
    
#     def post(self, request, game_id):
#         # Get the game
#         game = get_object_or_404(Game, id=game_id)
        
#         # Validate start request
#         serializer = StartGameSerializer(
#             data={},
#             context={
#                 'request': request,
#                 'game': game
#             }
#         )
#         serializer.is_valid(raise_exception=True)
        
#         # Start the game using service
#         result = GameService.start_game(game_id, request.user.monopoly_player.id)
        
#         if not result['success']:
#             return Response(
#                 {"detail": result['message']},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         # Broadcast game started via WebSocket
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f'game_{game_id}',
#             {
#                 'type': 'game_started',
#                 'data': result['game_state']
#             }
#         )
        
#         # Return response
#         response_serializer = GameDetailSerializer(
#             game,
#             context={'request': request}
#         )
#         return Response(
#             response_serializer.data,
#             status=status.HTTP_200_OK
#         )

# class GameStatusView(APIView):
#     """Get current game status with WebSocket info"""
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get(self, request, game_id):
#         get_object_or_404(Game, id=game_id)
        
#         # Get game state from service
#         game_state = GameService.get_game_state(game_id)
        
#         # Add WebSocket connection info
#         game_state['websocket_url'] = f"ws://{request.get_host()}/ws/game/{game_id}/"
        
#         return Response(game_state)


# def game_detail_view(request, game_id):
#     """Render the game detail page"""
#     game = get_object_or_404(Game, id=game_id)
    
#     # Check if user is in the game
#     if request.user.is_authenticated:
#         try:
#             player = request.user.monopoly_player
#             is_in_game = game.players.filter(id=player.id).exists()
#         except Player.DoesNotExist:
#             is_in_game = False
#     else:
#         is_in_game = False
    
#     context = {
#         'game': game,
#         'is_in_game': is_in_game,
#     }
    
#     return render(request, 'game/game_detail.html', context)

# @login_required
# def game_lobby_view(request):
#     """Render the game lobby"""
#     available_games = Game.objects.filter(state=Game.GameState.WAITING)
    
#     # Get player for current user
#     try:
#         player = request.user.monopoly_player
#     except Player.DoesNotExist:
#         player = None
    
#     context = {
#         'available_games': available_games,
#         'player': player,
#     }
    
#     return render(request, 'game/game_lobby.html', context)

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'registration/register.html')
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'registration/register.html')
        
        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'registration/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # Create player profile
            Player.objects.create(
                user=user,
                money=2000,
                position=0,
                is_in_jail=False,
                is_active=True
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('game-lobby')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'registration/register.html')
    
    return render(request, 'registration/register.html')

# @login_required
# def create_game_page(request):
#     """HTML page for creating a new game"""
#     try:
#         player = request.user.monopoly_player
#     except Player.DoesNotExist:
#         player = None
    
#     # Check if user already in a game
#     active_game = None
#     if player:
#         active_game = player.games.filter(
#             state__in=[Game.GameState.WAITING, Game.GameState.PLAYING]
#         ).first()
    
#     context = {
#         'player': player,
#         'active_game': active_game,
#         'max_players': 4,  # Default
#         'min_players': 2,  # Default
#     }
#     return render(request, 'game/create_game.html', context)

# class CreateGameView(APIView):
#     """API endpoint to create a game"""
    
#     # ✅ Use both session and token authentication
#     authentication_classes = [SessionAuthentication, TokenAuthentication]
#     permission_classes = [permissions.IsAuthenticated]
    
#     def post(self, request):
#         # Get or create player
#         player, created = Player.objects.get_or_create(
#             user=request.user,
#             defaults={'money': 2000}
#         )
        
#         # Check if player already in an active game
#         if player.games.filter(
#             state__in=[Game.GameState.WAITING, Game.GameState.PLAYING]
#         ).exists():
#             return Response(
#                 {"detail": "You are already in an active game"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         # Validate and create game
#         serializer = CreateGameSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         game = Game.objects.create(
#             name=serializer.validated_data.get('name', "Monopoly Game"),
#             max_players=serializer.validated_data.get('max_players', 4),
#             min_players=serializer.validated_data.get('min_players', 2),
#             created_by=player
#         )
#         game.players.add(player)
        
#         return Response(
#             {
#                 'id': game.id,
#                 'name': game.name,
#                 'message': 'Game created successfully!',
#                 'redirect': f'/games/{game.id}/'
#             },
#             status=status.HTTP_201_CREATED
#         )
#     """API endpoint to create a game"""
#     permission_classes = [permissions.IsAuthenticated]  # ✅ Requires token authentication
    
#     def post(self, request):
#         # Get or create player
#         player, created = Player.objects.get_or_create(
#             user=request.user,
#             defaults={'money': 2000}
#         )
        
#         # Check if player already in an active game
#         if player.games.filter(
#             state__in=[Game.GameState.WAITING, Game.GameState.PLAYING]
#         ).exists():
#             return Response(
#                 {"detail": "You are already in an active game"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         # Validate and create game
#         serializer = CreateGameSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         game = Game.objects.create(
#             name=serializer.validated_data.get('name', "Monopoly Game"),
#             max_players=serializer.validated_data.get('max_players', 4),
#             min_players=serializer.validated_data.get('min_players', 2),
#             created_by=player
#         )
#         game.players.add(player)
        
#         return Response(
#             {
#                 'id': game.id,
#                 'name': game.name,
#                 'message': 'Game created successfully!',
#                 'redirect': f'/games/{game.id}/'
#             },
#             status=status.HTTP_201_CREATED
#         )

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Game, Player
from .serializer import (
    GameSerializer, 
    GameDetailSerializer, 
    CreateGameSerializer,
    RegisterSerializer
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class GameListView(generics.ListAPIView):
    """List all available games"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GameSerializer
    
    def get_queryset(self):
        return Game.objects.filter(state=Game.GameState.WAITING)

class GameDetailView(generics.RetrieveAPIView):
    """Get game details"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GameDetailSerializer
    queryset = Game.objects.all()
    lookup_field = 'id'

class CreateGameView(APIView):
    """Create a new game"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        player, created = Player.objects.get_or_create(
            user=request.user,
            defaults={'money': 2000}
        )
        
        if player.games.filter(
            state__in=[Game.GameState.WAITING, Game.GameState.PLAYING]
        ).exists():
            return Response(
                {"detail": "You are already in an active game"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CreateGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        game = Game.objects.create(
            name=serializer.validated_data.get('name', "Monopoly Game"),
            max_players=serializer.validated_data.get('max_players', 4),
            min_players=serializer.validated_data.get('min_players', 2),
            created_by=player
        )
        game.players.add(player)
        
        return Response(
            GameDetailSerializer(game).data,
            status=status.HTTP_201_CREATED
        )

class JoinGameView(APIView):
    """Join an existing game"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, game_id):
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"detail": "Game not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        player = request.user.monopoly_player
        
        if not game.can_join(player)[0]:
            return Response(
                {"detail": game.can_join(player)[1]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        game.players.add(player)
        game.save()
        
        return Response(GameDetailSerializer(game).data)

class StartGameView(APIView):
    """Start a game"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, game_id):
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"detail": "Game not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        player = request.user.monopoly_player
        
        if game.created_by != player:
            return Response(
                {"detail": "Only the game creator can start the game"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        can_start, errors = game.can_start(player)
        if not can_start:
            return Response(
                {"detail": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        game.start_game()
        
        # Broadcast via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game_id}',
            {
                'type': 'game_started',
                'data': GameDetailSerializer(game).data
            }
        )
        
        return Response(GameDetailSerializer(game).data)

class GameStatusView(APIView):
    """Get game status"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, game_id):
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"detail": "Game not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(GameDetailSerializer(game).data)