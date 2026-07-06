from django.urls import path

from .views import CreateGameView, JoinGameView, StartGameView, GameStatusView

app_name = 'game'

urlpatterns = [
    # Create game - uses CreateGameSerializer
    path('create/', CreateGameView.as_view(), name='create-game'),
    path('<int:game_id>/join/', JoinGameView.as_view(), name='join-game'),
    path('<int:game_id>/start/', StartGameView.as_view(), name='start-game'),
    path('<int:game_id>/status/', GameStatusView.as_view(), name='game-status'),
]