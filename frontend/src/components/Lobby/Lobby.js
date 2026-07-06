// frontend/src/components/Lobby/Lobby.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { gameAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import CreateGameForm from './CreateGameForm';
import GameList from '../Game/GameList';
import Loading from '../Common/Loading';
import './Lobby.css';

const Lobby = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchGames();
  }, []);

  const fetchGames = async () => {
    try {
      setLoading(true);
      const response = await gameAPI.list();
      setGames(response.data);
      setError(null);
    } catch (error) {
      console.error('Error fetching games:', error);
      setError('Failed to load games');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGame = async (gameId) => {
    try {
      await gameAPI.join(gameId);
      navigate(`/game/${gameId}`);
    } catch (error) {
      console.error('Error joining game:', error);
      alert(error.response?.data?.detail || 'Failed to join game');
    }
  };

  const handleGameCreated = (game) => {
    navigate(`/game/${game.id}`);
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="lobby">
      <h1>🎲 Monopoly Game Lobby</h1>
      <p>Welcome, {user?.username}!</p>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="lobby-content">
        <div className="games-section">
          <h2>Available Games</h2>
          <GameList 
            games={games} 
            onJoinGame={handleJoinGame}
            onRefresh={fetchGames}
          />
        </div>
        
        <div className="create-section">
          <CreateGameForm onGameCreated={handleGameCreated} />
        </div>
      </div>
    </div>
  );
};

export default Lobby;