class MonopolyClient {
  constructor(gameId, token) {
    this.gameId = gameId;
    this.token = token;
    this.socket = null;
    this.eventHandlers = new Map();
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const wsUrl = `ws://${window.location.host}/ws/game/${this.gameId}/?token=${this.token}`;
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      this.isConnected = true;
      this.reconnectAttempts = 0;
      console.log('WebSocket connected');
      this.triggerEvent('connected', null);
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message:', data);
      this.handleMessage(data);
    };

    this.socket.onclose = (event) => {
      this.isConnected = false;
      console.log('WebSocket disconnected:', event.code);
      this.triggerEvent('disconnected', event);
      
      // Auto-reconnect
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => {
              console.log(`Reconnecting... (${this.reconnectAttempts})`);
              this.connect();
          }, 2000 * this.reconnectAttempts);
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.triggerEvent('error', error);
    };
  }

  handleMessage(data) {
    switch(data.type) {
      case 'game_started':
        this.triggerEvent('gameStarted', data.data);
        break;
      case 'game_update':
        this.triggerEvent('gameUpdate', data.data);
        break;
      case 'game_state':
        this.triggerEvent('gameState', data.data);
        break;
      case 'player_joined':
        this.triggerEvent('playerJoined', data);
        break;
      case 'player_left':
        this.triggerEvent('playerLeft', data);
        break;
      case 'turn_update':
        this.triggerEvent('turnUpdate', data.data);
        break;
      case 'game_over':
        this.triggerEvent('gameOver', data.data);
        break;
      case 'error':
        this.triggerEvent('error', data.message);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }
  send(action, data = {}) {
    if (!this.isConnected) {
      console.error('WebSocket not connected');
      return;
    }
    this.socket.send(JSON.stringify({
      action: action,
      ...data
    }));
  }
  // === Game Actions ===
  
  startGame() {
      this.send('start_game');
  }

  rollDice() {
      this.send('roll_dice');
  }

  buyProperty(propertyId) {
      this.send('buy_property', { property_id: propertyId });
  }

  endTurn() {
      this.send('end_turn');
  }

  // === Event Handlers ===
  
  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
        this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event).push(handler);
  }

  triggerEvent(event, data) {
    if (this.eventHandlers.has(event)) {
        this.eventHandlers.get(event).forEach(handler => {
            handler(data);
        });
    }
  }

  disconnect() {
    if (this.socket) {
        this.socket.close();
    }
  }
}