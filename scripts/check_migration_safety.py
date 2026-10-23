"""Fail CI if inherited publication or data destinations become active again."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
ARCHIVE = ROOT / "docs" / "archive" / "upstream-workflows"
DISABLED = {
    "build-omnivoice-tts.yml",
    "cla.yml",
    "commit-identity.yml",
    "docs-drift.yml",
    "docker.yml",
    "electron-release.yml",
    "evals.yml",
    "install-smoke.yml",
    "mac-app-store.yml",
    "microsoft-store.yml",
    "snap-store.yml",
}
ACTIVE_CI = {
    "ci.yml",
    "cosyvoice-dependencies.yml",
    "electron-build.yml",
    "mobile.yml",
    "security.yml",
    "speechnexa-safety.yml",
}


def check_active_workflows(directory: Path) -> list[str]:
    """Keep repository automation limited to the reviewed, read-only CI set."""
    errors: list[str] = []
    for file in sorted(directory.iterdir()):
        if file.suffix not in {".yml", ".yaml"}:
            continue
        if file.name not in ACTIVE_CI:
            errors.append(f"Unreviewed active workflow: {file.name}")
        # Match YAML permission keys at either workflow or job scope. CodeQL's
        # security-events: write is the one reviewed exception for SARIF upload.
        source = "\n".join(line.split("#", 1)[0] for line in file.read_text(encoding="utf-8").splitlines())
        if not re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", source):
            errors.append(f"Workflow lacks explicit read-only default permission: {file.name}")
        if re.search(r"(?m)^\s*permissions:\s*write-all\s*$", source):
            errors.append(f"Workflow grants write-all: {file.name}")
        if re.search(r"(?m)^\s*(?!security-events:)[\w-]+:\s*write\s*$", source):
            errors.append(f"Workflow grants a publishing-capable write permission: {file.name}")
        if re.search(r"\bsecrets\.(?!GITHUB_TOKEN\b)[A-Za-z_][A-Za-z_0-9]*", source):
            errors.append(f"Workflow accesses an unreviewed secret: {file.name}")
    return errors


def check() -> list[str]:
    errors: list[str] = []
    errors.extend(check_active_workflows(WORKFLOWS))
    for name in sorted(DISABLED):
        if (WORKFLOWS / name).exists():
            errors.append(f"Inherited workflow is active: {name}")
        if not (ARCHIVE / name).exists():
            errors.append(f"Historical workflow missing: {name}")
    for rel in (".github/FUNDING.yml", ".github/CLA-1.0.md", ".github/ISSUE_TEMPLATE/sponsor.yml"):
        if (ROOT / rel).exists():
            errors.append(f"Inherited owner configuration is active: {rel}")

    token = re.compile(r"phc_[A-Za-z0-9]{20,}")
    for base in (ROOT / "backend", ROOT / "electron"):
        for file in base.rglob("*"):
            if not file.is_file() or file.suffix not in {".py", ".ts", ".tsx", ".js", ".jsx"}:
                continue
            if any(part in {"node_modules", "dist", "build", ".venv"} for part in file.parts):
                continue
            if token.search(file.read_text(encoding="utf-8", errors="ignore")):
                errors.append(f"Hardcoded analytics project: {file.relative_to(ROOT)}")

    updater = (ROOT / "electron/src/main/distribution.ts").read_text(encoding="utf-8")
    if "SPEECHNEXA_ENABLE_UPDATES === '1'" not in updater:
        errors.append("Updater no longer requires SpeechNexa opt-in")
    report = (ROOT / "electron/src/shared/utils/bugReport.js").read_text(encoding="utf-8")
    if "https://github.com/Gaurav598/SpeechNexa-AI-Voice-Studio" not in report:
        errors.append("Bug reports no longer target SpeechNexa")
    return errors


if __name__ == "__main__":
    failures = check()
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        raise SystemExit(1)
    print("SpeechNexa migration safety checks passed")
