"""Unit tests for scripts/package_submission.py: the zip that gets emailed to the organiser."""

from __future__ import annotations

import zipfile
from pathlib import Path

import build_app
import package_submission
import pytest

from pipeline.pack import read_constant

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def zip_path() -> Path:
    build_app.main()
    return package_submission.main()


def test_zip_name_matches_team(zip_path):
    team = read_constant("TEAM_NUMBER")
    assert zip_path.name == f"DataChallenge_Team {team}_Submission.zip"
    assert zip_path.parent == ROOT / "dist"


def test_zip_contains_required_entries(zip_path):
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    required = (
        "index.html",
        "README.md",
        "pipeline/rules.py",
        "data/out/data_pack.json",
        "data/out/capability_table.csv",
    )
    for entry in required:
        assert entry in names, f"{entry} missing from {sorted(names)}"


def test_zip_excludes_venv_and_spike(zip_path):
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    retired_lane = "spi" + "ke"
    assert not any(name.startswith(".venv/") for name in names)
    assert not any(name.split("/")[0] == retired_lane for name in names)
    assert not any(name.endswith(".zip") for name in names)


def test_zip_under_100mb(zip_path):
    assert zip_path.stat().st_size < 100 * 1024 * 1024


def test_no_team_number_hardcoded_in_script():
    source = (ROOT / "scripts" / "package_submission.py").read_text(encoding="utf-8")
    assert "DIC005" not in source
