// @vitest-environment node
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, it } from 'vitest';
import { legacyElectronRuntimeLocation } from './legacy-electron-runtime';

const roots: string[] = [];
function fixture() {
  const parent = mkdtempSync(join(tmpdir(), 'speechnexa-legacy-runtime-'));
  roots.push(parent);
  return {
    current: join(parent, 'SpeechNexa'),
    legacy: join(parent, 'VoiceStudio'),
  };
}
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

it('does not claim an unrelated or absent legacy profile', () => {
  const { current } = fixture();
  expect(legacyElectronRuntimeLocation(current)).toBeNull();
  expect(legacyElectronRuntimeLocation(join(tmpdir(), 'DifferentApp'))).toBeNull();
});

it('finds an existing default runtime but never takes ownership', () => {
  const { current, legacy } = fixture();
  const runtime = join(legacy, 'runtime');
  mkdirSync(join(runtime, 'project'), { recursive: true });
  expect(legacyElectronRuntimeLocation(current)).toEqual({
    root: runtime,
    owned: false,
    scoped: false,
  });
});

it('finds a configured custom runtime and retains its scoped data policy', () => {
  const { current, legacy } = fixture();
  const runtime = join(legacy, 'external-runtime');
  mkdirSync(join(runtime, 'project'), { recursive: true });
  writeFileSync(
    join(legacy, 'runtime-location.json'),
    JSON.stringify({ root: runtime, owned: true, scoped: true }),
  );
  expect(legacyElectronRuntimeLocation(current)).toEqual({
    root: runtime,
    owned: false,
    scoped: true,
  });
});

it('ignores a missing custom runtime instead of redirecting setup into it', () => {
  const { current, legacy } = fixture();
  mkdirSync(legacy, { recursive: true });
  writeFileSync(
    join(legacy, 'runtime-location.json'),
    JSON.stringify({ root: join(legacy, 'missing'), owned: true, scoped: true }),
  );
  expect(legacyElectronRuntimeLocation(current)).toBeNull();
});
