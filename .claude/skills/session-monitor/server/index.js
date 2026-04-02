const http = require('http');
const path = require('path');
const os = require('os');
const fs = require('fs').promises;
const fssync = require('fs');
const readline = require('readline');
const express = require('express');
const { WebSocketServer } = require('ws');

const { SessionScanner } = require('./lib/session-scanner');
const { SessionEnricher } = require('./lib/session-enricher');
const { PidChecker } = require('./lib/pid-checker');
const { FileWatcher } = require('./lib/file-watcher');
const { WebSocketHandler } = require('./lib/websocket-handler');

// Configuration
const PORT = parseInt(process.env.SESSION_MONITOR_PORT, 10) || 3848;
const POLL_INTERVAL_MS = 10000; // Re-check PIDs and transcript mtimes every 10s

// Initialize Express
const app = express();
const server = http.createServer(app);

// Serve dashboard
app.use(express.static(path.join(__dirname, 'public')));
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// Initialize components
const scanner = new SessionScanner();
const enricher = new SessionEnricher();
const pidChecker = new PidChecker();
const watcher = new FileWatcher();

// In-memory session store: sessionId -> enrichedSession
const sessions = new Map();

// Initialize WebSocket
const wss = new WebSocketServer({ server });
const wsHandler = new WebSocketHandler({ wss });

wss.on('error', (err) => {
  if (err && err.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use. Try: SESSION_MONITOR_PORT=3849 node index.js`);
  } else {
    console.error(`[session-monitor] WebSocket server error: ${err ? err.message : 'unknown error'}`);
  }
});

wsHandler.init(() => ({
  sessions: Array.from(sessions.values())
}));

function buildDefaultAliveMap(pids, defaultAlive = true) {
  const map = new Map();
  for (const pid of pids) {
    map.set(pid, defaultAlive);
  }
  return map;
}

async function safeCheckAllPids(pids, defaultAlive = true) {
  if (!Array.isArray(pids) || pids.length === 0) {
    return new Map();
  }

  try {
    return await pidChecker.checkAll(pids);
  } catch (error) {
    console.warn(`[session-monitor] PID check failed; using default isAlive=${defaultAlive}: ${error.message}`);
    return buildDefaultAliveMap(pids, defaultAlive);
  }
}

function hasSessionChanged(prev, next) {
  if (!prev) return true;

  const keys = [
    'isAlive',
    'lastActivity',
    'messageCount',
    'firstPrompt',
    'gitBranch',
    'modified',
    'hasSubagents',
    'sessionType',
    'teamName',
    'projectName',
  ];

  return keys.some((k) => prev[k] !== next[k]);
}

/**
 * Extracts a lightweight summary from a session's JSONL transcript.
 * Streams through the file to count messages by role, tally tool usage,
 * collect touched file paths, and determine the time range.
 *
 * @param {string} jsonlPath
 * @returns {Promise<object>}
 */
async function extractSessionSummary(jsonlPath) {
  const summary = {
    userMessages: 0,
    assistantMessages: 0,
    toolCalls: {},      // toolName -> count
    filesTouched: [],   // unique file paths from tool calls
    firstTimestamp: null,
    lastTimestamp: null,
    fileSizeBytes: 0,
  };

  try {
    const stat = await fs.stat(jsonlPath);
    summary.fileSizeBytes = stat.size;
  } catch {
    return summary;
  }

  const filesSet = new Set();

  try {
    const stream = fssync.createReadStream(jsonlPath, { encoding: 'utf8' });
    const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });

    for await (const line of rl) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      let entry;
      try {
        entry = JSON.parse(trimmed);
      } catch {
        continue;
      }

      // Track timestamps
      const ts = entry.timestamp || entry.ts || null;
      if (ts) {
        if (!summary.firstTimestamp) summary.firstTimestamp = ts;
        summary.lastTimestamp = ts;
      }

      // Count by role
      const role = entry.role || (entry.message && entry.message.role) || null;
      if (role === 'user') summary.userMessages++;
      else if (role === 'assistant') summary.assistantMessages++;

      // Extract tool usage from assistant messages
      const content = entry.content || (entry.message && entry.message.content) || null;
      if (Array.isArray(content)) {
        for (const block of content) {
          if (block && block.type === 'tool_use') {
            const name = block.name || 'unknown';
            summary.toolCalls[name] = (summary.toolCalls[name] || 0) + 1;

            // Extract file paths from tool inputs
            const input = block.input;
            if (input) {
              const fp = input.file_path || input.path || input.filePath || null;
              if (fp && typeof fp === 'string') filesSet.add(fp);
              // Bash commands — just note that Bash was used, don't parse
              if (input.command && name === 'Bash') {
                // already counted above
              }
            }
          }
        }
      }
    }
  } catch (error) {
    if (error.code !== 'ENOENT') {
      console.warn(`[session-monitor] Could not read transcript ${jsonlPath}: ${error.message}`);
    }
  }

  summary.filesTouched = Array.from(filesSet).slice(0, 50); // cap at 50
  return summary;
}

// ---- Core scan + enrich logic ----

async function fullScan() {
  try {
    const rawSessions = await scanner.scan();
    const pids = Array.from(rawSessions.keys());
    const aliveMap = await safeCheckAllPids(pids, true);

    const enriched = await Promise.all(
      Array.from(rawSessions.values()).map(session =>
        enricher.enrich(session, aliveMap.get(session.pid) ?? true)
      )
    );

    sessions.clear();
    for (const s of enriched) {
      if (s.sessionId) {
        sessions.set(s.sessionId, s);
      }
    }

    return enriched;
  } catch (error) {
    console.error(`[session-monitor] fullScan failed: ${error.message}`);
    return [];
  }
}

async function refreshSingle(pid) {
  const rawSessions = await scanner.scan();
  const session = rawSessions.get(Number(pid));
  if (!session) return null;

  const aliveMap = await safeCheckAllPids([session.pid], true);
  const enriched = await enricher.enrich(session, aliveMap.get(session.pid) ?? true);

  if (enriched.sessionId) {
    sessions.set(enriched.sessionId, enriched);
  }
  return enriched;
}

// ---- File watcher events ----

watcher.on('session-changed', async ({ pid }) => {
  try {
    enricher.refreshTeams();
    await refreshSingle(pid);
    wsHandler.broadcastSessionsUpdate(Array.from(sessions.values()));
  } catch (error) {
    console.error(`Error handling session change for PID ${pid}:`, error.message);
  }
});

watcher.on('session-removed', async ({ pid }) => {
  // Find and remove the session with this PID
  for (const [sessionId, session] of sessions) {
    if (String(session.pid) === String(pid)) {
      sessions.delete(sessionId);
      wsHandler.broadcastSessionRemoved(sessionId);
      break;
    }
  }
});

// ---- Polling loop (PID liveness + transcript mtime refresh) ----

let pollTimer = null;

async function pollLoop() {
  try {
    const currentSessions = Array.from(sessions.values());
    if (currentSessions.length === 0) return;

    const pids = currentSessions.map(s => s.pid);
    const aliveMap = await safeCheckAllPids(pids, true);

    // Keep team role data fresh if team configs changed on disk.
    enricher.refreshTeams();

    let changed = false;

    const updatedSessions = await Promise.all(
      currentSessions.map(async (session) => {
        const updated = await enricher.enrich(
          {
            pid: session.pid,
            sessionId: session.sessionId,
            cwd: session.cwd,
            startedAt: session.startedAt
          },
          aliveMap.get(session.pid) ?? session.isAlive ?? true
        );

        if (hasSessionChanged(session, updated)) {
          changed = true;
        }

        return updated;
      })
    );

    if (changed) {
      for (const updated of updatedSessions) {
        sessions.set(updated.sessionId, updated);
      }
      wsHandler.broadcastSessionsUpdate(Array.from(sessions.values()));
    }
  } catch (error) {
    console.error('Poll loop error:', error.message);
  }
}

// ---- REST API ----

app.get('/api/sessions', (req, res) => {
  res.json(Array.from(sessions.values()));
});

app.get('/api/sessions/:sessionId/summary', async (req, res) => {
  const { sessionId } = req.params;
  const session = sessions.get(sessionId);

  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  const jsonlPath = session.transcriptPath;
  if (!jsonlPath) {
    return res.status(404).json({ error: 'Transcript file not found' });
  }

  try {
    const summary = await extractSessionSummary(jsonlPath);
    summary.jsonlPath = jsonlPath;
    res.json(summary);
  } catch (error) {
    res.status(500).json({ error: `Summary extraction failed: ${error.message}` });
  }
});

// ---- Graceful shutdown ----

function shutdown() {
  console.log('\nShutting down...');
  if (pollTimer) clearInterval(pollTimer);
  wsHandler.shutdown();
  watcher.stop();
  server.close(() => {
    console.log('Server stopped.');
    process.exit(0);
  });
  setTimeout(() => process.exit(0), 3000);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

// ---- Start ----

async function main() {
  console.log('Session Monitor Dashboard');
  console.log(`Sessions dir: ${path.join(os.homedir(), '.claude', 'sessions')}`);

  // Initial full scan
  const initialSessions = await fullScan();
  console.log(`Found ${initialSessions.length} session(s)`);

  // Start watching for file changes
  try {
    await watcher.start();
  } catch (error) {
    console.error(`[session-monitor] File watcher failed to start: ${error.message}`);
  }

  // Start poll loop
  pollTimer = setInterval(pollLoop, POLL_INTERVAL_MS);

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.error(`Port ${PORT} is already in use. Try: SESSION_MONITOR_PORT=3849 node index.js`);
    } else {
      console.error('Server error:', err.message);
    }
    process.exit(1);
  });

  server.listen(PORT, () => {
    console.log(`Dashboard running at http://localhost:${PORT}`);
  });
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
