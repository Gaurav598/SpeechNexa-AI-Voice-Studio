# Third-party notices

This inventory points to the retained notices and known license boundaries. It
is not a blanket clearance for every downloaded dependency or model revision.

| Component | Reported terms and notice |
| --- | --- |
| VoiceStudio application source | AGPL-3.0-only; [LICENSE](LICENSE) and [LICENSE-NOTICE.md](LICENSE-NOTICE.md). Copyright remains with Palash Debnath and VoiceStudio contributors. |
| Bundled `omnivoice/` model code | Upstream authors identify code as Apache-2.0; the [Apache-2.0 text](omnivoice/LICENSE-APACHE-2.0.txt) is retained beside the code. Some inherited file headers still refer to `../../LICENSE`, which was the upstream source layout; this repository's root `LICENSE` covers the derivative application. Weight and tokenizer terms are separate; see [OmniVoice's model card](https://huggingface.co/k2-fsa/OmniVoice). |
| Electron components adapted from T3 Code | MIT; retain [electron/T3CODE-LICENSE.txt](electron/T3CODE-LICENSE.txt). |
| Electron test fixture | MIT text retained at [electron/src/main/fixtures/LICENSE](electron/src/main/fixtures/LICENSE). |
| Mobile Inter font and Android dependencies | Notices and license texts retained under `mobile/android/app/src/main/assets/licenses/` and `mobile/ios/VoiceStudio/Resources/Licenses/`. |
| PyAV 15.1.0 wheels and bundled media libraries | [Wheel and FFmpeg/x264/x265 audit](docs/licensing/pyav-15.1.0-audit.md); binary redistribution obligations remain unresolved there. |
| Model weights, conversions, tokenizers and SDK-loaded assets | Per-model evidence in [backend/config/model_licenses.json](backend/config/model_licenses.json), [model inventory](docs/licensing/model-inventory.md), and [model credits](docs/model-credits.md). |
| Bundled demonstration audio and video | Example media under `backend/assets/samples/` is part of the imported source archive. The [dubbing manifest](backend/assets/samples/demo/dubbing/manifest.json) explicitly records `NOASSERTION` and `license_review_required: true`; the demo render scripts also require output-rights review. The exact recording, voice, model, and output rights for the checked-in bytes have not been independently verified. |

Resolved application dependency sets are recorded in `bun.lock`, `uv.lock`, and
`native/desktop-bridge/Cargo.lock`. Distribution of bundled binaries requires
reviewing the actual files and applicable license texts, including any notices
from transitive components. No downloaded model cache or unreviewed weight is
part of this notice.
