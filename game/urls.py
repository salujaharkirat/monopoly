from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    # Authentication
    
    # Game API Endpoints
    path('', views.GameListView.as_view(), name='game-list'),
    path('create/', views.CreateGameView.as_view(), name='create-game'),
    path('<int:game_id>/', views.GameDetailView.as_view(), name='game-detail'),
    path('<int:game_id>/join/', views.JoinGameView.as_view(), name='join-game'),
    path('<int:game_id>/start/', views.StartGameView.as_view(), name='start-game'),
]