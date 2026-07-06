from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Game, Player

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Player
        fields = ['id', 'user', 'username', 'money', 'position', 'is_in_jail', 'is_active']

class GameSerializer(serializers.ModelSerializer):
    player_count = serializers.IntegerField(source='players.count', read_only=True)
    created_by_username = serializers.CharField(source='created_by.user.username', read_only=True)
    
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'state', 'max_players', 'min_players',
            'player_count', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]

class GameDetailSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    player_count = serializers.IntegerField(source='players.count', read_only=True)
    created_by_username = serializers.CharField(source='created_by.user.username', read_only=True)
    current_player = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'state', 'max_players', 'min_players',
            'players', 'player_count', 'current_player_index',
            'turn_number', 'created_by', 'created_by_username',
            'created_at', 'updated_at', 'current_player'
        ]
    
    def get_current_player(self, obj):
        current = obj.get_current_player()
        if current:
            return PlayerSerializer(current).data
        return None

class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['name', 'max_players', 'min_players']