// frontend/src/components/Game/GameBoard.js - Updated
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { gameAPI } from '../../services/api';
import websocketService from '../../services/websocket';
import animationService from '../../services/animation';
import { useAuth } from '../../context/AuthContext';
import Board from './Board';
import PlayerList from './PlayerList';
import GameControls from './GameControls';
import Dice from './Dice';
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
  const [diceState, setDiceState] = useState({
    values: null,
    isRolling: false,
    animationComplete: false
  });
  const [movingPlayers, setMovingPlayers] = useState({});
  const [isProcessing, setIsProcessing] = useState(false);
  const wsHandlerRef = useRef();

  useEffect(() => {
    console.log("inside socket...")
    fetchGame();
    websocketService.connect(gameId);
    
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
      animationService.stopAllAnimations();
    };
  }, [gameId]);

  const fetchGame = async () => {
    try {
      setLoading(true);
      const response = await gameAPI.get(gameId);
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
      case 'game_state':
        setGame(data.data);
        break;
      case 'game_started':
        addNotification('🎮 Game started! Good luck!', 'success');
        setGame(data.data);
        break;
      case 'dice_rolled':
        handleDiceRolled(data.data);
        break;
      case 'game_update':
        setGame(data.data);
        break;
      case 'turn_update':
        const nextPlayer = data.data?.current_player?.username || 'Unknown';
        addNotification(`⏰ It's ${nextPlayer}'s turn!`, 'info');
        setGame(data.data);
        setIsProcessing(false);
        setDiceState(prev => ({ ...prev, isRolling: false }));
        break;
      case 'player_joined':
        addNotification(`👋 ${data.username} joined the game`, 'info');
        fetchGame();
        break;
      case 'player_left':
        addNotification(`👋 ${data.username} left the game`, 'info');
        fetchGame();
        break;
      case 'game_over':
        addNotification(`🏆 Game Over! Winner: ${data.data.winner}`, 'success');
        setGame(data.data);
        setIsProcessing(false);
        setDiceState(prev => ({ ...prev, isRolling: false }));
        break;
      case 'error':
        addNotification(`❌ ${data.message}`, 'error');
        setIsProcessing(false);
        setDiceState(prev => ({ ...prev, isRolling: false }));
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const handleDiceRolled = (data) => {
    const { dice, game_state, square_result } = data;
    
    setDiceState({
      values: dice,
      isRolling: true,
      animationComplete: false
    });

    console.log("info..", dice);
    
    // Show dice result notification
    addNotification(`🎲 Rolled ${dice.dice1} + ${dice.dice2} = ${dice.total}${dice.is_doubles ? ' 🎯 Doubles!' : ''}`, 'info');
    
    // Animate player movement
    const playerId = game_state?.current_player?.id;
    if (playerId) {
      setMovingPlayers(prev => ({ ...prev, [playerId]: true }));
      
      // Calculate movement steps
      let currentPos = dice.old_position;
      let stepCount = 0;
      const totalSteps = dice.total;
      
      const interval = setInterval(() => {
        if (stepCount < totalSteps) {
          currentPos = (currentPos + 1) % 40;
          stepCount++;
          
          // Update player position in UI
          setGame(prev => {
            if (!prev) return prev;
            const updatedPlayers = prev.players.map(p => {
              if (p.id === playerId) {
                return { ...p, position: currentPos };
              }
              return p;
            });
            return { ...prev, players: updatedPlayers };
          });
        } else {
          clearInterval(interval);
          setMovingPlayers(prev => ({ ...prev, [playerId]: false }));
          
          // Update with final game state
          setGame(game_state);
          setDiceState(prev => ({ 
            ...prev, 
            isRolling: false, 
            animationComplete: true 
          }));
          setIsProcessing(false);
          
          // Show square result
          if (square_result?.message) {
            addNotification(`📍 ${square_result.message}`, 'info');
          }
          
          // Check if can buy property
          if (square_result?.can_buy) {
            addNotification(`🏠 ${square_result.name} is available for $${square_result.price}`, 'success');
          }
        }
      }, 400); // 400ms per step
    }
  };

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const handleRollDice = () => {
    if (diceState.isRolling || isProcessing) return;
    setIsProcessing(true);
    websocketService.send({ action: 'roll_dice' });
  };

  const handleBuyProperty = () => {
    // Will implement later
    addNotification('🏠 Buying property - Coming soon!', 'info');
  };

  const handleEndTurn = () => {
    if (diceState.isRolling || isProcessing) return;
    // Only end turn if not doubles
    if (diceState.values?.is_doubles) {
      addNotification('🎯 You rolled doubles! Roll again!', 'info');
      return;
    }
    setIsProcessing(true);
    websocketService.send({ action: 'end_turn' });
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
  const isMyTurn = game.current_player?.username === user?.username;
  const isWaiting = game.state === 'WT' || game.state === 'WAITING';
  const isPlaying = game.state === 'PL' || game.state === 'PLAYING';

  return (
    <div className="game-board">
      <div className="game-header">
        <h1>🎲 {game.name}</h1>
        <div className="game-status">
          <span className={`status-badge ${game.state}`}>
            {game.state === 'WT' ? '⏳ Waiting' : 
             game.state === 'PL' ? '🎮 Playing' : 
             '🏁 Finished'}
          </span>
          <span>Turn: {game.turn_number}</span>
          <span>Players: {game.player_count}/{game.max_players}</span>
        </div>
        <button className="leave-btn" onClick={handleLeaveGame}>
          🚪 Leave
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
          <Board 
            players={game.players} 
            currentPlayerIndex={game.current_player_index}
            movingPlayers={movingPlayers}
          />
          
          <Dice 
            values={diceState.values}
            isRolling={diceState.isRolling}
            onRollComplete={() => {
              setDiceState(prev => ({ ...prev, animationComplete: true }));
            }}
          />
        </div>
        
        <div className="game-sidebar">
          <PlayerList 
            players={game.players}
            currentPlayerIndex={game.current_player_index}
          />
          
          <GameControls
            game={game}
            isCreator={isCreator}
            isMyTurn={isMyTurn}
            isWaiting={isWaiting}
            isPlaying={isPlaying}
            isRolling={diceState.isRolling}
            onStartGame={handleStartGame}
            onRollDice={handleRollDice}
            onEndTurn={handleEndTurn}
            onBuyProperty={handleBuyProperty}
            onViewProperties={() => addNotification('📋 Properties coming soon!', 'info')}
          />
        </div>
      </div>
    </div>
  );
};

export default GameBoard;