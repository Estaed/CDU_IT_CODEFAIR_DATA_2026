"""Unit tests for pipeline.provenance: the source registry and PROVENANCE.md writer."""

from __future__ import annotations

import fnmatch
import json
import re
from pathlib import Path

import pytest

from pipeline import provenance, rules

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data/raw"
PACK = ROOT / "data/out/data_pack.json"

REQUIRED_KEYS = {"id", "name", "pack_source", "url", "licence", "attribution", "pattern", "date"}
EXPECTED_IDS = {
    "bushtel",
    "nbn_fixedline",
    "nbn_wireless",
    "accc_mir_2025",
    "rrl",
    "ntg_2019",
    "ntg_2021",
    "ntg_2022",
    "ntg_smallcell",
    "abs_ste_2021",
}
NON_EMPTY_KEYS = {"id", "name", "url", "licence", "attribution", "pattern", "date"}


def test_sources_shape():
    ids = []
    for entry in provenance.SOURCES:
        assert REQUIRED_KEYS <= set(entry.keys())
        for key in NON_EMPTY_KEYS:
            assert entry[key], f"{entry.get('id')}: empty {key}"
        ids.append(entry["id"])
    assert set(ids) == EXPECTED_IDS
    assert len(ids) == len(set(ids))


def _filename_for_pattern(pattern: str) -> str:
    """Turn a glob like 'ntg_2019.*' or 'accc_*_outdoor_2025.*' into one matching name."""
    name = pattern.replace("*", "2026-09-12")
    assert fnmatch.fnmatch(name, pattern)
    return name


def test_write_lists_every_matched_file(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    created = []
    for entry in provenance.SOURCES:
        filename = _filename_for_pattern(entry["pattern"])
        path = raw_dir / filename
        if not path.exists():
            path.write_bytes(b"x" * 10)
        created.append(path)

    out_path = tmp_path / "PROVENANCE.md"
    provenance.write(out_path, raw_dir)
    text = out_path.read_text(encoding="utf-8")

    for path in set(created):
        assert path.name in text, f"missing {path.name} in PROVENANCE.md"
        assert str(path.stat().st_size) in text, f"missing size for {path.name}"

    absent = raw_dir / "not_a_real_file_2026-09-12.zip"
    assert absent.name not in text


def test_write_raises_on_empty_raw_dir(tmp_path):
    raw_dir = tmp_path / "empty_raw"
    raw_dir.mkdir()
    with pytest.raises(Exception, match=r"pipeline\.fetch\."):
        provenance.write(tmp_path / "PROVENANCE.md", raw_dir)


def test_patterns_match_exactly_data_raw():
    if not RAW_DIR.exists():
        pytest.skip("data/raw not present in this environment")
    matched = set()
    for entry in provenance.SOURCES:
        for path in RAW_DIR.glob(entry["pattern"]):
            matched.add(path.name)
    actual = {path.name for path in RAW_DIR.iterdir() if path.is_file()}
    assert matched == actual


def _iter_src_values(communities: list[dict]):
    for community in communities:
        population = community.get("population")
        if isinstance(population, dict) and "src" in population:
            yield population["src"]
        for publisher in community.get("publishers", []):
            if "src" in publisher:
                yield publisher["src"]
        for service in community.get("services", []):
            for source in service.get("sources", []):
                if "src" in source:
                    yield source["src"]
        for flag in community.get("flags", []):
            if "src" in flag:
                yield flag["src"]


def test_pack_sources_table():
    with PACK.open(encoding="utf-8") as handle:
        pack = json.load(handle)
    sources = pack["sources"]
    assert sources, "pack sources table must not be empty"

    ids = list(sources.keys())
    assert ids == [f"s{i}" for i in range(1, len(ids) + 1)]

    pairs = [(entry["source"], entry["date"]) for entry in sources.values()]
    assert pairs == sorted(pairs)

    date_re = re.compile(r"^\d{4}(-\d{2}-\d{2})?$")
    for sid, entry in sources.items():
        assert entry.get("source"), f"{sid}: empty source"
        assert date_re.match(entry.get("date", "")), f"{sid}: bad date {entry.get('date')!r}"
        source = entry["source"]
        allowed_no_url = source.endswith(", " + rules.RULE_NAME) or source == "none published"
        if not allowed_no_url:
            assert entry.get("url"), f"{sid}: missing url for source {source!r}"

    for entry in provenance.SOURCES:
        if entry["pack_source"]:
            assert any(
                s["source"] == entry["pack_source"] for s in sources.values()
            ), f"{entry['id']}: pack_source {entry['pack_source']!r} not in pack sources table"

    for community in pack.get("communities", []):
        bushtel_id = community.get("bushtel_id")
        for src in _iter_src_values([community]):
            assert src in sources, f"unresolved src {src!r} in community {bushtel_id}"
