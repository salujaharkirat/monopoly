// frontend/src/components/Lobby/CreateGameForm.js
import React, { useState } from 'react';
import { gameAPI } from '../../services/api';
import './CreateGameForm.css';

const CreateGameForm = ({ onGameCreated }) => {
  const [formData, setFormData] = useState({
    name: '',
    max_players: 4,
    min_players: 2,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'name' ? value : parseInt(value)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Game name is required');
      return;
    }
    
    if (formData.name.length < 3) {
      setError('Game name must be at least 3 characters');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await gameAPI.create(formData);
      onGameCreated(response.data);
    } catch (error) {
      console.error('Error creating game:', error);
      setError(error.response?.data?.detail || 'Failed to create game');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-game-form">
      <h3>Create New Game</h3>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Game Name</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Enter game name"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="max_players">Maximum Players</label>
          <select
            id="max_players"
            name="max_players"
            value={formData.max_players}
            onChange={handleChange}
          >
            {[2, 3, 4, 5, 6, 7, 8].map(num => (
              <option key={num} value={num}>{num} Players</option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="min_players">Minimum Players</label>
          <select
            id="min_players"
            name="min_players"
            value={formData.min_players}
            onChange={handleChange}
          >
            {[2, 3, 4].map(num => (
              <option key={num} value={num}>{num} Players</option>
            ))}
          </select>
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create Game'}
        </button>
      </form>
    </div>
  );
};

export default CreateGameForm;