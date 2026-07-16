
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import QuerySet

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
    CreateGameSerializer
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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

class GameListView(generics.ListAPIView):
    """List all available games"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GameSerializer
    
    def get_queryset(self) -> QuerySet[Game]:
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

        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'game_{game_id}',
                {
                    'type': 'game_started',
                    'data': GameDetailSerializer(game).data
                }
            )
        
        return Response(GameDetailSerializer(game).data)