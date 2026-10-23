"""The imported owner's publication and payment automation stays inactive."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / ".github" / "workflows"
ARCHIVE = ROOT / "docs" / "archive" / "upstream-workflows"
spec = importlib.util.spec_from_file_location("check_migration_safety", ROOT / "scripts" / "check_migration_safety.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
check_active_workflows = checker.check_active_workflows

UPSTREAM_AUTOMATION = {
    "docker.yml",
    "electron-release.yml",
    "snap-store.yml",
    "microsoft-store.yml",
    "mac-app-store.yml",
    "cla.yml",
    "docs-drift.yml",
    "build-omnivoice-tts.yml",
    "install-smoke.yml",
    "commit-identity.yml",
    "evals.yml",
}


def test_inherited_publication_and_owner_automation_is_archived():
    assert all(not (ACTIVE / name).exists() for name in UPSTREAM_AUTOMATION)
    assert all((ARCHIVE / name).exists() for name in UPSTREAM_AUTOMATION)
    assert not (ROOT / ".github" / "FUNDING.yml").exists()
    assert not (ROOT / ".github" / "CLA-1.0.md").exists()
    assert not (ROOT / ".github" / "ISSUE_TEMPLATE" / "sponsor.yml").exists()


def test_final_tauri_feeds_remain_historical_and_immutable():
    release = (ARCHIVE / "electron-release.yml").read_text(encoding="utf-8")
    assert "Preserve the final Tauri updater feeds" in release
    assert "latest.json" in release and "latest-user.json" in release
    assert (ROOT / "scripts" / "prepare_electron_release.py").exists()


def test_active_workflows_are_reviewed_read_only_ci():
    assert check_active_workflows(ACTIVE) == []


def test_unknown_or_publishing_workflow_fails_closed(tmp_path):
    (tmp_path / "publish.yml").write_text("name: New publisher\npermissions: write-all\n")
    (tmp_path / "ci.yml").write_text("permissions:\n  contents: write\n")
    (tmp_path / "mobile.yml").write_text("env:\n  KEY: ${{ secrets.STORE_KEY }}\n")
    errors = check_active_workflows(tmp_path)
    assert any("Unreviewed active workflow: publish.yml" in error for error in errors)
    assert any("write-all: publish.yml" in error for error in errors)
    assert any("write permission: ci.yml" in error for error in errors)
    assert any("unreviewed secret: mobile.yml" in error for error in errors)
    assert any("read-only default permission: mobile.yml" in error for error in errors)
