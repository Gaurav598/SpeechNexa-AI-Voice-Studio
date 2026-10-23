/** VoiceStudio Cloud endpoints (vssaas desktop-app-guide §1). One block per environment. */
export type CloudEnvName = 'prod' | 'dev' | 'local';

export interface CloudEnvironment {
  name: CloudEnvName;
  issuer: string;
  accountApi: string;
  syncApi: string;
  signedInPage: string;
  clientId: string;
}

const CLIENT_ID = 'voicestudio-desktop-oss';

const ENVIRONMENTS: Record<CloudEnvName, Omit<CloudEnvironment, 'name' | 'clientId'>> = {
  prod: {
    issuer: 'https://voicestudio.sh/identity/realms/vssaas',
    accountApi: 'https://appapi.voicestudio.sh/v1/account',
    syncApi: 'https://appapi.voicestudio.sh/v1/sync',
    signedInPage: 'https://app.voicestudio.sh/app/desktop-signed-in',
  },
  dev: {
    issuer: 'https://dev-app.voicestudio.sh/identity/realms/vssaas',
    accountApi: 'https://dev-appapi.voicestudio.sh/v1/account',
    syncApi: 'https://dev-appapi.voicestudio.sh/v1/sync',
    signedInPage: 'https://dev-app.voicestudio.sh/app/desktop-signed-in',
  },
  local: {
    issuer: 'http://127.0.0.1:3000/identity/realms/vssaas',
    accountApi: 'http://127.0.0.1:8080/v1/account',
    syncApi: 'http://127.0.0.1:8090/v1/sync',
    signedInPage: 'http://127.0.0.1:3000/app/desktop-signed-in',
  },
};

export function resolveCloudEnvironment(opts: {
  packaged: boolean;
  requested?: string;
}): CloudEnvironment {
  const requested = opts.requested as CloudEnvName | undefined;
  const name: CloudEnvName = opts.packaged
    ? 'prod'
    : requested && Object.hasOwn(ENVIRONMENTS, requested)
      ? requested
      : 'dev';
  return { name, clientId: CLIENT_ID, ...ENVIRONMENTS[name] };
}

/** Sync origins join in S1; S0 talks only to the issuer and the account API. */
export function cloudOrigins(env: CloudEnvironment): Set<string> {
  return new Set([new URL(env.issuer).origin, new URL(env.accountApi).origin]);
}

/**
 * On in developer builds; packaged builds need VOICESTUDIO_CLOUD_ACCOUNTS=1 at build
 * time, so releases ship it dark until the vssaas production API launches.
 */
export function cloudAccountsAvailable(packaged: boolean): boolean {
  // Only an explicitly requested local integration test can use this code.
  // The old packaged flag and saved switches cannot revive upstream Cloud.
  return !packaged && process.env.SPEECHNEXA_ENABLE_LOCAL_ACCOUNT_TESTING === '1';
}
