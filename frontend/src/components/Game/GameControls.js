import React from 'react';
import './GameControls.css';

const GameControls = ({ 
  isCreator, 
  isMyTurn, 
  isWaiting, 
  isPlaying, 
  onStartGame, 
  onRollDice, 
  onEndTurn, 
  onBuyProperty 
}) => {
  return (
    <div className="game-controls">
      <h3>Controls</h3>
      
      {isWaiting && isCreator && (
        <button className="btn-start" onClick={onStartGame}>
          🎮 Start Game
        </button>
      )}
      
      {isPlaying && isMyTurn && (
        <>
          <button className="btn-roll" onClick={onRollDice}>
            🎲 Roll Dice
          </button>
          <button className="btn-buy" onClick={onBuyProperty}>
            🏠 Buy Property
          </button>
          <button className="btn-end" onClick={onEndTurn}>
            ⏭️ End Turn
          </button>
        </>
      )}
      
      {isPlaying && !isMyTurn && (
        <div className="waiting-message">
          ⏳ Waiting for {isCreator ? 'creator' : 'other player'}...
        </div>
      )}
      
      {isWaiting && !isCreator && (
        <div className="waiting-message">
          ⏳ Waiting for creator to start the game...
        </div>
      )}
    </div>
  );
};

export default GameControls;