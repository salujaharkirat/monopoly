// frontend/src/services/websocket.js
class WebSocketService {
  constructor() {
    this.socket = null;
    this.messageHandlers = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.isConnected = false;
  }

  connect(gameId) {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('No token found for WebSocket connection');
      return;
    }

    // Avoid opening a second socket if one is already open/connecting
    if (this.socket && this.socket.readyState <= WebSocket.OPEN) {
      return;
    }

    this.intentionalClose = false;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//localhost:8001/ws/game/${gameId}/?token=${token}`;
    
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
    };
    
    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.messageHandlers.forEach(handler => handler(data));
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    this.socket.onclose = (event) => {
      console.log('WebSocket disconnected');
      this.isConnected = false;
      
      // Don't reconnect if it was a 4001 (authentication failure)
      if (event.code === 4001) {
        console.error('WebSocket authentication failed');
        return;
      }

      // Don't reconnect if we closed the socket on purpose (e.g. unmount)
      if (this.intentionalClose) {
        return;
      }

      // Auto-reconnect
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => {
          console.log(`Reconnecting... (${this.reconnectAttempts})`);
          this.connect(gameId);
        }, 2000 * this.reconnectAttempts);
      }
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  disconnect() {
    if (this.socket) {
      this.intentionalClose = true;
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
    }
  }

  send(data) {
    if (this.isConnected && this.socket) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.error('WebSocket not connected');
    }
  }

  onMessage(handler) {
    this.messageHandlers.push(handler);
  }

  removeMessageHandler(handler) {
    this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
  }
}

export default new WebSocketService();