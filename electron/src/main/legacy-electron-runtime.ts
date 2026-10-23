import { readFileSync, statSync } from 'node:fs';
import { basename, dirname, isAbsolute, join, resolve } from 'node:path';

export interface LegacyElectronRuntimeLocation {
  root: string;
  owned: false;
  scoped: boolean;
}

function hasProject(root: string): boolean {
  try {
    return statSync(join(root, 'project')).isDirectory();
  } catch {
    return false;
  }
}

/**
 * Find an installed VoiceStudio runtime without moving it or treating its files
 * as SpeechNexa-owned. Fresh SpeechNexa installs never select this path.
 */
export function legacyElectronRuntimeLocation(
  userData: string,
): LegacyElectronRuntimeLocation | null {
  if (basename(userData).toLocaleLowerCase('en-US') !== 'speechnexa') return null;
  const legacyData = join(dirname(userData), 'VoiceStudio');
  try {
    const config = JSON.parse(readFileSync(join(legacyData, 'runtime-location.json'), 'utf8')) as {
      root?: unknown;
      scoped?: unknown;
    };
    if (typeof config.root === 'string' && isAbsolute(config.root)) {
      const root = resolve(config.root);
      if (hasProject(root)) return { root, owned: false, scoped: config.scoped === true };
    }
  } catch {
    // Older default installs may not have a runtime-location file.
  }
  const defaultRoot = join(legacyData, 'runtime');
  return hasProject(defaultRoot) ? { root: defaultRoot, owned: false, scoped: false } : null;
}
