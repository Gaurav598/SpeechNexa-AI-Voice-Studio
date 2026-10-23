"""The imported analytics project must never be a SpeechNexa default."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_POSTHOG_KEY_RE = re.compile(r"phc_[A-Za-z0-9]{20,}")
_SKIP_DIRS = {"node_modules", ".git", "target", "dist", "build", ".venv", "zig-out"}
_SCAN_EXT = {".ts", ".tsx", ".js", ".jsx", ".py", ".rs", ".json", ".yml", ".yaml", ".md", ".env"}


def _source_files():
    result = subprocess.run(["git", "ls-files", "-z"], cwd=_REPO, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        paths = (Path(name) for name in result.stdout.split("\0") if name)
    else:
        paths = (path.relative_to(_REPO) for path in _REPO.rglob("*"))
    for path in paths:
        if any(part in _SKIP_DIRS for part in path.parts) or path.suffix.lower() not in _SCAN_EXT:
            continue
        yield path


def test_no_inherited_posthog_key_in_source():
    offenders = []
    for path in _source_files():
        if path == Path("tests/test_no_committed_analytics_token.py"):
            continue
        try:
            source = (_REPO / path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if _POSTHOG_KEY_RE.search(source):
            offenders.append(str(path))
    assert not offenders, f"committed PostHog destinations: {offenders}"


def test_analytics_still_accepts_explicit_own_project_configuration():
    frontend = (_REPO / "electron/src/shared/utils/analytics.ts").read_text(encoding="utf-8")
    backend = (_REPO / "backend/core/analytics.py").read_text(encoding="utf-8")
    shell = (_REPO / "electron/src/main/backend.ts").read_text(encoding="utf-8")
    config = (_REPO / "electron/electron.vite.config.ts").read_text(encoding="utf-8")
    assert "VITE_POSTHOG_KEY" in frontend and "VITE_POSTHOG_KEY" in config
    assert "POSTHOG_PROJECT_TOKEN" in backend and "POSTHOG_PROJECT_TOKEN" in shell
    assert "_PUBLIC_PROJECT_TOKEN = \"\"" in backend
    assert "PUBLIC_PROJECT_TOKEN = ''" in frontend
