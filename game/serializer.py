from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from . import turn_order
from .models import Game, Player, Square, Property

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
        fields = ['id', 'user', 'username', 'money', 'position', 'is_in_jail', 'get_out_of_jail_cards', 'is_active']

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

class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['name', 'max_players', 'min_players']

class SquareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Square
        fields = '__all__'

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'square', 'owner', 'houses', 'is_mortgaged']


class GameDetailSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    player_count = serializers.IntegerField(source='players.count', read_only=True)
    created_by_username = serializers.CharField(source='created_by.user.username', read_only=True)
    current_player = serializers.SerializerMethodField()
    squares = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'state', 'max_players', 'min_players',
            'players', 'player_count', 'current_player_index',
            'turn_number', 'created_by', 'created_by_username',
            'created_at', 'updated_at', 'current_player', 'squares', 'properties'
        ]
    
    def get_current_player(self, obj):
        current = turn_order.get_current_player(obj)
        if current:
            return PlayerSerializer(current).data
        return None
    
    def get_squares(self, obj):
        squares = Square.objects.all().order_by('position')
        return SquareSerializer(squares, many=True).data

    def get_properties(self, obj):
        properties = Property.objects.filter(game=obj).select_related('square', 'owner')
        return PropertySerializer(properties, many=True).data