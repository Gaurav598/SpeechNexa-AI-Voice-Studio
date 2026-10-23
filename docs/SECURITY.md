# Security and local-first boundaries

The supported backend binds to `127.0.0.1` by default. Keep it on loopback: the local API is not a public multi-user service and has no general remote authentication layer. Opening it to another host requires an explicit security review.

Model downloads are user initiated. The verified offline KittenTTS path starts with `HF_HUB_OFFLINE=1` and an installed snapshot. The optional AudioSeal generator is loaded only from a present local checkpoint during generation; `scripts/smoke_real_tts.py` verifies no AudioSeal cache write in an isolated run. Inherited analytics, account/cloud and packaged updater integrations are disabled or gated in the SpeechNexa migration. Inspect the relevant settings before enabling any external service.

Do not commit secrets, local model caches, generated audio, recordings or application databases. `scripts/check_migration_safety.py` checks active publication and endpoint boundaries; the SpeechNexa safety workflow runs it without write permissions. This check is not a substitute for reviewing credentials, dependency updates and binary distribution obligations.

Application source and separately licensed assets have different terms. The rights of imported sample audio/video are unresolved; see [third-party notices](../THIRD_PARTY_NOTICES.md) and [model licensing](MODEL_LICENSING.md).
