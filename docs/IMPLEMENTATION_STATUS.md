# SpeechNexa implementation status

Updated: 2026-10-24 (Asia/Kolkata). This is a source implementation checkpoint, not a binary release announcement.

## Repository and provenance

- The source arrived as a downloaded VoiceStudio archive without `.git`. Five pre-edit root files matched upstream Git blobs from `28bf2c7a83b8a64836297340c52a45d716684aed`. A full recursive archive match is unproven.
- The owner's `Gaurav598/SpeechNexa-AI-Voice-Studio` repository uses an owner-authored root source snapshot. The prepublication `main` HEAD for this checkpoint is `a0fef4460112cc67aafba303a242bd8d6fbad10c`; the final published commit is the Git commit containing this document. On 2026-10-24 the owner explicitly requested removal of mistakenly imported upstream Git history from `main`; upstream authorship remains credited through inherited source notices, [UPSTREAM.md](../UPSTREAM.md), and [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). `upstream` is fetch-only with a disabled push URL. Earlier SpeechNexa commits based on the upstream Git graph are superseded, not part of the corrected history.
- GitHub's API reported only `main`, two commits authored by Gaurav598, and one contributor (Gaurav598) after the history correction and inherited Dependabot configuration archive. The former 102-contributor sidebar count came from the superseded Git graph and may take time to refresh in GitHub's UI. This is source publication, not a binary release.
- Imported sample media under `backend/assets/samples/` has unresolved redistribution rights (`NOASSERTION` in its own manifest). See `UPSTREAM.md` and `THIRD_PARTY_NOTICES.md`.

## Verified implementation

- Locked Python 3.11 dependencies installed in ignored `.venv/`; Electron dependencies installed in ignored `node_modules/`. Root frozen Bun install passed earlier in this migration.
- FastAPI starts on loopback. Real `KittenML/kitten-tts-mini-0.8` inference through `POST /generate` produced a 24 kHz mono WAV. The final offline smoke on this Apple M4 Mac (16 GB RAM) produced 3.939 seconds of non-silent audio (RMS 0.1788) in 4.218 seconds of API time. `GET /audio/fe500b6a.wav` matched the response and stored WAV byte for byte. SQLite history and a completed `speech_generate` job were verified after backend shutdown. Engine is ONNX CPU; direct PyTorch MPS availability was false.
- Optional AudioSeal no longer downloads its checkpoint during offline generation. The smoke used an empty isolated AudioSeal cache and detected no cache writes or download logs. Explicit opt-in prefetch remains possible. The regression test failed before and passed after the runtime gate.
- Active `/generate` creates a durable job ID exposed in `X-Job-Id` for classic and streaming responses. Guarded transitions validate the WAV before completion and record failures/cancellation. The existing GPU pool now has FIFO memory reservations when dedicated free VRAM is measurable. CPU/MPS/unknown VRAM retains the worker-count bound; no preemption or guaranteed GPU capacity is claimed.
- Electron desktop/web builds, locale/type checks and full renderer/shared unit suites passed on this Mac under Node 24 and Bun 1.4.2. Active product metadata, packaged icons, store listing and the macOS development bundle use SpeechNexa; legacy runtime compatibility remains. The inherited first-run demo recording is no longer seeded into new profiles because its rights and spoken branding are unresolved.
- Imported release/store/CLA/funding automation was archived; active CI has read-only permissions and SpeechNexa migration gates. Local provenance and model-inventory checks passed in the specialist pass. Model weights are not checked in.

## Current verification and limits

- The earlier full Python suite excluding `tests/smoke/` passed: 9,844 passed, 84 skipped, 2 expected failures and 7 unexpected passes. After the dependency upgrade, `backend/tests/` passed 515 tests; 203 affected Python tests passed with 7 skips, 188 setup/pin tests passed, and 58 Torch/failure tests passed. A final 41 focused watermark/PIN/pin tests passed. The boot smoke passed separately before these changes (4 tests). The remaining macOS hotkey smoke requires Cargo, which is absent on this host. Electron under bundled Node 24 and Bun 1.4.2: renderer suite 1,681 passed and 2 skipped; shared suite 2,902 passed. Typecheck, locale contract, Electron and web builds, packaging contract, frozen Bun install, and 107 root frontend tests passed. The repeated-window desktop UI smoke was stopped at the owner's request; its focused local-first and fake-backend checks passed. These results overlap; they are not additive.
- Gitleaks found zero leaks in both staged publication changes and the two commits reachable from `main`. New GitHub Actions results are still needed for the latest changes. `git diff --check` and the SpeechNexa migration/model-license validators passed locally. Current Bandit scan: 16 medium, zero high. Fresh default-lock pip-audit: 7 findings in 4 packages, down from the earlier 52-reported CI snapshot; Bun audit: 6 development-tool findings, down from 55, with no reported production dependency advisory. Exact IDs, affected paths and mitigations are in [the security review](SECURITY_REVIEW_2026-10-24.md).
- Before the repository became private, GitHub reported 566 open code-scanning alerts from an old upstream-backed commit: 550 CodeQL and 16 Bandit findings. They had not been re-evaluated on the corrected root. Private-repository CodeQL uploads failed with `Resource not accessible by integration`; the updated workflow runs CodeQL after public visibility is restored and retains secret, Bandit and dependency checks in either visibility. Old alerts require fresh-current-source triage; no claim of 566 fixes is made.
- macOS is the only runtime host used for real speech. Windows and Linux execution, native installers, native mobile apps, other model adapters and all imported workflows are unverified. A full first-release claim requires those gates and GitHub CI.
- Jobs begin after model prewarming; a model-load wait can occur before a job ID is available. Persistence records state but does not replay a crashed generation. A history retention action can remove an output while its job metadata remains.
- Analytics/account/cloud/update paths are disabled or gated for the migration. Active SpeechNexa UI and backend messages were audited; technical compatibility keys, truthful upstream provenance, and dormant inherited account/sponsor code remain. The old Docker base images are not validated against the newly matched PyTorch 2.10 stack; inherited Docker publishing remains disabled.
- The real KittenTTS smoke remains verified from the earlier offline run, but it could not be repeated after the dependency update because the model files were absent from the available local cache. No model was downloaded to make this check pass. The remaining Python advisories concern local/untrusted checkpoint loading or packaging; see the security review. Native Windows/Linux and the upgraded Torch GPU paths remain unverified.

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
