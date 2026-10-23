import { existsSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, it, vi } from 'vitest';

const h = vi.hoisted(() => ({
  packaged: false,
  dir: '',
  safeThrows: false,
  keyring: false,
  setBackendOnlyEnv: vi.fn(),
  handlers: new Map<string, (...a: unknown[]) => unknown>(),
}));
vi.mock('electron', () => ({
  app: {
    get isPackaged() {
      return h.packaged;
    },
    getPath: () => h.dir,
  },
  safeStorage: {
    isEncryptionAvailable: () => {
      if (h.safeThrows) throw new Error('keychain locked');
      return h.keyring;
    },
    encryptString: (s: string) => Buffer.from(s),
    decryptString: (b: Buffer) => b.toString(),
  },
  shell: { openExternal: vi.fn() },
  ipcMain: {
    handle: vi.fn((channel: string, fn: (...a: unknown[]) => unknown) =>
      h.handlers.set(channel, fn),
    ),
    removeHandler: vi.fn(),
  },
  BrowserWindow: { getAllWindows: () => [] },
}));
vi.mock('../backend', () => ({ setBackendOnlyEnv: h.setBackendOnlyEnv }));
vi.mock('../ipc', () => ({ assertTrustedMainFrame: vi.fn() }));

import { startAccount } from './index';

const opts = {
  getMainWindow: () => null,
  isRemoteBackend: () => false,
  notifyBackend: vi.fn(async (_path: string) => {}),
};
afterEach(() => {
  h.packaged = false;
  h.safeThrows = false;
  h.keyring = false;
  h.setBackendOnlyEnv.mockClear();
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

it('does not start the inherited account bridge in a developer build', async () => {
  h.dir = mkdtempSync(join(tmpdir(), 'vs-account-'));
  const close = await startAccount(opts);
  expect(h.setBackendOnlyEnv).not.toHaveBeenCalled();
  expect(process.env.VOICESTUDIO_ACCOUNT_BRIDGE_TOKEN).toBeUndefined();
  close();
  expect(h.setBackendOnlyEnv).not.toHaveBeenCalled();
});

it('starts no bridge when the build does not offer accounts', async () => {
  h.packaged = true;
  h.dir = mkdtempSync(join(tmpdir(), 'vs-account-'));
  (await startAccount(opts))();
  expect(h.setBackendOnlyEnv).not.toHaveBeenCalled();
});

it('a startup failure degrades to no account features instead of blocking app start', async () => {
  h.safeThrows = true;
  h.dir = mkdtempSync(join(tmpdir(), 'vs-account-'));
  const close = await startAccount(opts);
  expect(typeof close).toBe('function');
  close();
});

/** A signed-in install: the keyring holds a refresh token from an earlier sign-in. */
function signedInDir(): string {
  const dir = mkdtempSync(join(tmpdir(), 'vs-account-'));
  writeFileSync(
    join(dir, 'account.json'),
    JSON.stringify({ v: 1, token: Buffer.from('rt').toString('base64') }),
  );
  // Account features already on (a token with them off is cleared at start-up).
  writeFileSync(
    join(dir, 'cloud-switches.json'),
    JSON.stringify({ accountEnabled: true, syncEnabled: false, prompted: true }),
  );
  h.keyring = true;
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => Promise.reject(new Error('offline'))),
  );
  return dir;
}

it('does not start inherited sync with saved switches enabled', async () => {
  h.dir = signedInDir();
  opts.notifyBackend.mockClear();
  const close = await startAccount(opts);
  const set = h.handlers.get('account:set-switches')!;
  await set({}, { accountEnabled: true, syncEnabled: true });
  await set({}, { syncEnabled: false });
  await set({}, { syncEnabled: true });
  await set({}, { accountEnabled: false });
  close();
  expect(opts.notifyBackend).not.toHaveBeenCalled();
});

it('never calls a remote backend about sync', async () => {
  h.dir = mkdtempSync(join(tmpdir(), 'vs-account-'));
  const notifyBackend = vi.fn(async () => {});
  const close = await startAccount({ ...opts, isRemoteBackend: () => true, notifyBackend });
  await h.handlers.get('account:set-switches')!({}, { accountEnabled: true, syncEnabled: true });
  close();
  expect(notifyBackend).not.toHaveBeenCalled();
});

it('signing out a retained session does not contact the inherited backend', async () => {
  h.dir = signedInDir();
  opts.notifyBackend.mockClear();
  const close = await startAccount(opts);
  await h.handlers.get('account:set-switches')!({}, { accountEnabled: true, syncEnabled: true });
  await h.handlers.get('account:sign-out')!({});
  close();
  expect(opts.notifyBackend).not.toHaveBeenCalled();
});

it('signing out deletes the cached profile photo', async () => {
  h.dir = signedInDir();
  const photo = join(h.dir, 'account-avatar.json');
  writeFileSync(
    photo,
    JSON.stringify({ v: 1, artifactId: 'Ar1', dataUrl: 'data:image/png;base64,AA' }),
  );
  const close = await startAccount(opts);
  await h.handlers.get('account:sign-out')!({});
  close();
  expect(existsSync(photo)).toBe(false);
});

it('a cached photo does not outlive account features being off', async () => {
  h.dir = mkdtempSync(join(tmpdir(), 'vs-account-'));
  const photo = join(h.dir, 'account-avatar.json');
  writeFileSync(
    photo,
    JSON.stringify({ v: 1, artifactId: 'Ar1', dataUrl: 'data:image/png;base64,AA' }),
  );
  (await startAccount(opts))();
  expect(existsSync(photo)).toBe(false);
});
