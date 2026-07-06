import React from 'react';
import './PlayerList.css';

const PlayerList = ({ players, currentPlayerIndex }) => {
  if (!players) return null;

  return (
    <div className="player-list">
      <h3>Players</h3>
      {players.map((player, index) => (
        <div 
          key={player.id} 
          className={`player-card ${index === currentPlayerIndex ? 'current-player' : ''}`}
        >
          <div className="player-name">
            <strong>{player.username}</strong>
            {index === currentPlayerIndex && <span className="turn-indicator">🎯</span>}
          </div>
          <div className="player-stats">
            <span>💰 ${player.money}</span>
            <span>📍 {player.position}</span>
            <span>{player.is_in_jail ? '🔒 In Jail' : '✅ Free'}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PlayerList;