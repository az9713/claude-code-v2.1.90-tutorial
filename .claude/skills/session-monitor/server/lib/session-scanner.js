const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const SESSIONS_DIR = path.join(os.homedir(), '.claude', 'sessions');

class SessionScanner {
  /**
   * Reads all session JSON files from ~/.claude/sessions/ and returns
   * a map of pid -> session record.
   *
   * Files that are missing, unreadable, or contain corrupt JSON are
   * skipped with a warning rather than throwing.
   *
   * @returns {Promise<Map<number, {pid: number, sessionId: string, cwd: string, startedAt: string}>>}
   */
  async scan() {
    const sessions = new Map();

    let entries;
    try {
      entries = await fs.readdir(SESSIONS_DIR);
    } catch (error) {
      if (error.code === 'ENOENT') {
        // Sessions directory does not exist yet; return empty map
        return sessions;
      }
      throw new Error(`Failed to read sessions directory: ${error.message}`);
    }

    const jsonFiles = entries.filter(name => name.endsWith('.json'));

    await Promise.all(jsonFiles.map(async (filename) => {
      const filepath = path.join(SESSIONS_DIR, filename);

      let raw;
      try {
        raw = await fs.readFile(filepath, 'utf8');
      } catch (error) {
        console.warn(`[session-scanner] Could not read file ${filepath}: ${error.message}`);
        return;
      }

      let record;
      try {
        record = JSON.parse(raw);
      } catch (error) {
        console.warn(`[session-scanner] Corrupt JSON in ${filepath}: ${error.message}`);
        return;
      }

      const pid = Number(record.pid);
      if (!pid || isNaN(pid)) {
        console.warn(`[session-scanner] Missing or invalid pid in ${filepath}`);
        return;
      }

      sessions.set(pid, {
        pid,
        sessionId: record.sessionId ?? null,
        cwd: record.cwd ?? null,
        startedAt: record.startedAt ?? null,
      });
    }));

    return sessions;
  }
}

module.exports = { SessionScanner };
