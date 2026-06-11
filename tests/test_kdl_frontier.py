"""Tests for KDL Frontier backend configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

from pdf2md.backends.kdl_frontier import convert_pdf
from pdf2md.backends.kdl_frontier_engine import KdlFrontierConfigError, parse_document


def test_convert_pdf_requires_endpoint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KDL_NANO_ENDPOINT_URL", raising=False)
    with pytest.raises(KdlFrontierConfigError, match="KDL_NANO_ENDPOINT_URL"):
        convert_pdf(Path("dummy.pdf"), tmp_path)


def test_parse_document_requires_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KDL_NANO_ENDPOINT_URL", raising=False)
    with pytest.raises(KdlFrontierConfigError, match="KDL_NANO_ENDPOINT_URL"):
        parse_document([])
