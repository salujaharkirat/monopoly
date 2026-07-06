// frontend/src/components/Game/Board.js
import React from 'react';
import './Board.css';

const BOARD_SQUARES = [
    {"id": 0, "name": "GO", "type": "go", "color": null},
    {"id": 1, "name": "Mediterranean Avenue", "type": "property", "color": "brown", "price": 60, "rent": 2},
    {"id": 2, "name": "Community Chest", "type": "community_chest", "color": null},
    {"id": 3, "name": "Baltic Avenue", "type": "property", "color": "brown", "price": 60, "rent": 4},
    {"id": 4, "name": "Income Tax", "type": "tax", "color": null, "amount": 200},
    {"id": 5, "name": "Reading Railroad", "type": "railroad", "color": "railroad", "price": 200, "rent": 25},
    {"id": 6, "name": "Oriental Avenue", "type": "property", "color": "light_blue", "price": 100, "rent": 6},
    {"id": 7, "name": "Chance", "type": "chance", "color": null},
    {"id": 8, "name": "Vermont Avenue", "type": "property", "color": "light_blue", "price": 100, "rent": 6},
    {"id": 9, "name": "Connecticut Avenue", "type": "property", "color": "light_blue", "price": 120, "rent": 8},
    {"id": 10, "name": "Jail / Just Visiting", "type": "jail", "color": null},
    {"id": 11, "name": "St. Charles Place", "type": "property", "color": "pink", "price": 140, "rent": 10},
    {"id": 12, "name": "Electric Company", "type": "utility", "color": "utility", "price": 150, "rent": 0},
    {"id": 13, "name": "States Avenue", "type": "property", "color": "pink", "price": 140, "rent": 10},
    {"id": 14, "name": "Virginia Avenue", "type": "property", "color": "pink", "price": 160, "rent": 12},
    {"id": 15, "name": "Pennsylvania Railroad", "type": "railroad", "color": "railroad", "price": 200, "rent": 25},
    {"id": 16, "name": "St. James Place", "type": "property", "color": "orange", "price": 180, "rent": 14},
    {"id": 17, "name": "Community Chest", "type": "community_chest", "color": null},
    {"id": 18, "name": "Tennessee Avenue", "type": "property", "color": "orange", "price": 180, "rent": 14},
    {"id": 19, "name": "New York Avenue", "type": "property", "color": "orange", "price": 200, "rent": 16},
    {"id": 20, "name": "Free Parking", "type": "free_parking", "color": null},
    {"id": 21, "name": "Kentucky Avenue", "type": "property", "color": "red", "price": 220, "rent": 18},
    {"id": 22, "name": "Chance", "type": "chance", "color": null},
    {"id": 23, "name": "Indiana Avenue", "type": "property", "color": "red", "price": 220, "rent": 18},
    {"id": 24, "name": "Illinois Avenue", "type": "property", "color": "red", "price": 240, "rent": 20},
    {"id": 25, "name": "B. & O. Railroad", "type": "railroad", "color": "railroad", "price": 200, "rent": 25},
    {"id": 26, "name": "Atlantic Avenue", "type": "property", "color": "yellow", "price": 260, "rent": 22},
    {"id": 27, "name": "Ventnor Avenue", "type": "property", "color": "yellow", "price": 260, "rent": 22},
    {"id": 28, "name": "Water Works", "type": "utility", "color": "utility", "price": 150, "rent": 0},
    {"id": 29, "name": "Marvin Gardens", "type": "property", "color": "yellow", "price": 280, "rent": 24},
    {"id": 30, "name": "Go To Jail", "type": "go_to_jail", "color": null},
    {"id": 31, "name": "Pacific Avenue", "type": "property", "color": "green", "price": 300, "rent": 26},
    {"id": 32, "name": "North Carolina Avenue", "type": "property", "color": "green", "price": 300, "rent": 26},
    {"id": 33, "name": "Community Chest", "type": "community_chest", "color": null},
    {"id": 34, "name": "Pennsylvania Avenue", "type": "property", "color": "green", "price": 320, "rent": 28},
    {"id": 35, "name": "Short Line", "type": "railroad", "color": "railroad", "price": 200, "rent": 25},
    {"id": 36, "name": "Chance", "type": "chance", "color": null},
    {"id": 37, "name": "Park Place", "type": "property", "color": "dark_blue", "price": 350, "rent": 35},
    {"id": 38, "name": "Luxury Tax", "type": "tax", "color": null, "amount": 100},
    {"id": 39, "name": "Boardwalk", "type": "property", "color": "dark_blue", "price": 400, "rent": 50},
];

const Board = ({ players, currentPlayerIndex, movingPlayers }) => {
  const getPlayerTokens = (position) => {
    if (!players) return [];
    return players.filter(p => p.position === position);
  };
  
  const renderSquare = (index) => {
    const square = BOARD_SQUARES[index];
    const playersOnSquare = getPlayerTokens(index);
    const isMoving = playersOnSquare.some(p => movingPlayers?.[p.id]);
    
    return (
      <div key={index} className={`board-square ${square.type}`}>
        {square.color && <div className="color-strip" style={{ background: square.color }} />}
        <div className="square-name">{square.name}</div>
        {playersOnSquare.length > 0 && (
          <div className="player-tokens">
            {playersOnSquare.map((p, idx) => (
              <div 
                key={p.id} 
                className={`player-token ${idx === currentPlayerIndex ? 'active' : ''} ${movingPlayers?.[p.id] ? 'moving' : ''}`}
                style={{ background: getPlayerColor(idx) }}
                title={p.username}
              >
                {p.username[0].toUpperCase()}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const getPlayerColor = (index) => {
    const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#2c3e50'];
    return colors[index % colors.length];
  };

  return (
    <div className="board">
      <div className="board-row top-row">
        {[20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30].map(i => renderSquare(i))}
      </div>
      <div className="board-row middle-rows">
        <div className="board-left">
          {[19, 18, 17, 16, 15, 14, 13, 12, 11].map(i => renderSquare(i))}
        </div>
        <div className="board-center">
          {/* Board center - Monopoly logo or game info */}
        </div>
        <div className="board-right">
          {[31, 32, 33, 34, 35, 36, 37, 38, 39].map(i => renderSquare(i))}
        </div>
      </div>
      <div className="board-row bottom-row">
        {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0].map(i => renderSquare(i))}
      </div>
    </div>
  );
};

export default Board;