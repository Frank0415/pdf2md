"""Post-process converted markdown into clear, MarkItDown-style document text."""

from __future__ import annotations

import re
from pathlib import Path

_SUP_PAIR = re.compile(r"<sup>(.*?)</sup>", re.IGNORECASE | re.DOTALL)
_SUP_FRAGMENT = re.compile(r"</?sup\s*>", re.IGNORECASE)
_IMAGE_LINE = re.compile(r"^\s*!\[[^\]]*\]\([^)]+\)\s*$", re.MULTILINE)
_DETAILS_BLOCK = re.compile(r"<details>.*?</details>\s*", re.IGNORECASE | re.DOTALL)
_MERMAID_BLOCK = re.compile(r"```mermaid\s*.*?```\s*", re.IGNORECASE | re.DOTALL)
_HTML_TAG = re.compile(r"<[^>]+>")
_MULTI_BLANK = re.compile(r"\n{3,}")


def strip_sup_markup(text: str) -> str:
    """Remove MinerU <sup> wrappers; keep inner text as normal document content."""
    cleaned = text
    for _ in range(32):
        next_text, count = _SUP_PAIR.subn(r"\1", cleaned)
        cleaned = next_text
        if count == 0:
            break
    return _SUP_FRAGMENT.sub("", cleaned)


def to_clear_markdown(text: str) -> str:
    """Normalize VLM-heavy output toward plain MarkItDown-style markdown."""
    cleaned = strip_sup_markup(text)
    cleaned = _DETAILS_BLOCK.sub("", cleaned)
    cleaned = _MERMAID_BLOCK.sub("", cleaned)
    cleaned = _IMAGE_LINE.sub("", cleaned)
    cleaned = _HTML_TAG.sub("", cleaned)
    cleaned = _MULTI_BLANK.sub("\n\n", cleaned)
    return cleaned.strip() + "\n"


def clean_document_markdown(path: Path) -> bool:
    """Rewrite document.md in place. Returns True if content changed."""
    path = Path(path)
    original = path.read_text(encoding="utf-8")
    cleaned = to_clear_markdown(original)
    if cleaned == original:
        return False
    path.write_text(cleaned, encoding="utf-8")
    return True
