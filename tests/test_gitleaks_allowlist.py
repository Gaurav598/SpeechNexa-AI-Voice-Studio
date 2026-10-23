"""The secret-scan allowlist must remain exact and value-scoped."""
import hashlib
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_EXACT_REGEXES = {
    "^528e871c2a26c4f0f7773b9754e2e1acae20899d$",
    "^hf_abcdefghijklmnopqrstuvwxyz01234567890abcd$",
    "^hf_abcdefghijklmnopqrstuvwxyz0123456789ABCDEF$",
    "^hf_QWERTYUIOPasdfghjklZXCVBNM0123456789xyzAB$",
    "^max_length=400$",
    "^Ed25519PrivateKey$",
    r"^omnivoice\.dubSplit\.v1$",
}


def test_gitleaks_allowlist_contains_only_reviewed_exact_values():
    config = tomllib.loads((ROOT / ".gitleaks.toml").read_text(encoding="utf-8"))
    allowlist = config["allowlist"]

    assert set(allowlist) == {"description", "regexes"}
    assert set(allowlist["regexes"]) == EXPECTED_EXACT_REGEXES
    assert not any("phc_" in regex for regex in allowlist["regexes"])
    assert all(
        regex.startswith("^") and regex.endswith("$")
        for regex in allowlist["regexes"]
    )
    assert "rules" not in config


def test_dub_storage_key_allowlist_does_not_hide_similar_credentials():
    config = tomllib.loads((ROOT / ".gitleaks.toml").read_text(encoding="utf-8"))
    regexes = config["allowlist"]["regexes"]
    assert any(re.fullmatch(regex, "omnivoice.dubSplit.v1") for regex in regexes)
    for value in (
        "omnivoiceXdubSplitXv1",
        "omnivoice.dubSplit.v1-secret",
        "secret-omnivoice.dubSplit.v1",
    ):
        assert not any(re.fullmatch(regex, value) for regex in regexes)


# SHA-256 of each retired PostHog project token that history still holds (the
# value itself may only appear in the two canonical analytics files).
_RETIRED_TOKEN_SHA256 = {"cf19c9566b83f7375f591f5fbf776b9c344025805d12c16bd21333f70a708f72"}
_FINGERPRINT = re.compile(r"^([0-9a-f]{40}):([^:]+):([a-z0-9-]+):([0-9]+)$")
_PUBLIC_WEBSOCKET_SAMPLE = (
    "f6d634e19902c0fd0e64947e635359d5bc1f85de:"
    "electron/tests/fake-health-backend.test.mjs:generic-api-key:59"
)
_EXPECTED_IGNORES = {
    "23f1767e3c4f971cc5d8e4c8b84fb17337b69bc5:backend/core/analytics.py:generic-api-key:57",
    "23f1767e3c4f971cc5d8e4c8b84fb17337b69bc5:frontend/src/utils/analytics.ts:generic-api-key:44",
    _PUBLIC_WEBSOCKET_SAMPLE,
}


def _ignored_fingerprints():
    text = (ROOT / ".gitleaksignore").read_text(encoding="utf-8")
    return [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]


def test_gitleaks_ignores_only_commit_pinned_posthog_findings():
    """Only reviewed findings in specific commits may be ignored."""
    import subprocess

    entries = _ignored_fingerprints()
    assert len(entries) == len(_EXPECTED_IGNORES)
    assert set(entries) == _EXPECTED_IGNORES
    shallow = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip() == "true"
    for entry in entries:
        match = _FINGERPRINT.fullmatch(entry)
        assert match, f"not a commit-pinned fingerprint: {entry}"
        commit, path, _rule, line = match.groups()
        if shallow:
            continue
        shown = subprocess.run(
            ["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, text=True,
        )
        assert shown.returncode == 0, f"cannot read the pinned commit and path: {entry}"
        source_line = shown.stdout.splitlines()[int(line) - 1]
        if entry == _PUBLIC_WEBSOCKET_SAMPLE:
            rfc_sample = "dGhlIHNhbXBsZSBu" + "b25jZQ=="
            assert source_line.strip() == f"'Sec-WebSocket-Key': '{rfc_sample}',"
            continue
        # Only the retired public PostHog project token may be skipped.
        token = re.search(r"phc_[A-Za-z0-9]{20,}", source_line)
        assert token, entry
        assert hashlib.sha256(token.group(0).encode()).hexdigest() in _RETIRED_TOKEN_SHA256, entry
