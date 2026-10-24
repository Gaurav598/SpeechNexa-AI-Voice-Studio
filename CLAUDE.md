# SpeechNexa engineering guidance

SpeechNexa is an AGPL-3.0-only derivative of [VoiceStudio](https://github.com/debpalash/VoiceStudio). The imported source remains attributed to its authors. SpeechNexa's original engineering is recorded by its own changes; do not imply ownership of imported code, voices, model weights or generated sample media. See `UPSTREAM.md`, `THIRD_PARTY_NOTICES.md` and `docs/MODEL_LICENSING.md`.

## Architecture and product

- `electron/` owns the desktop and web UI. Tauri is removed. Never restore Tauri build or publication paths. Keep final upstream Tauri updater feeds immutable and direct legacy installation reports to the migration guide.
- `backend/main.py` owns the local FastAPI service. `backend/api/routers/generation.py` is the active speech path, with adapters, worker admission and SQLite state in `backend/services/` and `backend/core/`. Extend this path rather than creating a disconnected scheduler.
- `mobile/ios/` and `mobile/android/` are native source projects with the shared `mobile/contract/SPEC.md`. Their first-release SpeechNexa functionality and platform parity require separate verification.
- Preserve existing `omnivoice` Python imports and `OMNIVOICE_*` compatibility settings when they protect model identifiers or existing user data. Use SpeechNexa names for new project-owned state and UI.

## Local-first and safety

- The default service binds to loopback. No required cloud API, analytics, account or network call for installed local inference. Downloads require an explicit installation action. Optional AudioSeal watermarking may use a cached checkpoint but must not fetch one during synthesis.
- Keep synthetic audio on the `mark_synthetic` path. Validate decoded output before recording a job as done. Use bounded queues, cancellation cleanup and honest restart state; do not claim work can resume if only its metadata persists.
- Every model or third-party component keeps its own license and attribution. Model-card labels do not prove all component or redistribution rights. Never commit weights, recordings, generated outputs, caches or secrets. Imported sample media rights remain unresolved.
- Do not automatically re-enable inherited publishing, app stores, Docker releases, cloud, updater or owner-specific workflows. SpeechNexa CI should run with minimal permissions and without model downloads.

## Change quality

- Find the failure class, add a focused fail-before/pass-after regression test, then make the smallest complete fix. Run targeted tests while iterating and relevant full checks before landing. CI should use `HF_HUB_OFFLINE=1` with an empty model cache.
- User-visible default behavior must match across macOS, Windows and Linux; accelerator performance may differ. State which platforms and engines were actually tested.
- Localize new Electron text across all 21 active renderer catalogs. New select controls use `SearchableSelect`, voice controls use `VoiceSelector`, and scrolling contexts use the menu portal where needed.
- Root `package.json` is the version source. Do not bump without the owner's request. Keep `pyproject.toml` and backend fallback version in lockstep if a bump is authorized. Regenerate root `bun.lock` when JS dependencies change, and check frozen install.
- Update user instructions and limitations with each behavior change. Preserve AGPL, Apache and MIT notices. Commit and PR attribution uses only the configured human submitter identity, without agent credit.

## Git and release

`origin` is the existing `Gaurav598/SpeechNexa-AI-Voice-Studio` repository. The obsolete local `upstream` remote was removed; its read-only provenance link remains in `UPSTREAM.md`. Keep the destination's commit history limited to the owner's SpeechNexa work; credit inherited source in its original copyright/license notices and `UPSTREAM.md`, not by importing upstream Git commits. The owner authorized a one-time correction of the mistakenly imported history on 2026-10-24. After that correction, do not force-push without new explicit owner direction. Do not create a new repository or publish releases automatically. Review the destination and the diff before pushing. For any later PR merge, inspect reviews, fix findings on its branch, require current CI and verify post-merge `main`.

Use `docs/IMPLEMENTATION_STATUS.md` for exact verification and continuation state. Older upstream release, account and owner instructions remain available in the upstream repository or `docs/archive/`; they do not authorize SpeechNexa deployment.
