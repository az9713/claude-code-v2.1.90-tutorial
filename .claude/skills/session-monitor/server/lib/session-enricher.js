const fs = require('fs').promises;
const fssync = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

const DEFAULT_PROJECTS_DIR = path.join(os.homedir(), '.claude', 'projects');
const DEFAULT_TEAMS_DIR = path.join(os.homedir(), '.claude', 'teams');

/**
 * Encodes a filesystem path into the dot-less, slash-free format that Claude
 * uses when naming project index directories.
 *
 * Examples:
 *   C:\Users\simon\Downloads\foo  →  C--Users-simon-Downloads-foo
 *   /home/simon/projects/bar      →  -home-simon-projects-bar
 *
 * Rules:
 *   - Replace `:` with `-`
 *   - Replace `\` and `/` with `-`
 *
 * @param {string} cwdPath - Absolute path to encode
 * @returns {string}
 */
function encodePath(cwdPath) {
  return cwdPath
    .replace(/:/g, '-')
    .replace(/[/\\]/g, '-');
}

class SessionEnricher {
  /**
   * @param {object} [options]
   * @param {string} [options.projectsDir] - Path to ~/.claude/projects/
   * @param {string} [options.teamsDir]    - Path to ~/.claude/teams/
   */
  constructor({ projectsDir, teamsDir } = {}) {
    this._projectsDir = projectsDir ?? DEFAULT_PROJECTS_DIR;
    this._teamsDir = teamsDir ?? DEFAULT_TEAMS_DIR;

    // Team configs are loaded lazily and refreshed only on refreshTeams()
    this._teamConfigs = null;
    this._sessionProjectDirCache = new Map();
  }

  /**
   * Forces a reload of all team config files on the next enrich() call.
   * Call this whenever the teams directory may have changed.
   */
  refreshTeams() {
    this._teamConfigs = null;
  }

  /**
   * Enriches a raw session record with project index data, file stats, and
   * team membership information.
   *
   * @param {{ pid: number, sessionId: string, cwd: string, startedAt: string }} session
   * @param {boolean} isAlive - Whether the process for this session is still running
   * @returns {Promise<object>} Enriched session object
   */
  async enrich(session, isAlive) {
    const { sessionId, cwd } = session;

    // 1. Project name is the last path component of cwd
    const projectName = cwd ? path.basename(cwd) : null;

    const encodedPath = cwd ? encodePath(cwd) : null;
    let projectDir = encodedPath
      ? path.join(this._projectsDir, encodedPath)
      : null;

    if (sessionId) {
      const transcriptInDerivedDir = projectDir
        ? await this._fileExists(path.join(projectDir, `${sessionId}.jsonl`))
        : false;

      if (!transcriptInDerivedDir) {
        const discoveredProjectDir = await this._findProjectDirBySessionId(sessionId);
        if (discoveredProjectDir) {
          projectDir = discoveredProjectDir;
        }
      }
    }

    // 2 & 3. Read the sessions index to find this session's metadata
    let firstPrompt = null;
    let messageCount = null;
    let gitBranch = null;
    let modified = null;

    let transcriptPath = null;

    if (projectDir && sessionId) {
      const indexPath = path.join(projectDir, 'sessions-index.json');
      const indexEntry = await this._readIndexEntry(indexPath, sessionId);
      if (indexEntry) {
        firstPrompt = indexEntry.firstPrompt ?? null;
        messageCount = indexEntry.messageCount ?? null;
        gitBranch = indexEntry.gitBranch ?? null;
        modified = indexEntry.modified ?? null;
      }
      transcriptPath = path.join(projectDir, `${sessionId}.jsonl`);
    }

    // 4. Get last activity from the transcript JSONL file's mtime
    let lastActivity = null;

    if (transcriptPath) {
      lastActivity = await this._getFileMtime(transcriptPath);

      // Fallback metadata when sessions-index.json is absent or stale.
      if (firstPrompt === null || messageCount === null || modified === null) {
        const summary = await this._summarizeTranscript(transcriptPath);
        if (firstPrompt === null) firstPrompt = summary.firstPrompt;
        if (messageCount === null) messageCount = summary.messageCount;
        if (modified === null) modified = summary.modified;
      }
    }

    // 5. Check whether a subagents directory exists for this session
    let hasSubagents = false;

    if (projectDir && sessionId) {
      const subagentsDir = path.join(projectDir, sessionId, 'subagents');
      hasSubagents = await this._directoryExists(subagentsDir);
    }

    // 6. Determine session type via team configs
    const { type: sessionType, teamName } = await this._detectSessionType(session);

    return {
      ...session,
      projectName,
      firstPrompt,
      messageCount,
      gitBranch,
      modified,
      lastActivity,
      hasSubagents,
      sessionType,
      teamName,
      isAlive,
      transcriptPath: transcriptPath ?? null,
    };
  }

  // ---------------------------------------------------------------------------
  // Private helpers
  // ---------------------------------------------------------------------------

  /**
   * Reads a sessions-index.json file and returns the entry whose sessionId
   * matches the one provided, or null if not found or the file is missing.
   *
   * The index is expected to be an array of session entry objects or a plain
   * object keyed by sessionId.  Both shapes are handled.
   *
   * @param {string} indexPath
   * @param {string} sessionId
   * @returns {Promise<object|null>}
   */
  async _readIndexEntry(indexPath, sessionId) {
    let raw;
    try {
      raw = await fs.readFile(indexPath, 'utf8');
    } catch (error) {
      if (error.code !== 'ENOENT') {
        console.warn(`[session-enricher] Could not read index ${indexPath}: ${error.message}`);
      }
      return null;
    }

    let index;
    try {
      index = JSON.parse(raw);
    } catch (error) {
      console.warn(`[session-enricher] Corrupt JSON in ${indexPath}: ${error.message}`);
      return null;
    }

    // The index file has shape { version, entries: [...] }
    const entries = Array.isArray(index) ? index
      : (index && Array.isArray(index.entries)) ? index.entries
      : [];

    return entries.find(entry => entry.sessionId === sessionId) ?? null;
  }

  /**
   * Returns the mtime of a file as an ISO string, or null if the file does
   * not exist or cannot be stat'd.
   *
   * @param {string} filePath
   * @returns {Promise<string|null>}
   */
  async _getFileMtime(filePath) {
    try {
      const stat = await fs.stat(filePath);
      return stat.mtime.toISOString();
    } catch (error) {
      if (error.code !== 'ENOENT') {
        console.warn(`[session-enricher] Could not stat ${filePath}: ${error.message}`);
      }
      return null;
    }
  }

  /**
   * Reads a transcript JSONL file and derives basic metadata from it.
   *
   * @param {string} transcriptPath
   * @returns {Promise<{ firstPrompt: string|null, messageCount: number|null, modified: string|null }>}
   */
  async _summarizeTranscript(transcriptPath) {
    const summary = {
      firstPrompt: null,
      messageCount: 0,
      modified: null,
    };

    // Use mtime as a modified fallback.
    summary.modified = await this._getFileMtime(transcriptPath);

    try {
      const stream = fssync.createReadStream(transcriptPath, { encoding: 'utf8' });
      const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });

      for await (const line of rl) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        let parsed;
        try {
          parsed = JSON.parse(trimmed);
        } catch {
          continue;
        }

        summary.messageCount += 1;

        if (summary.firstPrompt === null) {
          const text = this._extractPromptCandidate(parsed);
          if (text) summary.firstPrompt = text;
        }
      }
    } catch (error) {
      if (error.code !== 'ENOENT') {
        console.warn(`[session-enricher] Could not read transcript ${transcriptPath}: ${error.message}`);
      }
      return { firstPrompt: null, messageCount: null, modified: summary.modified };
    }

    if (summary.messageCount === 0) {
      return { firstPrompt: null, messageCount: null, modified: summary.modified };
    }

    return summary;
  }

  /**
   * Best-effort extraction of user prompt text from variable transcript schemas.
   *
   * @param {object} entry
   * @returns {string|null}
   */
  _extractPromptCandidate(entry) {
    if (!entry || typeof entry !== 'object') return null;

    const role = entry.role || entry.author || entry.sender || null;
    if (role && !String(role).toLowerCase().includes('user')) {
      return null;
    }

    if (typeof entry.text === 'string' && entry.text.trim()) return entry.text.trim();
    if (typeof entry.prompt === 'string' && entry.prompt.trim()) return entry.prompt.trim();

    const content = entry.content;
    if (typeof content === 'string' && content.trim()) return content.trim();

    if (Array.isArray(content)) {
      for (const part of content) {
        if (!part || typeof part !== 'object') continue;
        if (typeof part.text === 'string' && part.text.trim()) return part.text.trim();
        if (typeof part.content === 'string' && part.content.trim()) return part.content.trim();
      }
    }

    if (entry.message && typeof entry.message === 'object') {
      return this._extractPromptCandidate(entry.message);
    }

    return null;
  }

  /**
   * Returns true if the given path exists and is a directory.
   *
   * @param {string} dirPath
   * @returns {Promise<boolean>}
   */
  async _directoryExists(dirPath) {
    try {
      const stat = await fs.stat(dirPath);
      return stat.isDirectory();
    } catch {
      return false;
    }
  }

  /**
   * Returns true if the given file exists.
   *
   * @param {string} filePath
   * @returns {Promise<boolean>}
   */
  async _fileExists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Finds the project directory that contains <sessionId>.jsonl.
   * Uses a cache for repeated lookups across poll cycles.
   *
   * @param {string} sessionId
   * @returns {Promise<string|null>}
   */
  async _findProjectDirBySessionId(sessionId) {
    const cached = this._sessionProjectDirCache.get(sessionId);
    if (cached) {
      const exists = await this._fileExists(path.join(cached, `${sessionId}.jsonl`));
      if (exists) return cached;
      this._sessionProjectDirCache.delete(sessionId);
    }

    let entries;
    try {
      entries = await fs.readdir(this._projectsDir, { withFileTypes: true });
    } catch (error) {
      if (error.code !== 'ENOENT') {
        console.warn(`[session-enricher] Could not read projects dir ${this._projectsDir}: ${error.message}`);
      }
      return null;
    }

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const projectDir = path.join(this._projectsDir, entry.name);
      const transcriptPath = path.join(projectDir, `${sessionId}.jsonl`);
      if (await this._fileExists(transcriptPath)) {
        this._sessionProjectDirCache.set(sessionId, projectDir);
        return projectDir;
      }
    }

    return null;
  }

  /**
   * Loads team configs from disk if not already cached, then searches each
   * config for a member entry whose cwd or sessionId matches the session.
   * Returns the team name string when a match is found, or 'solo' otherwise.
   *
   * Team configs are cached after the first load and only refreshed when
   * refreshTeams() is called.
   *
   * @param {{ cwd: string, sessionId: string }} session
   * @returns {Promise<string>}
   */
  async _detectSessionType(session) {
    if (this._teamConfigs === null) {
      this._teamConfigs = await this._loadTeamConfigs();
    }

    for (const { teamName, config } of this._teamConfigs) {
      const members = config.members;
      if (!Array.isArray(members)) continue;

      const matchedMember = members.find(member =>
        (session.cwd && member.cwd === session.cwd) ||
        (session.sessionId && member.sessionId === session.sessionId)
      );

      if (matchedMember) {
        const isLead = matchedMember.agentType === 'team-lead' ||
          config.leadSessionId === session.sessionId;
        return {
          type: isLead ? 'team-lead' : 'team-member',
          teamName
        };
      }
    }

    return { type: 'solo', teamName: null };
  }

  /**
   * Scans team config files and returns all successfully parsed
   * configs as an array of { teamName, config } objects.
   *
   * @returns {Promise<Array<{ teamName: string, config: object }>>}
   */
  async _loadTeamConfigs() {
    let entries;
    try {
      entries = await fs.readdir(this._teamsDir);
    } catch (error) {
      if (error.code !== 'ENOENT') {
        console.warn(`[session-enricher] Could not read teams dir ${this._teamsDir}: ${error.message}`);
      }
      return [];
    }

    const configs = [];

    await Promise.all(entries.map(async (teamName) => {
      const configPath = path.join(this._teamsDir, teamName, 'config.json');

      let raw;
      try {
        raw = await fs.readFile(configPath, 'utf8');
      } catch (error) {
        if (error.code !== 'ENOENT') {
          console.warn(`[session-enricher] Could not read team config ${configPath}: ${error.message}`);
        }
        return;
      }

      let config;
      try {
        config = JSON.parse(raw);
      } catch (error) {
        console.warn(`[session-enricher] Corrupt JSON in ${configPath}: ${error.message}`);
        return;
      }

      configs.push({ teamName, config });
    }));

    return configs;
  }
}

module.exports = { SessionEnricher };
