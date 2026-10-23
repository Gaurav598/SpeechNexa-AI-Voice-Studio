# Development

Use Python 3.11, uv and the Bun version pinned in `package.json`. From the repository root:

```bash
uv sync --locked --python 3.11
bun install --frozen-lockfile
OMNIVOICE_TTS_BACKEND=kittentts HF_HUB_OFFLINE=1 uv run python backend/main.py
```

In a second terminal, run `bun run dev:desktop` for Electron or `bun run --cwd electron dev:web` for the browser renderer. The backend binds to loopback by default. Install the KittenTTS model explicitly using the command in [README](../README.md) before running offline generation. Never add downloaded weights, recordings or generated outputs to Git.

For code changes, run focused tests first, then the gates in [testing](TESTING.md). User-facing Electron strings belong in all 21 renderer locale catalogs. Regenerate `bun.lock` when JavaScript dependencies change. Keep application source AGPL-3.0-only and preserve imported attribution. See [UPSTREAM](../UPSTREAM.md).

Publishing workflows inherited from VoiceStudio are archived. Do not enable releases, stores, account services, analytics or update checks merely to make local development work.
