# SpeechNexa implementation status

Updated: 2026-10-24 (Asia/Kolkata). This is a source implementation checkpoint, not a binary release announcement.

## Repository and provenance

- The source arrived as a downloaded VoiceStudio archive without `.git`. Five pre-edit root files matched upstream Git blobs from `28bf2c7a83b8a64836297340c52a45d716684aed`. A full recursive archive match is unproven.
- The owner's existing `Gaurav598/SpeechNexa-AI-Voice-Studio` repository uses a new owner-authored root source snapshot. On 2026-10-24 the owner explicitly requested removal of mistakenly imported VoiceStudio Git history from `main`; upstream authorship remains credited through inherited source notices, [UPSTREAM.md](../UPSTREAM.md), and [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). `upstream` is fetch-only with a disabled push URL. Earlier SpeechNexa commits based on the upstream Git graph are superseded, not part of the corrected public history.
- The prior main branch and its CI runs are not evidence for the corrected history. Verify the current remote `main` SHA, contributor graph, source scan and Actions runs after the owner-authored root is published. This is source publication, not a binary release.
- Imported sample media under `backend/assets/samples/` has unresolved redistribution rights (`NOASSERTION` in its own manifest). See `UPSTREAM.md` and `THIRD_PARTY_NOTICES.md`.

## Verified implementation

- Locked Python 3.11 dependencies installed in ignored `.venv/`; Electron dependencies installed in ignored `node_modules/`. Root frozen Bun install passed earlier in this migration.
- FastAPI starts on loopback. Real `KittenML/kitten-tts-mini-0.8` inference through `POST /generate` produced a 24 kHz mono WAV. The final offline smoke on this Apple M4 Mac (16 GB RAM) produced 3.939 seconds of non-silent audio (RMS 0.1788) in 4.218 seconds of API time. `GET /audio/fe500b6a.wav` matched the response and stored WAV byte for byte. SQLite history and a completed `speech_generate` job were verified after backend shutdown. Engine is ONNX CPU; direct PyTorch MPS availability was false.
- Optional AudioSeal no longer downloads its checkpoint during offline generation. The smoke used an empty isolated AudioSeal cache and detected no cache writes or download logs. Explicit opt-in prefetch remains possible. The regression test failed before and passed after the runtime gate.
- Active `/generate` creates a durable job ID exposed in `X-Job-Id` for classic and streaming responses. Guarded transitions validate the WAV before completion and record failures/cancellation. The existing GPU pool now has FIFO memory reservations when dedicated free VRAM is measurable. CPU/MPS/unknown VRAM retains the worker-count bound; no preemption or guaranteed GPU capacity is claimed.
- Electron desktop/web builds, locale/type checks and full renderer/shared unit suites passed on this Mac. Active product metadata, packaged icons and the macOS development bundle use SpeechNexa; legacy runtime compatibility remains.
- Imported release/store/CLA/funding automation was archived; active CI has read-only permissions and SpeechNexa migration gates. Local provenance and model-inventory checks passed in the specialist pass. Model weights are not checked in.

## Current verification and limits

- The full Python suite excluding `tests/smoke/` passed: 9,844 passed, 84 skipped, 2 expected failures and 7 unexpected passes. The boot smoke passed separately (4 tests), and `backend/tests/` passed (515 tests). The remaining macOS hotkey smoke requires Cargo, which is absent on this host. Electron under bundled Node 24: renderer suite 1,683 passed and 2 skipped; shared suite 2,902 passed. The macOS desktop UI suite passed all 16 tests after correcting title/route expectations and an unclean-exit harness race. Typecheck, locale contract, Electron and web builds, packaging contract, and 107 root frontend tests passed. The earlier focused Python and UI results overlap these broader gates.
- The migration and follow-up source changes separately passed `gitleaks dir` with the repository configuration (zero findings). A whole-workspace scan included ignored generated build files and is not a source verdict. The corrected root snapshot needs its own complete tracked-source scan and new GitHub Actions results. `git diff --check` and the SpeechNexa migration/model-license validators passed locally.
- macOS is the only runtime host used for real speech. Windows and Linux execution, native installers, native mobile apps, other model adapters and all imported workflows are unverified. A full first-release claim requires those gates and GitHub CI.
- Jobs begin after model prewarming; a model-load wait can occur before a job ID is available. Persistence records state but does not replay a crashed generation. A history retention action can remove an output while its job metadata remains.
- Analytics/account/cloud/update paths are disabled or gated for the migration. Some inherited VoiceStudio wording and commercial-only UI pages are being audited; do not claim all screens fully migrated.

## Continuation commands

```bash
cd /Users/gaurav/Downloads/SpeechNexa
git status --short
git diff --check
HF_HUB_OFFLINE=1 HF_HUB_CACHE=/private/tmp/speechnexa-empty-hf .venv/bin/python -m pytest -q tests/test_watermark_offline_checkpoint.py tests/test_generate_streaming.py tests/test_job_store.py tests/test_gpu_memory_reservations.py
.venv/bin/python scripts/smoke_real_tts.py --hf-home /private/tmp/speechnexa-hf --output /private/tmp/speechnexa-smoke.wav
python3 scripts/check_migration_safety.py
bun run --cwd electron typecheck
bun run --cwd electron build
```

Use an isolated `OMNIVOICE_DATA_DIR` for API tests. Do not delete user-owned caches or databases. Do not push to `upstream`.
