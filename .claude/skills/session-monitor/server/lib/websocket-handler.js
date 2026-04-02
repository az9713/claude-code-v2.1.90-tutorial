const WebSocket = require('ws');

const HEARTBEAT_INTERVAL_MS = 5000;

class WebSocketHandler {
  /**
   * Manages WebSocket connections for the session-monitor skill.
   *
   * Handles client connections, inbound client messages, and outbound
   * broadcasts (full state, incremental updates, heartbeats).
   *
   * @param {object} options
   * @param {import('ws').WebSocketServer} options.wss - The WebSocketServer instance
   */
  constructor({ wss }) {
    this.wss = wss;
    this.clients = new Set();
    this.getStateFn = null;
    this.heartbeatInterval = null;

    this._setupConnectionHandler();
    this._startHeartbeat();
  }

  /**
   * Registers the callback used to retrieve current session state.
   * Must be called before clients begin connecting, or the initial
   * full_state send will be skipped.
   *
   * @param {() => { sessions: object[] }} getStateFn - Returns current state
   */
  init(getStateFn) {
    if (typeof getStateFn !== 'function') {
      throw new Error('[websocket-handler] getStateFn must be a function');
    }
    this.getStateFn = getStateFn;
  }

  /**
   * Broadcasts a typed message to all currently open client connections.
   * Clients whose sockets are no longer in the OPEN state are removed
   * from the tracked set before sending.
   *
   * @param {string} type - Message type identifier
   * @param {object} data - Payload to include under the `data` key
   */
  broadcast(type, data) {
    // Remove dead connections before broadcasting
    for (const client of this.clients) {
      if (client.readyState !== WebSocket.OPEN) {
        this.clients.delete(client);
      }
    }

    for (const client of this.clients) {
      this._sendToClient(client, type, data);
    }
  }

  /**
   * Broadcasts a full session list update to all connected clients.
   *
   * @param {object[]} sessions - Array of session records
   */
  broadcastSessionsUpdate(sessions) {
    this.broadcast('sessions_update', { sessions });
  }

  /**
   * Broadcasts a session-removed notification to all connected clients.
   *
   * @param {string} sessionId - The ID of the session that was removed
   */
  broadcastSessionRemoved(sessionId) {
    this.broadcast('session_removed', { sessionId });
  }

  /**
   * Returns the number of clients currently in the OPEN state.
   *
   * @returns {number}
   */
  getClientCount() {
    let count = 0;
    for (const client of this.clients) {
      if (client.readyState === WebSocket.OPEN) {
        count++;
      }
    }
    return count;
  }

  /**
   * Stops the heartbeat interval and closes all active client connections.
   * Safe to call multiple times.
   */
  shutdown() {
    if (this.heartbeatInterval !== null) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    for (const client of this.clients) {
      if (client.readyState === WebSocket.OPEN) {
        client.close();
      }
    }

    this.clients.clear();
  }

  // ---------------------------------------------------------------------------
  // Private methods
  // ---------------------------------------------------------------------------

  /**
   * Attaches the `connection` listener to the WebSocketServer.
   * Each new client receives a full_state snapshot immediately on connect.
   */
  _setupConnectionHandler() {
    this.wss.on('connection', (ws) => {
      this.clients.add(ws);

      // Send current state immediately on connection
      if (this.getStateFn !== null) {
        try {
          const state = this.getStateFn();
          this._sendToClient(ws, 'full_state', state);
        } catch (error) {
          console.warn(`[websocket-handler] Failed to send full_state on connect: ${error.message}`);
        }
      }

      ws.on('message', (raw) => {
        this._handleClientMessage(ws, raw);
      });

      ws.on('close', () => {
        this.clients.delete(ws);
      });

      ws.on('error', (error) => {
        console.warn(`[websocket-handler] Client socket error: ${error.message}`);
        this.clients.delete(ws);
      });
    });
  }

  /**
   * Parses and dispatches a raw message received from a client.
   *
   * Supported message types:
   *   - `refresh` — responds with a fresh full_state
   *
   * @param {import('ws').WebSocket} ws - The sending client
   * @param {Buffer|string} raw - Raw message data
   */
  _handleClientMessage(ws, raw) {
    let message;
    try {
      message = JSON.parse(raw.toString());
    } catch (error) {
      console.warn(`[websocket-handler] Received non-JSON message, ignoring: ${error.message}`);
      return;
    }

    const { type } = message;

    switch (type) {
      case 'refresh': {
        if (this.getStateFn === null) {
          console.warn('[websocket-handler] refresh requested but getStateFn not initialised');
          return;
        }
        try {
          const state = this.getStateFn();
          this._sendToClient(ws, 'full_state', state);
        } catch (error) {
          console.warn(`[websocket-handler] Failed to handle refresh: ${error.message}`);
        }
        break;
      }

      default:
        console.warn(`[websocket-handler] Unknown message type from client: ${type}`);
    }
  }

  /**
   * Starts the 5-second heartbeat that broadcasts client count to all peers.
   */
  _startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.broadcast('heartbeat', { clientCount: this.getClientCount() });
    }, HEARTBEAT_INTERVAL_MS);

    // Prevent the interval from keeping the process alive on its own
    if (this.heartbeatInterval.unref) {
      this.heartbeatInterval.unref();
    }
  }

  /**
   * Serialises and sends a typed envelope to a single client.
   *
   * Envelope shape: `{ type, data, timestamp }`
   *
   * Silently drops the send if the socket is not in the OPEN state.
   *
   * @param {import('ws').WebSocket} ws - Target client
   * @param {string} type - Message type identifier
   * @param {object} data - Payload
   */
  _sendToClient(ws, type, data) {
    if (ws.readyState !== WebSocket.OPEN) {
      return;
    }

    const envelope = JSON.stringify({ type, data, timestamp: new Date().toISOString() });

    try {
      ws.send(envelope);
    } catch (error) {
      console.warn(`[websocket-handler] Failed to send message to client: ${error.message}`);
    }
  }
}

module.exports = { WebSocketHandler };
