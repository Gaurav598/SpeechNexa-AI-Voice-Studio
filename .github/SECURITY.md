# SpeechNexa security

SpeechNexa is a personal project whose source is being migrated. There is no verified binary release or support window. Security fixes are made on `main`; inherited release and response-time promises do not apply.

## Reporting

Report a suspected vulnerability through the repository's private [GitHub security advisory](https://github.com/Gaurav598/SpeechNexa-AI-Voice-Studio/security/advisories/new). Do not post exploit details in a public issue or send them to upstream project accounts; those accounts do not operate SpeechNexa.

## Current checks

Every push to `main` runs [the security workflow](workflows/security.yml). It checks for leaked secrets, Python static findings, and dependency advisories. CodeQL is configured for Python and JavaScript/TypeScript on the public repository. Findings remain open for triage until a current successful analysis resolves them; a green workflow alone does not establish that the code has no vulnerabilities. [The current security review](../docs/SECURITY_REVIEW_2026-10-24.md) records remaining findings and limits.

Local inference should remain on loopback unless the owner explicitly configures authentication and network access. Model archives, audio and video inputs, and dependencies remain untrusted inputs. Review [API authentication](../docs/api-auth.md) and [model licenses](../docs/MODEL_LICENSING.md) before exposure or redistribution.
