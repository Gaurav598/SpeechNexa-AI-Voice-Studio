# Publishing SpeechNexa source and planning releases

SpeechNexa is an AGPL-3.0-only derivative of VoiceStudio. The active GitHub
destination is `Gaurav598/SpeechNexa-AI-Voice-Studio`; `debpalash/VoiceStudio`
is a read-only provenance source. Electron is the desktop and web UI. Native
iOS and Android sources have a separate, unverified first-release contract.
The current verification state and known gaps are in
[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

This guide covers source publication and the checks required before proposing
a future binary release. No SpeechNexa release, store or container publishing
workflow is active. The manually dispatched
[`electron-build.yml`](../.github/workflows/electron-build.yml) produces
rehearsal artifacts only; it does not create a release or upload to a store.
Historical VoiceStudio workflows are archived under
[`docs/archive/upstream-workflows/`](archive/upstream-workflows/README.md) and
do not authorize SpeechNexa publication.

## Source publication checklist

1. Check `git remote -v`, the intended branch and the full diff. Push only to
   `origin` (`Gaurav598/SpeechNexa-AI-Voice-Studio`). Keep SpeechNexa's
   owner-authored commit history separate from upstream Git history. Preserve
   upstream copyright and license attribution in the source and notices; never
   push to `upstream`. Future non-fast-forward updates need explicit owner direction.
2. Review tracked files for secrets, downloaded weights, recordings, generated
   audio, caches, databases and personal files. Run the repository's secret
   scan on the actual source to be pushed. Do not treat ignored build output
   as part of the source scan.
3. Review [source provenance](../UPSTREAM.md),
   [third-party notices](../THIRD_PARTY_NOTICES.md), and
   [model licensing](MODEL_LICENSING.md). Imported sample audio and video
   rights remain unresolved; do not describe the source or a binary as fully
   rights-cleared. Preserve AGPL, Apache and MIT notices and the model license
   gates. Do not include downloaded model weights.
4. Run the migration and licensing checks, then the relevant full gates in
   [TESTING.md](TESTING.md). Keep CI model-free with `HF_HUB_OFFLINE=1` and an
   empty `HF_HUB_CACHE`. Check current CI results before merging and verify
   `main` CI afterward. Record platform and engine coverage honestly.
5. Review the destination, licenses, scan results and checks before pushing.
   The configured human submitter identity is the only commit and PR
   attribution. Record the pushed commit and CI result in
   [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

The local migration checks are:

```bash
python scripts/check_migration_safety.py
python scripts/check_model_licenses.py
python scripts/generate_model_license_data.py --check
```

These checks support a review; they do not establish third-party media or
binary redistribution rights. The active CI and security workflows have
read-only repository permissions. No inherited release, store, CLA, sponsor,
cloud, analytics or dependency-bot automation should be enabled as part of a source push.

## Versioning

Root `package.json` is the application version source. `pyproject.toml` and
`backend/core/version.py` have maintained mirrors. **Version bumps are manual and require owner approval.** Keep the three values aligned only when a bump
has been requested. Do not change the version or create a release tag merely
for a source migration. Archived Tauri manifests and the final upstream Tauri
updater feeds are immutable compatibility material; see the
[Electron migration guide](electron-migration.md).

## Future binary releases

Before a release workflow, tag or store channel is proposed, review the exact
packages and all bundled licenses, media, native dependencies and transitive
components. Verify reproducible builds, installer launch, managed backend
startup, offline generation after explicit model installation, update metadata,
and rollback behavior on each claimed platform. Use the artifact-only Electron
rehearsal as evidence where it succeeds, then test the downloaded packages on
clean hosts. The inherited workflow's historical target matrix is not proof of
SpeechNexa support. Native mobile features require both iOS and Android
verification against [`mobile/contract/SPEC.md`](../mobile/contract/SPEC.md).

Any new publishing automation needs its own review of triggers, permissions,
identities, destinations, signing, update feeds and release assets. Keep Tauri
updater feeds on their original immutable legacy assets; a Tauri client must
never receive an Electron installer. Stores, registries and app update services
are separate publication decisions. The archived
[VoiceStudio release workflow](archive/upstream-workflows/electron-release.yml)
and [store handover](STORE-PUBLISHING-HANDOVER.md) are historical reference
only.

## Credentials

Source CI does not need publishing credentials. Any future signed macOS or
Windows package must use a SpeechNexa-owned signing identity and have its
signature, notarization where applicable, and final downloaded artifact
verified before publication. No inherited VoiceStudio secret or store account
should be copied or activated by default. See the
[macOS signing verification notes](macos-signing-verification.md) for the
platform-specific checks; they do not themselves approve a release.
