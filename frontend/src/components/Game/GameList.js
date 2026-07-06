import React from 'react';
import './GameList.css';

const GameList = ({ games, onJoinGame, onRefresh }) => {
  if (!games || games.length === 0) {
    return (
      <div className="game-list-empty">
        <p>No games available</p>
        <button onClick={onRefresh} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="game-list">
      {games.map(game => (
        <div key={game.id} className="game-item">
          <div className="game-info">
            <h3>{game.name}</h3>
            <p>Players: {game.player_count}/{game.max_players}</p>
            <p>Created by: {game.created_by_username}</p>
            <p>Status: {game.state}</p>
          </div>
          <button 
            onClick={() => onJoinGame(game.id)}
            className="join-btn"
            disabled={game.player_count >= game.max_players}
          >
            {game.player_count >= game.max_players ? 'Full' : 'Join Game'}
          </button>
        </div>
      ))}
    </div>
  );
};

export default GameList;