from rest_framework import serializers
from .models import Player, Game

class PlayerSerializer(serializers.ModelSerializer):
  username = serializers.CharField(source='user.username', read_only=True)
  email = serializers.EmailField(source='user.email', read_only=True)
    
  class Meta:
    model = Player
    fields = ['id', 'username', 'email', 'money', 'position', 'is_in_jail', 'is_active']
    read_only_fields = ['money', 'position', 'is_in_jail', 'is_active']


class CreateGameSerializer(serializers.ModelSerializer):
  class Meta:
      model = Game
      fields = ['id', 'name', 'max_players', 'min_players']
      read_only_fields = ['id']
  
  def validate_name(self, value):
      if len(value.strip()) < 3:
          raise serializers.ValidationError("Game name must be at least 3 characters")
      if Game.objects.filter(name=value.strip(), state=Game.GameState.WAITING).exists():
          raise serializers.ValidationError("A game with this name already exists")
      return value.strip()
  
  def validate_max_players(self, value):
      if value < 2:
          raise serializers.ValidationError("Game needs at least 2 players")
      if value > 8:
          raise serializers.ValidationError("Game cannot have more than 8 players")
      return value
  
  def validate_min_players(self, value):
      if value < 2:
          raise serializers.ValidationError("Game needs at least 2 players")
      if value > 4:
          raise serializers.ValidationError("Game cannot have more than 4 players as minimum")
      return value
  
  def validate(self, data):
      min_players = data.get('min_players', 2)
      max_players = data.get('max_players', 4)
      if min_players > max_players:
          raise serializers.ValidationError(
              "Min players cannot be greater than max players"
          )
      return data
  
  def create(self, validated_data):
      """Override create to handle the game creation with creator"""
      # Get the player from context
      player = self.context.get('player')
      if not player:
          raise serializers.ValidationError("Player context missing")
      
      # Create the game
      game = Game.objects.create(
          name=validated_data.get('name', "Monopoly Game"),
          max_players=validated_data.get('max_players', 4),
          min_players=validated_data.get('min_players', 2),
          created_by=player
      )
      
      # Add creator as first player
      game.players.add(player)
      
      return game



class JoinGameSerializer(serializers.Serializer):
    # No fields needed since game_id comes from URL
    
  def validate(self, data):
      """Validate player can join the game"""
      request = self.context.get('request')
      game = self.context.get('game')
      
      if not request:
        raise serializers.ValidationError("Authentication required")
      
      if not game:
        raise serializers.ValidationError("Game not found")
      
      # Get the player from authenticated user
      try:
        player = request.user.monopoly_player
      except Player.DoesNotExist:
        raise serializers.ValidationError("Player profile does not exist")
      
      # Check if game is in waiting state
      if game.state != Game.GameState.WAITING:
        raise serializers.ValidationError(
            f"Cannot join game: Game is {game.get_state_display().lower()}"
        )
      
      # Check if game is full
      if game.players.count() >= game.max_players:
        raise serializers.ValidationError(
            f"Game is full (maximum {game.max_players} players)"
        )
      
      # Check if player is already in this game
      if game.players.filter(id=player.id).exists():
        raise serializers.ValidationError("You are already in this game")
      
      # Check if player is active
      if not player.is_active:
        raise serializers.ValidationError("Your player profile is inactive")
      
      # Check if player is already in another active game
      if player.games.filter(
        state__in=[Game.GameState.WAITING, Game.GameState.PLAYING]
      ).exclude(id=game.id).exists():
        raise serializers.ValidationError(
            "You are already in another active game"
        )
      
      # Store player in context
      self.context['player'] = player
      
      return data
    
class GameDetailSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    players_count = serializers.IntegerField(source='players.count', read_only=True)
    created_by_username = serializers.CharField(
      source='created_by.user.username', 
      read_only=True
    )
    is_full = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    
    class Meta:
      model = Game
      fields = [
          'id', 'name', 'state', 'max_players', 'min_players',
          'players', 'current_player_index', 
          'turn_number', 'created_by', 'created_by_username',
          'created_at', 'updated_at', 'is_full', 'can_join', 'players_count'
      ]
      read_only_fields = fields
  
    def get_is_full(self, obj):
      return obj.players.count() >= obj.max_players
    
    def get_can_join(self, obj):
      if 'request' in self.context:
          user = self.context['request'].user
          try:
              player = user.monopoly_player
              can_join, _ = obj.can_join(player)
              return can_join
          except Player.DoesNotExist:
              return False
      return False

class StartGameSerializer():
   pass