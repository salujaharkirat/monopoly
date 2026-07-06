from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Player, Game
from .serializer import CreateGameSerializer, GameDetailSerializer, JoinGameSerializer

class CreateGameView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  
  def post(self, request):
      # Get or create player
      player, created = Player.objects.get_or_create(
          user=request.user,
          defaults={'money': 2000}
      )
      
      # Check if player already in an active game
      if player.games.filter(
          state__in=[Game.GameState.WAITING, Game.GameState.PLAYING]
      ).exists():
          return Response(
              {"detail": "You are already in an active game"},
              status=status.HTTP_400_BAD_REQUEST
          )
      
      # Validate and create game using serializer
      serializer = CreateGameSerializer(
          data=request.data,
          context={'player': player, 'request': request}  # Pass player to serializer
      )
      serializer.is_valid(raise_exception=True)
      
      # ✅ Serializer's create method handles the game creation
      game = serializer.save()
      
      # Return game details
      response_serializer = GameDetailSerializer(
          game, 
          context={'request': request}
      )
      return Response(
          response_serializer.data,
          status=status.HTTP_201_CREATED
      )
class JoinGameView(APIView):
  """
  API to join an existing game by ID
  POST /api/games/join/
  """
  permission_classes = [permissions.IsAuthenticated]
  
  def post(self, request, game_id):
    # Validate request
    player, created = Player.objects.get_or_create(
        user=request.user,
        defaults={
            'money': 2000,
            'position': 0,
            'is_in_jail': False,
            'is_active': True
        }
    )
    game = get_object_or_404(Game, id=game_id)

    serializer = JoinGameSerializer(
        data={},
        context={
          'request': request,
          'game': game
        }
    )
    serializer.is_valid(raise_exception=True)
    
    # Get validated data
    game = serializer.context['game']
    player = serializer.context['player']
    
    # Add player to game
    game.players.add(player)
    game.save()
    
    # Return updated game details
    response_serializer = GameDetailSerializer(
        game,
        context={'request': request}
    )

    return Response(
        response_serializer.data,
        status=status.HTTP_200_OK
    )