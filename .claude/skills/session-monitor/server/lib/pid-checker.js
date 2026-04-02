const { execFile } = require('child_process');
const os = require('os');

const CACHE_TTL_MS = 5000;

class PidChecker {
  constructor() {
    this._cache = null;
    this._cacheTimestamp = 0;
  }

  /**
   * Checks whether a list of PIDs are alive on the current OS.
   * Results are cached for 5 seconds to avoid hammering the OS.
   * @param {number[]} pids - Array of PIDs to check
   * @returns {Promise<Map<number, boolean>>} Map of pid -> alive status
   */
  async checkAll(pids) {
    const alivePids = await this._getAlivePids();
    const result = new Map();

    for (const pid of pids) {
      result.set(pid, alivePids.has(Number(pid)));
    }

    return result;
  }

  /**
   * Returns a Set of alive PIDs, using cache if still valid.
   * @returns {Promise<Set<number>>}
   */
  async _getAlivePids() {
    const now = Date.now();

    if (this._cache !== null && now - this._cacheTimestamp < CACHE_TTL_MS) {
      return this._cache;
    }

    let alivePids;
    try {
      alivePids = os.platform() === 'win32'
        ? await this._getAlivePidsWindows()
        : await this._getAlivePidsUnix();
    } catch (error) {
      // Keep the dashboard running even if the host blocks process listing.
      console.warn(`[pid-checker] Falling back to per-pid checks: ${error.message}`);
      alivePids = await this._getAlivePidsBySignalProbe();
    }

    this._cache = alivePids;
    this._cacheTimestamp = now;

    return alivePids;
  }

  /**
   * Runs `tasklist /NH /FO CSV` on Windows and parses PIDs from CSV output.
   * CSV format per line: "Image Name","PID","Session Name","Session#","Mem Usage"
   * @returns {Promise<Set<number>>}
   */
  _getAlivePidsWindows() {
    return new Promise((resolve, reject) => {
      execFile('tasklist', ['/NH', '/FO', 'CSV'], (error, stdout, stderr) => {
        if (error) {
          return reject(new Error(`tasklist failed: ${error.message}`));
        }

        const alivePids = new Set();
        const lines = stdout.split(/\r?\n/);

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          // CSV fields are quoted; split on `","` after stripping outer quotes
          // Example line: "node.exe","1234","Console","1","50,000 K"
          const fields = trimmed.replace(/^"|"$/g, '').split('","');

          if (fields.length >= 2) {
            const pid = parseInt(fields[1], 10);
            if (!isNaN(pid)) {
              alivePids.add(pid);
            }
          }
        }

        resolve(alivePids);
      });
    });
  }

  /**
   * Runs `ps -eo pid` on Unix and parses PIDs from output.
   * @returns {Promise<Set<number>>}
   */
  _getAlivePidsUnix() {
    return new Promise((resolve, reject) => {
      execFile('ps', ['-eo', 'pid'], (error, stdout, stderr) => {
        if (error) {
          return reject(new Error(`ps failed: ${error.message}`));
        }

        const alivePids = new Set();
        const lines = stdout.split(/\n/);

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          const pid = parseInt(trimmed, 10);
          if (!isNaN(pid)) {
            alivePids.add(pid);
          }
        }

        resolve(alivePids);
      });
    });
  }

  /**
   * Fallback path when process enumeration commands are unavailable.
   * This scans an expected PID range and probes each PID with process.kill(pid, 0).
   * It is slower than tasklist/ps, so only used when primary methods fail.
   *
   * @returns {Promise<Set<number>>}
   */
  async _getAlivePidsBySignalProbe() {
    const maxPid = os.platform() === 'win32' ? 262144 : 131072;
    const alivePids = new Set();

    for (let pid = 1; pid <= maxPid; pid++) {
      try {
        process.kill(pid, 0);
        alivePids.add(pid);
      } catch (error) {
        // EPERM means process exists but is not accessible to this user.
        if (error && error.code === 'EPERM') {
          alivePids.add(pid);
        }
      }
    }

    return alivePids;
  }
}

module.exports = { PidChecker };
