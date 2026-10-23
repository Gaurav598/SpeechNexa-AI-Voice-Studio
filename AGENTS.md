# SpeechNexa agent operating contract

SpeechNexa is an AGPL-3.0-only derivative of VoiceStudio. Preserve original copyright and license notices, source attribution, and compatible user data. SpeechNexa's Git history is the owner's personal project history; do not import upstream commits or assign them to the owner. Read `CLAUDE.md` for the full project guidance; where these files differ, it wins. The repository's active destination is `Gaurav598/SpeechNexa-AI-Voice-Studio`. `debpalash/VoiceStudio` is a read-only provenance source, never a push target.

## Product boundaries

- Electron (`electron/`) is the only desktop and web UI. Do not revive removed Tauri build, runtime, release or CI paths. Existing Tauri installations belong to the upstream migration guide and immutable updater feeds.
- Native iOS and Android sources live under `mobile/`. Both follow `mobile/contract/SPEC.md`; a mobile feature ships on both or neither. Their first-release SpeechNexa behavior is not yet verified. Desktop/web UI work stays in Electron.
- Python `omnivoice` imports and established `OMNIVOICE_*` settings remain compatibility names where changing them would break engines or user data. New project-owned identifiers should use `SpeechNexa`, `speechnexa` and `SPEECHNEXA_*`.

## Engineering rules

- Keep local inference usable offline after explicit model installation. No implicit model or optional checkpoint downloads. Preserve model license gates and the `mark_synthetic` audio entry point.
- Fix the root cause with a focused fail-before/pass-after regression test. Run targeted checks during development and full relevant gates before landing. Use `HF_HUB_OFFLINE=1` and an empty `HF_HUB_CACHE` for deterministic CI tests.
- Default user-visible behavior must be consistent across macOS, Windows and Linux. Hardware optimization may differ by host. Report untested platforms honestly.
- All new user-facing Electron strings need real translations in all 21 `electron/src/renderer/src/i18n/locales/*.json` catalogs. Use the shared `SearchableSelect` for new select controls and `VoiceSelector` for voice choices.
- Root `package.json` is the version source; do not bump without owner direction. Regenerate root `bun.lock` after JavaScript dependency changes. Update docs in the same change.
- Never add downloaded weights, generated audio, recordings, caches, databases, secrets or personal files to Git. Retain required AGPL, Apache, MIT and model notices.
- Commits and PR text carry only the configured human submitter identity. Do not add agent credit or unrelated names/emails.

## Publication

Do not enable inherited release, store, CLA, sponsor, cloud or analytics automation by default. Review files, licenses, secret scans, tests and the destination before pushing. The owner authorized a one-time `main` history correction on 2026-10-24 to remove mistakenly imported upstream commits. After that correction, never force-push without a new explicit owner instruction; never publish to upstream. Merge only after review and passing current checks; verify `main` CI after a merge. Source status and known limitations are in `docs/IMPLEMENTATION_STATUS.md`.

Project skills pinned by `skills-lock.json` are installed under `.agents/skills/` for FastAPI and Vite. Repository rules and current tests override generic skill advice.
