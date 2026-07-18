// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ✅ Add token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ✅ Handle 401 errors (token expired/invalid)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (username, password) => 
    api.post('/auth/login/', { username, password }),
  register: (data) => 
    api.post('/auth/register/', data),
  logout: () => 
    api.post('/auth/logout/'),
  getCurrentUser: () => 
    api.get('/auth/me/'),
};

// Game APIs
export const gameAPI = {
  list: () => 
    api.get('/games/'),
  create: (data) => 
    api.post('/games/create/', data),
  get: (gameId) => 
    api.get(`/games/${gameId}/`),
  join: (gameId) => 
    api.post(`/games/${gameId}/join/`),
  start: (gameId) => 
    api.post(`/games/${gameId}/start/`),
  status: (gameId) => 
    api.get(`/games/${gameId}/status/`),
  leave: (gameId) => 
    api.post(`/games/${gameId}/leave/`),
};

export default api;