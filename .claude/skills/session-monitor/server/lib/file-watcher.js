const EventEmitter = require('events');
const chokidar = require('chokidar');
const path = require('path');
const os = require('os');
const fs = require('fs').promises;

const DEFAULT_SESSIONS_DIR = path.join(os.homedir(), '.claude', 'sessions');

// Windows fires paired add+change events for a single write; debounce absorbs
// the duplicate within this window.
const DEBOUNCE_MS = 100;

/**
 * Watches ~/.claude/sessions/ for *.json file additions, changes, and
 * removals, then emits normalised events with the extracted PID.
 *
 * Events:
 *   'session-changed'  { pid: string, filePath: string }
 *   'session-removed'  { pid: string, filePath: string }
 *
 * @fires FileWatcher#session-changed
 * @fires FileWatcher#session-removed
 */
class FileWatcher extends EventEmitter {
  /**
   * @param {object} [options]
   * @param {string} [options.sessionsDir] - Directory to watch; defaults to ~/.claude/sessions/
   */
  constructor({ sessionsDir } = {}) {
    super();
    this._sessionsDir = sessionsDir ?? DEFAULT_SESSIONS_DIR;
    this._watcher = null;

    // pid (string) -> timer handle; used to debounce rapid double-events
    this._debounceTimers = new Map();
  }

  /**
   * Performs an initial scan of the sessions directory and emits
   * 'session-changed' for every existing .json file, then starts the
   * chokidar watcher for ongoing changes.
   *
   * @returns {Promise<void>}
   */
  async start() {
    await this._initialScan();
    this._startWatcher();
  }

  /**
   * Stops the chokidar watcher and clears all pending debounce timers.
   */
  stop() {
    if (this._watcher) {
      this._watcher.close();
      this._watcher = null;
    }

    for (const timer of this._debounceTimers.values()) {
      clearTimeout(timer);
    }
    this._debounceTimers.clear();
  }

  // ---------------------------------------------------------------------------
  // Private
  // ---------------------------------------------------------------------------

  /**
   * Reads the sessions directory and emits 'session-changed' for every
   * .json file found.  Missing directory is treated as an empty scan rather
   * than an error.
   *
   * @returns {Promise<void>}
   */
  async _initialScan() {
    let entries;
    try {
      entries = await fs.readdir(this._sessionsDir);
    } catch (error) {
      if (error.code === 'ENOENT') {
        // Directory doesn't exist yet; nothing to scan
        return;
      }
      console.warn(`[file-watcher] Could not read sessions dir ${this._sessionsDir}: ${error.message}`);
      return;
    }

    for (const filename of entries) {
      if (!filename.endsWith('.json')) continue;

      const filePath = path.join(this._sessionsDir, filename);
      const pid = this._extractPid(filename);

      this.emit('session-changed', { pid, filePath });
    }
  }

  /**
   * Creates and configures the chokidar watcher on the sessions directory.
   * Only *.json files are watched.
   */
  _startWatcher() {
    const globPattern = path.join(this._sessionsDir, '*.json')
      // chokidar expects forward slashes even on Windows
      .replace(/\\/g, '/');

    this._watcher = chokidar.watch(globPattern, {
      // Do not emit add events for files discovered during initial scan
      // (we already handled those in _initialScan)
      ignoreInitial: true,
      // Use polling as a fallback for network/container filesystems
      usePolling: false,
      // Avoid acting on partial writes
      awaitWriteFinish: {
        stabilityThreshold: 80,
        pollInterval: 20,
      },
    });

    this._watcher.on('add', (filePath) => {
      this._scheduleChanged(filePath);
    });

    this._watcher.on('change', (filePath) => {
      this._scheduleChanged(filePath);
    });

    this._watcher.on('unlink', (filePath) => {
      this._scheduleRemoved(filePath);
    });

    this._watcher.on('error', (error) => {
      console.warn(`[file-watcher] Watcher error: ${error.message}`);
    });
  }

  /**
   * Debounces a 'session-changed' emit for the given file path.
   * If an existing timer is pending for this PID it is replaced, so only
   * the final event in the burst is emitted.
   *
   * @param {string} filePath
   */
  _scheduleChanged(filePath) {
    const filename = path.basename(filePath);
    const pid = this._extractPid(filename);

    const existing = this._debounceTimers.get(pid);
    if (existing) {
      clearTimeout(existing);
    }

    const timer = setTimeout(() => {
      this._debounceTimers.delete(pid);
      this.emit('session-changed', { pid, filePath });
    }, DEBOUNCE_MS);

    this._debounceTimers.set(pid, timer);
  }

  /**
   * Debounces a 'session-removed' emit for the given file path.
   *
   * @param {string} filePath
   */
  _scheduleRemoved(filePath) {
    const filename = path.basename(filePath);
    const pid = this._extractPid(filename);

    const existing = this._debounceTimers.get(pid);
    if (existing) {
      clearTimeout(existing);
    }

    const timer = setTimeout(() => {
      this._debounceTimers.delete(pid);
      this.emit('session-removed', { pid, filePath });
    }, DEBOUNCE_MS);

    this._debounceTimers.set(pid, timer);
  }

  /**
   * Extracts the PID string from a session filename.
   * Example: '103680.json' → '103680'
   *
   * @param {string} filename
   * @returns {string}
   */
  _extractPid(filename) {
    return path.basename(filename, '.json');
  }
}

module.exports = { FileWatcher };
