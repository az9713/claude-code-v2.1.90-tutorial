const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');

const { SessionEnricher } = require('../lib/session-enricher');

function encodePath(cwdPath) {
  return cwdPath.replace(/:/g, '-').replace(/[/\\]/g, '-');
}

test('SessionEnricher derives metadata from transcript when sessions-index is missing', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'session-monitor-test-'));
  const projectsDir = path.join(root, 'projects');
  const teamsDir = path.join(root, 'teams');
  const cwd = path.join(root, 'workspace', 'repo');
  const sessionId = 'sess-1';
  const projectDir = path.join(projectsDir, encodePath(cwd));

  try {
    await fs.mkdir(projectDir, { recursive: true });
    await fs.mkdir(teamsDir, { recursive: true });

    const transcriptPath = path.join(projectDir, `${sessionId}.jsonl`);
    await fs.writeFile(
      transcriptPath,
      `${JSON.stringify({ role: 'user', content: 'first user prompt' })}\n${JSON.stringify({ role: 'assistant', content: 'reply' })}\n`,
      'utf8'
    );

    const enricher = new SessionEnricher({ projectsDir, teamsDir });
    const enriched = await enricher.enrich(
      {
        pid: 1,
        sessionId,
        cwd,
        startedAt: new Date().toISOString(),
      },
      true
    );

    assert.equal(enriched.firstPrompt, 'first user prompt');
    assert.equal(enriched.messageCount, 2);
    assert.equal(enriched.projectName, path.basename(cwd));
    assert.equal(enriched.sessionType, 'solo');
    assert.equal(enriched.isAlive, true);
    assert.ok(enriched.lastActivity);
    assert.ok(enriched.modified);
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test('SessionEnricher prefers sessions-index metadata when available', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'session-monitor-test-'));
  const projectsDir = path.join(root, 'projects');
  const teamsDir = path.join(root, 'teams');
  const cwd = path.join(root, 'workspace', 'repo');
  const sessionId = 'sess-2';
  const projectDir = path.join(projectsDir, encodePath(cwd));

  try {
    await fs.mkdir(projectDir, { recursive: true });
    await fs.mkdir(teamsDir, { recursive: true });

    const indexPath = path.join(projectDir, 'sessions-index.json');
    await fs.writeFile(
      indexPath,
      JSON.stringify({
        version: 1,
        entries: [{
          sessionId,
          firstPrompt: 'from index',
          messageCount: 42,
          gitBranch: 'feature/harden',
          modified: '2026-01-01T00:00:00.000Z',
        }]
      }),
      'utf8'
    );

    const transcriptPath = path.join(projectDir, `${sessionId}.jsonl`);
    await fs.writeFile(
      transcriptPath,
      `${JSON.stringify({ role: 'user', content: 'from transcript' })}\n`,
      'utf8'
    );

    const enricher = new SessionEnricher({ projectsDir, teamsDir });
    const enriched = await enricher.enrich(
      {
        pid: 2,
        sessionId,
        cwd,
        startedAt: new Date().toISOString(),
      },
      false
    );

    assert.equal(enriched.firstPrompt, 'from index');
    assert.equal(enriched.messageCount, 42);
    assert.equal(enriched.gitBranch, 'feature/harden');
    assert.equal(enriched.modified, '2026-01-01T00:00:00.000Z');
    assert.equal(enriched.isAlive, false);
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});
