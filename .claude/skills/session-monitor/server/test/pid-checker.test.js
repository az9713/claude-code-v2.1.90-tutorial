const test = require('node:test');
const assert = require('node:assert/strict');

const { PidChecker } = require('../lib/pid-checker');

test('PidChecker falls back to signal probe when primary listing fails', async () => {
  const checker = new PidChecker();

  checker._getAlivePidsWindows = async () => {
    throw new Error('tasklist unavailable');
  };
  checker._getAlivePidsUnix = async () => {
    throw new Error('ps unavailable');
  };
  checker._getAlivePidsBySignalProbe = async () => new Set([123, 456]);

  const result = await checker.checkAll([123, 999]);

  assert.equal(result.get(123), true);
  assert.equal(result.get(999), false);
});
