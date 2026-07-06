from django.urls import path

from .views import CreateGameView, JoinGameView

app_name = 'game'

urlpatterns = [
    # Create game - uses CreateGameSerializer
    path('create/', CreateGameView.as_view(), name='create-game'),
    
    # Alternative: Join specific game
    path('<int:game_id>/join/', JoinGameView.as_view(), name='join-game-by-id'),
]