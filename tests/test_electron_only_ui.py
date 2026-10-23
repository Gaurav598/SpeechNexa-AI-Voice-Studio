import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tauri_shell_and_legacy_ui_entrypoints_are_removed():
    assert not (ROOT / "frontend/src-tauri").exists()
    assert not (ROOT / "frontend/src").exists()
    assert not (ROOT / ".github/workflows/release.yml").exists()
    for path in (
        "frontend/index.html",
        "electron/src/shared/main.jsx",
        "electron/src/shared/main-app.jsx",
        "electron/src/shared/App.jsx",
        "scripts/desktop-dev.mjs",
        "scripts/desktop-dev-launch.mjs",
        "scripts/desktop-prod.sh",
        "scripts/desktop-prod.mjs",
        "scripts/desktop-fresh.mjs",
    ):
        assert not (ROOT / path).exists(), f"retired Tauri entrypoint remains: {path}"


def test_supported_ui_commands_target_electron_only():
    root_package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert root_package["workspaces"] == ["electron"]
    for command in ("dev", "desktop", "build", "build:web", "start", "test", "typecheck"):
        assert "electron" in root_package["scripts"][command]

    assert not (ROOT / "frontend/package.json").exists()
    manifests = [ROOT / "package.json", ROOT / "electron/package.json"]
    assert all("@tauri-apps/" not in path.read_text(encoding="utf-8") for path in manifests)

    electron_package = json.loads((ROOT / "electron/package.json").read_text(encoding="utf-8"))
    assert "vite.shared.config.ts" in electron_package["scripts"]["test"]


def test_docker_builds_the_electron_renderer():
    dockerfile = (ROOT / "deploy/Dockerfile").read_text(encoding="utf-8")
    assert "--cwd electron build:web" in dockerfile
    assert "frontend/index.html" not in dockerfile


def test_macos_dev_launcher_uses_maintained_electron_paths():
    launcher = (ROOT / "electron/scripts/dev.mjs").read_text(encoding="utf-8")
    assert "join(repoRoot, 'package.json')" in launcher
    assert "join(electronRoot, 'build', 'icons', 'icon.icns')" in launcher
    assert "'frontend'" not in launcher


def test_home_keeps_creation_actions_with_localized_product_heading():
    home = (ROOT / "electron/src/renderer/src/features/home/home-page.tsx").read_text(
        encoding="utf-8"
    )
    assert "t('nav.home')" in home
    assert "t('homeUi.title')" in home
    assert "t('homeUi.subtitle')" in home
    assert "<HomeContributors />" in home
    assert "group.map(" in home
    assert "browser.open('https://voicestudio.sh')" not in home
    assert "PanelLeftOpenIcon" not in home


def test_inherited_install_smoke_does_not_install_upstream_releases_in_ci():
    assert not (ROOT / ".github/workflows/install-smoke.yml").exists()
    assert (ROOT / "docs/archive/upstream-workflows/install-smoke.yml").exists()
