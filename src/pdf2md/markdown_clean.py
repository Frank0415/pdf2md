"""Post-process converted markdown into plain document text."""

from __future__ import annotations

import re
from pathlib import Path

_SUP_PAIR = re.compile(r"<sup>(.*?)</sup>", re.IGNORECASE | re.DOTALL)
_SUP_FRAGMENT = re.compile(r"</?sup\s*>", re.IGNORECASE)


def strip_sup_markup(text: str) -> str:
    """Remove MinerU <sup> wrappers; keep inner text as normal document content."""
    cleaned = text
    for _ in range(32):
        next_text, count = _SUP_PAIR.subn(r"\1", cleaned)
        cleaned = next_text
        if count == 0:
            break
    cleaned = _SUP_FRAGMENT.sub("", cleaned)
    return cleaned


def clean_document_markdown(path: Path) -> bool:
    """Rewrite document.md in place. Returns True if content changed."""
    path = Path(path)
    original = path.read_text(encoding="utf-8")
    cleaned = strip_sup_markup(original)
    if cleaned == original:
        return False
    path.write_text(cleaned, encoding="utf-8")
    return True
