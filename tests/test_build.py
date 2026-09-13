"""Unit tests for scripts/build_app.py: inlining CSS, JS and the pack into dist/index.html."""

from __future__ import annotations

import re
from pathlib import Path

import build_app
import pytest

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = "<html><head><!-- CSS --></head><body><!-- PACK --><!-- JS --></body></html>"


def test_inline_replaces_placeholders():
    result = build_app.inline(
        TEMPLATE,
        css_parts=["a{}", "b{}"],
        js="x=1",
        pack_json='{"a":"</script>"}',
    )
    assert "<style>a{}\nb{}</style>" in result
    assert (
        '<script type="application/json" id="pack">{"a":"<\\/script>"}</script>' in result
    )
    assert "<script>x=1</script>" in result


def test_inline_missing_placeholder_raises():
    with pytest.raises(ValueError, match="PACK"):
        build_app.inline(
            "<html><head><!-- CSS --></head><body><!-- JS --></body></html>",
            css_parts=["a{}"],
            js="x=1",
            pack_json="{}",
        )


def test_real_build():
    build_app.main()
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")

    assert html.count('id="pack"') == 1
    assert "<link" not in html
    assert "<script src" not in html
    assert len(html.encode("utf-8")) <= 1_048_576

    stripped = re.sub(
        r'<script type="application/json" id="pack">.*?</script>', "", html, flags=re.S
    )
    assert "http://" not in stripped
    assert "https://" not in stripped
    assert "DIC005" not in stripped
