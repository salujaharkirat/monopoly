import React from 'react';
import './GameList.css';

const GameList = ({ games, user, onStartGame, onJoinGame, onRefresh, navigateToGame }) => {
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
          {
            game.state != 'PL' &&  (
            <button 
              onClick={() => onStartGame(game.id)}
              className="join-btn"
            >
              {user.userName === game.created_by_username ? "Start Game" : "Join Game"}
            </button>
            )
          }
          {
            game.state == 'PL' && (
              <button 
              onClick={() => navigateToGame(game.id)}
              className="join-btn"
              >
                Go to Game
            </button>
            )
          }

        </div>
      ))}
    </div>
  );
};

export default GameList;