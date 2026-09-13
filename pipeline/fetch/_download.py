"""Shared helpers for streaming fetched files to disk."""

from __future__ import annotations

from pathlib import Path


def present_at(dest: Path, expected_size: int | None) -> bool:
    return dest.is_file() and (not expected_size or dest.stat().st_size == expected_size)


def stream_to_file(response, dest: Path, chunk_bytes: int = 1 << 20) -> int:
    partial = dest.with_name(dest.name + ".part")
    with partial.open("wb") as file:
        for chunk in response.iter_content(chunk_size=chunk_bytes):
            if chunk:
                file.write(chunk)
    partial.replace(dest)
    return dest.stat().st_size
