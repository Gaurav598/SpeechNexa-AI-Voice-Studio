# Source provenance

SpeechNexa is an AGPL-3.0-only derivative of
[VoiceStudio](https://github.com/debpalash/VoiceStudio), originally developed
by Palash Debnath and VoiceStudio contributors. The imported tree was supplied
as a local source archive in `SpeechNexa/`; it contained no `.git` directory.
Its exact application commit, branch, commit authors, and archive checksum could
not be verified from the archive alone. Upstream commit
[`28bf2c7a83b8a64836297340c52a45d716684aed`](https://github.com/debpalash/VoiceStudio/commit/28bf2c7a83b8a64836297340c52a45d716684aed)
is a comparison reference, not proof that every file in the downloaded archive
matched it. The owner's SpeechNexa repository uses its own root source snapshot
and owner-authored Git commits; it does not import VoiceStudio's commit history
or assign that history to the owner. Original authorship and licenses remain
credited in inherited source notices, this document, and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The `source_commit` field in
`backend/config/model_licenses.json` tracks that model inventory's evidence;
it is **not** proof of the application archive's Git revision. Preserve any
additional source attribution found during future provenance review, and record
a verified recursive import revision here before making one a public claim.

A limited comparison against upstream commit
`28bf2c7a83b8a64836297340c52a45d716684aed` found these five files to
have matching Git blob IDs **before SpeechNexa edits**:

| File | Matching Git blob ID |
| --- | --- |
| `CHANGELOG.md` | `d31eadf29409b8bbf3643b7bf00d45c7113d6aeb` |
| `CLAUDE.md` | `c449644142211cc981940bd2f26f23a0de5acc52` |
| `README.md` | `9f5b7e01370e672810bd9b33fe3b19cd1862fd37` |
| `bun.lock` | `5ad446e829d9392ee19d74fa76861fdcdd259f4a` |
| `package.json` | `2d042bd7e33b12c1b5d858bb8005bd8e8925bb2a` |

This comparison does not establish a recursive tree match or the archive's
complete source revision. `bun.lock` and `package.json` changed as part of the
SpeechNexa migration.

The imported application includes the Electron UI, Python/FastAPI backend,
native helper, mobile sources, tests, docs, and build tooling. Retained code and
existing notices remain attributed to their original authors. SpeechNexa's
own work is identifiable through its personal project history and release notes;
the new product name does not assert independent authorship of imported code,
models, or weights.

The imported tree also contains demonstration audio and video under
`backend/assets/samples/`. Its recording, voice, and generation provenance has
not been independently verified; the imported dubbing manifest itself records
`NOASSERTION` and `license_review_required: true`. Source publication under the
application's AGPL terms does not by itself establish permission to redistribute
those media files or any separately licensed model weights. Review the media
rights before calling a public source or binary distribution fully cleared.

The full source license is [AGPL-3.0-only](LICENSE). Separate third-party and
model boundaries are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
and [docs/MODEL_LICENSING.md](docs/MODEL_LICENSING.md).

The inherited publication and owner-specific automation has been moved to
`docs/archive/upstream-workflows/` and `docs/archive/upstream-github-config/`.
Those files are historical references, not SpeechNexa release instructions.
The final Tauri updater assets hosted by the original project are immutable
legacy compatibility assets; this repository does not build or republish them.
Existing Tauri users should follow the upstream
[Electron migration guide](docs/electron-migration.md). SpeechNexa's active
desktop UI is Electron only.
