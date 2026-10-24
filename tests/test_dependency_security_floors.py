"""Keep resolved dependencies above reviewed security-fix floors."""

from collections import defaultdict
from pathlib import Path
import tomllib

from packaging.version import Version


PYTHON_FLOORS = {
    "aiohttp": "3.14.3",
    "cryptography": "50.0.0",
    "certifi": "2026.10.19",
    # Hydra instantiate and logging-config callable resolution, fixed in 1.3.7.
    "hydra-core": "1.3.7",
    # GHSA-qqmf-gpg7-g8gw: checkpoint _instantiator code execution, fixed in
    # 2.6.6. The advisory range is malformed (< 2022.6.15), so Dependabot
    # still flags fixed releases; this floor is the real guard.
    "lightning": "2.6.6",
    "mako": "1.4.2",
    "mcp": "1.30.0",
    "msgpack": "1.2.1",
    "multidict": "6.9.1",
    "nltk": "3.10.0",
    "pillow": "13.0.0",
    "protobuf": "5.29.6",
    "pydantic-settings": "2.14.2",
    "pygments": "2.20.0",
    "pypdf": "6.21.1",
    "pytorch-lightning": "2.6.6",
    "python-multipart": "0.0.31",
    "starlette": "1.3.1",
    "transformers": "5.10.0",
    "yt-dlp": "2026.7.4",
}


def _resolved_versions(packages, names):
    resolved = defaultdict(list)
    for package in packages:
        name = package["name"].lower()
        if name in names:
            resolved[name].append(Version(package["version"]))
    return dict(resolved)


def _versions_below_floors(resolved, floors):
    return {
        name: [str(version) for version in versions if version < Version(floors[name])]
        for name, versions in resolved.items()
        if any(version < Version(floors[name]) for version in versions)
    }


def test_python_security_floors_are_locked():
    lock = tomllib.loads(Path("uv.lock").read_text(encoding="utf-8"))
    resolved = _resolved_versions(lock["package"], PYTHON_FLOORS)
    assert resolved.keys() == PYTHON_FLOORS.keys()
    assert _versions_below_floors(resolved, PYTHON_FLOORS) == {}


def test_default_lock_excludes_legacy_ui_and_vulnerable_argos_loader():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    lock = tomllib.loads(Path("uv.lock").read_text(encoding="utf-8"))
    locked = {package["name"] for package in lock["package"]}

    assert "gradio" not in locked
    assert "argostranslate" not in locked
    assert "stanza" not in locked
    assert "omnivoice-demo" not in project["project"]["scripts"]


def test_duplicate_lock_entries_cannot_hide_a_vulnerable_version():
    packages = [
        {"name": "demo", "version": "2.0"},
        {"name": "demo", "version": "0.9"},
    ]
    floors = {"demo": "1.0"}
    resolved = _resolved_versions(packages, floors)
    assert resolved == {"demo": [Version("2.0"), Version("0.9")]}
    assert _versions_below_floors(resolved, floors) == {"demo": ["0.9"]}
