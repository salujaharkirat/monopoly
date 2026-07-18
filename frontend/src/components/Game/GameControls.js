// frontend/src/components/Game/GameControls.js
import React from 'react';
import './GameControls.css';

const GameControls = ({ 
  game,
  isCreator, 
  isMyTurn, 
  isWaiting, 
  isPlaying, 
  isRolling,
  onStartGame, 
  onRollDice, 
  onEndTurn, 
  onBuyProperty,
  onViewProperties
}) => {
  const isDisabled = isRolling || !isPlaying;

  return (
    <div className="game-controls">
      <h3>🎮 Controls</h3>
      
      {isWaiting && isCreator && (
        <button className="btn-start" onClick={onStartGame}>
          🚀 Start Game
        </button>
      )}
      
      {isPlaying && (
        <div className="controls-group">
          <button 
            className="btn-roll" 
            onClick={onRollDice}
            disabled={!isMyTurn || isRolling}
          >
            {isRolling ? '🎲 Rolling...' : '🎲 Roll Dice'}
          </button>
          
          <button 
            className="btn-buy" 
            onClick={onBuyProperty}
            disabled={!isMyTurn || isDisabled}
          >
            🏠 Buy Property
          </button>
          
          <button 
            className="btn-end" 
            onClick={onEndTurn}
            disabled={!isMyTurn || isDisabled}
          >
            ⏭️ End Turn
          </button>
          
          <button 
            className="btn-properties"  
            onClick={onViewProperties}
            disabled={isDisabled}
          >
            📋 My Properties
          </button>
        </div>
      )}
      
      {isPlaying && !isMyTurn && !isRolling && (
        <div className="waiting-message">
          <span className="waiting-icon">⏳</span>
          <span>Waiting for {game?.current_player?.username || 'opponent'}...</span>
        </div>
      )}
      
      {isPlaying && isMyTurn && isRolling && (
        <div className="rolling-message">
          <span className="rolling-icon">🎲</span>
          <span>Rolling dice...</span>
        </div>
      )}
      
      {isWaiting && !isCreator && (
        <div className="waiting-message">
          <span className="waiting-icon">⏳</span>
          <span>Waiting for creator to start the game...</span>
        </div>
      )}
      
      {isPlaying && game?.state === 'PL' && (
        <div className="turn-info">
          <span className="turn-label">Turn:</span>
          <span className="turn-number">{game?.turn_number || 0}</span>
        </div>
      )}
    </div>
  );
};

export default GameControls;