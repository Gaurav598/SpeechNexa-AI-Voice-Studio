# SpeechNexa security review — 2026-10-24

This review records what was actually checked before republishing the personal
repository. A successful audit *job* is not a clean dependency audit: the
previous job deliberately reported findings without failing the workflow.

## Evidence and fixes

- GitHub Actions run `40007789613`, Dependency audit job `120600045706`,
  reported 52 Python findings in nine packages and 55 JavaScript findings
  (3 critical, 18 high, 25 moderate, 9 low) at commit `a0fef4460`.
  See the current Security run for the results after these changes.
- The Python lock now resolves Pillow 13.0.0, pypdf 6.21.2, MCP 1.30.0 and
  certifi 2026.10.23, meeting the published fixes for 45 of those Python
  findings. The unused standalone Gradio UI dependency and command were
  removed because Gradio requires Pillow below 13. The active product UI is
  Electron.
- A fresh `uv export --frozen --no-dev --no-emit-project` plus pip-audit 2.10.1
  initially found 16 findings. Updating `filelock` from 3.32.3 to 4.2.4
  resolved three; upgrading the matched PyTorch/TorchAudio/TorchVision stack
  from 2.8.0/2.8.0/0.23.0 to 2.10.0/2.10.0/0.25.0 resolved another six.
  The **current lock reports seven findings in four packages**: Accelerate 1,
  NLTK 1, setuptools 3 and PyTorch 2. Two setuptools entries share the same
  `PYSEC-2026-3447` identifier and are duplicate descriptions; seven is the
  scanner's reported count, six distinct identifiers. The scan evaluates the
  default dependency graph from the lock, not optional extras. This is also
  lower than the prior CI report of 52 Python findings; the prior and current
  scans are separate advisory-database snapshots, so the numerical difference
  is not a claim that every difference represents a direct code fix.
- Argos Translate pinned vulnerable Stanza 1.10.1. Both are absent from the
  default lock. Argos is an explicit optional installation; its language packs
  must still be installed by the user. Its upstream Stanza pin remains a risk
  if a user chooses that optional package; only trusted language packs should
  be loaded. NLLB needs explicitly installed model
  weights. Neither missing package nor missing weights cause an implicit model
  download.
- The optional LAN share had an unlimited six-digit PIN guessing path. Its
  middleware now limits each client to ten failed attempts per minute and
  returns `429` with `Retry-After` after that. A valid PIN or another client
  remains usable. The counter is synchronized for concurrent requests and is
  retained across PIN rotation, so overlapping share-session requests cannot
  reset it. A successful PIN clears that client's failures. The listener
  remains loopback-only until the user enables sharing.
- Gitleaks 8.30.1 scanned the three commits reachable from published `main` (about 40 MB)
  and the staged publication changes; both found zero leaks. A separate copy
  of all present tracked and non-ignored source files (about 60 MB scanned)
  also found zero leaks. The local checkout
  retains 43 inherited local tags outside `main`; scanning *all local refs*
  finds three old upstream findings and is not a verdict on SpeechNexa's
  published `main`. GitHub has no tags or other branches.

## Current CodeQL triage

The first valid public CodeQL run succeeded at `f8f9bac7` and reported 624
current-code alerts: 521 note, 70 warning and 33 error. Scan success means
analysis completed, not that all findings were fixed. Focused review found
three raw exception-to-response disclosures (watermark detection, optional
Argos package checking and legacy dubbing transcription), two unsafe log
fields, and a reflected URL in a test-only HTML fixture. These were fixed in
the follow-up source change with fail-before/pass-after response tests;
165 affected tests passed with seven unexpected passes. The CodeQL scan after
that change is required to confirm which alerts close.

The other reviewed error-level findings include a fixed-message SSE failure
wrapper, intentional opt-in LAN binding protected by PIN and per-client
limits, and path operations with basename validation, resolved-path
containment or native-only guards. They are not broadly dismissed; remaining
alerts need rule-by-rule review. In particular, CodeQL source paths alone do
not prove an unauthenticated traversal exploit or a safe false positive.

## Bandit review

The current backend Bandit 1.9.4 JSON report has 16 medium-severity findings and
zero high-severity findings. They remain visible for review rather than being
silenced by broad exclusions:

- Three B608 SQL statements build column/placeholder lists from hardcoded
  allowlists; all user values are bound parameters.
- Five B310 URL opens use fixed HTTPS destinations or require HTTPS, and
  executable downloads are checked against pinned SHA-256 and sizes.
- Four B615 Hugging Face loader calls use local snapshot paths, pinned commit
  revisions, or `local_files_only=True`; the model-install path remains an
  explicit user action.
- Two B104 findings are the deliberate optional LAN-share wildcard bind; the
  listener is opt-in and PIN-gated. The PIN rate limiter above reduces
  guessing exposure.
- Two B108 findings are literal `/tmp` strings inside validation tests, not
  temporary file creation.

## Remaining limitations

- Accelerate 1.14.0 (`PYSEC-2026-3804`) has no published fixed version and
  permits path traversal through a malicious sharded-checkpoint index.
  SpeechNexa requires an explicit, license-gated model install, but model
  files from untrusted sources remain hazardous.
- NLTK 3.10.3 (`PYSEC-2026-3740`) has no published fixed version for
  caller-controlled model-artifact paths. The local speech-generation path
  does not accept arbitrary NLTK model paths from unauthenticated clients.
- Setuptools 79.0.1 is held below 80 for legacy WhisperX/faster-whisper
  `pkg_resources` compatibility. Its remaining reported entries are
  `PYSEC-2026-3447` (twice, fixed at 83) and `GHSA-xmj3-9gf7-h52w`
  (fixed at 84.1). They concern source-package manifest assembly and legacy
  wheel installation rather than the KittenTTS generation request path.
- PyTorch 2.10.0 remains on the two reported IDs `PYSEC-2026-139` (local PT2
  loading deserialization, no fixed version in this audit) and
  `PYSEC-2025-194` (local JIT memory corruption, fixed at 2.13). There are
  no direct `torch.jit.script` or PT2 loading calls in SpeechNexa's backend
  source; transitive engines have not all been audited. The previous 2.8
  `weights_only` checkpoint-unpickling finding (`PYSEC-2026-2286`) is fixed
  by 2.10. KittenTTS synthesis uses ONNX and converts its output with
  `torch.from_numpy`; OmniVoice loads explicitly installed checkpoints with
  `torch.load(..., weights_only=True)`. Untrusted model files remain unsafe.
  The matched 2.10 stack passed 203 affected backend tests on macOS, with
  seven skips including real KittenTTS inference because its model files
  were not present in the local cache. Windows, Linux and CUDA execution of
  the upgraded stack remain unverified locally.
- Bun 1.4.2 `audit --json` against the regenerated, frozen `bun.lock` reports
  **six findings, all in the `vite-plus` development tool**: one high
  (`GHSA-587h-7wmj-h5pm`), four moderate and one low. The prior lock reported
  55 (3 critical, 18 high, 25 moderate, 9 low). The remaining high finding is
  a Windows `launch-editor` command-execution path in a development server;
  it is not included in the Electron or web production bundles and the app
  does not expose a Vite development server to remote users by default.
  Upgrading Vite+ to its patched 1.4 line pulled in Vitest 5 and broke the
  maintained test suite, so the compatible 0.3 line is retained. Developers
  should run the dev server only on trusted loopback hosts until a compatible
  patched release is validated. A green reporting-only CI job does not imply
  the six findings have disappeared.
- The 28 inherited audio/video files under `backend/assets/samples/` have
  unresolved redistribution rights. Their dubbing manifest explicitly says
  `NOASSERTION` and `license_review_required`. No rights clearance is claimed;
  existing Git commits also retain those bytes. See `UPSTREAM.md` and
  `THIRD_PARTY_NOTICES.md` before redistributing media or installers.
- A clean secret scan does not prove absence of every possible credential.
  Keep the checked-in source review and CI scan in the publication gate.
