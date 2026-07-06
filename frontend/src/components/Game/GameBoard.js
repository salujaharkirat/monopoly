// frontend/src/components/Game/GameBoard.js
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { gameAPI } from '../../services/api';
import websocketService from '../../services/websocket';
import { useAuth } from '../../context/AuthContext';
import PlayerList from './PlayerList';
import GameControls from './GameControls';
import Loading from '../Common/Loading';
import './GameBoard.css';

const GameBoard = () => {
  const { gameId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const wsHandlerRef = useRef();

  useEffect(() => {
    fetchGame();
    
    // Connect WebSocket
    websocketService.connect(gameId);
    
    // Add WebSocket message handler
    const handler = (data) => {
      console.log('WebSocket message:', data);
      handleWebSocketMessage(data);
    };
    websocketService.onMessage(handler);
    wsHandlerRef.current = handler;
    
    return () => {
      websocketService.disconnect();
      if (wsHandlerRef.current) {
        websocketService.removeMessageHandler(wsHandlerRef.current);
      }
    };
  }, [gameId]);

  const fetchGame = async () => {
    try {
      setLoading(true);
      const response = await gameAPI.status(gameId);
      setGame(response.data);
      setError(null);
    } catch (error) {
      console.error('Error fetching game:', error);
      if (error.response?.status === 404) {
        navigate('/');
      } else {
        setError('Failed to load game');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleWebSocketMessage = (data) => {
    switch(data.type) {
      case 'game_started':
        addNotification('Game started! Good luck!', 'success');
        setGame(data.data);
        break;
      case 'game_update':
        setGame(data.data);
        break;
      case 'turn_update':
        addNotification(`It's ${data.data.current_player?.username}'s turn!`, 'info');
        setGame(data.data);
        break;
      case 'player_joined':
        addNotification(`${data.username} joined the game`, 'info');
        fetchGame();
        break;
      case 'player_left':
        addNotification(`${data.username} left the game`, 'info');
        fetchGame();
        break;
      case 'game_over':
        addNotification(`Game Over! Winner: ${data.data.winner}`, 'success');
        setGame(data.data);
        break;
      case 'error':
        addNotification(`Error: ${data.message}`, 'error');
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const handleStartGame = async () => {
    try {
      await gameAPI.start(gameId);
    } catch (error) {
      console.error('Error starting game:', error);
      addNotification(error.response?.data?.detail || 'Failed to start game', 'error');
    }
  };

  const handleLeaveGame = async () => {
    if (!window.confirm('Are you sure you want to leave this game?')) {
      return;
    }
    
    try {
      await gameAPI.leave(gameId);
      navigate('/');
    } catch (error) {
      console.error('Error leaving game:', error);
      addNotification(error.response?.data?.detail || 'Failed to leave game', 'error');
    }
  };

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return <div className="error-container">{error}</div>;
  }

  if (!game) {
    return <div>Game not found</div>;
  }

  const isCreator = game.created_by_username === user?.username;
  const currentPlayer = game.players?.[game.current_player_index];
  const isMyTurn = currentPlayer?.username === user?.username;
  const isWaiting = game.state === 'WT';
  const isPlaying = game.state === 'PL';

  return (
    <div className="game-board">
      <div className="game-header">
        <h1>{game.name}</h1>
        <div className="game-status">
          <span>Status: {game.state}</span>
          <span>Turn: {game.turn_number}</span>
          <span>Players: {game.player_count}/{game.max_players}</span>
        </div>
        <button className="leave-btn" onClick={handleLeaveGame}>
          Leave Game
        </button>
      </div>
      
      <div className="notifications">
        {notifications.map(notif => (
          <div key={notif.id} className={`notification ${notif.type}`}>
            {notif.message}
          </div>
        ))}
      </div>
      
      <div className="game-content">
        <div className="game-main">
          <div className="game-board-display">
            {/* Board visualization will go here */}
            <div className="board-placeholder">
              🎲 Monopoly Board
              <p>Board visualization coming soon!</p>
            </div>
          </div>
        </div>
        
        <div className="game-sidebar">
          <PlayerList 
            players={game.players}
            currentPlayerIndex={game.current_player_index}
          />
          
          <GameControls
            isCreator={isCreator}
            isMyTurn={isMyTurn}
            isWaiting={isWaiting}
            isPlaying={isPlaying}
            onStartGame={handleStartGame}
            onRollDice={() => console.log('Roll dice')}
            onEndTurn={() => console.log('End turn')}
            onBuyProperty={() => console.log('Buy property')}
          />
        </div>
      </div>
    </div>
  );
};

export default GameBoard;