"""Post-process converted markdown into plain document text."""

from __future__ import annotations

import re
from pathlib import Path

_SUP_PAIR = re.compile(r"<sup>(.*?)</sup>", re.IGNORECASE | re.DOTALL)
_SUP_FRAGMENT = re.compile(r"</?sup\s*>", re.IGNORECASE)
_DETAILS_BLOCK = re.compile(r"<details>.*?</details>\s*", re.IGNORECASE | re.DOTALL)
_SUMMARY_TAG = re.compile(r"<summary>.*?</summary>\s*", re.IGNORECASE | re.DOTALL)
_IMAGE_ALT = re.compile(r"!\[[^\]]*\]\(")
_IMAGE_LINE = re.compile(r"^\s*!\[[^\]]*\]\([^)]+\)\s*$")
_MERMAID_BLOCK = re.compile(r"```mermaid\s*.*?```\s*", re.IGNORECASE | re.DOTALL)
_HTML_TAG = re.compile(r"<[^>]+>")
_VLM_CAPTION = re.compile(
    r"^(?:"
    r"(?:Cartoon |An )?illustration of .+|"
    r"A (?:diagram|flowchart|chart|image|figure) (?:of|showing) .+|"
    r"natural_image|flowchart"
    r")$",
    re.IGNORECASE,
)
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


def strip_image_alt_text(text: str) -> str:
    """Drop VLM-generated alt text; keep bare image references."""
    return _IMAGE_ALT.sub("![](", text)


def strip_image_description_blocks(text: str) -> str:
    """Remove MinerU <details> captions that follow image lines."""
    cleaned = text
    for _ in range(32):
        next_text, count = _DETAILS_BLOCK.subn("", cleaned)
        cleaned = next_text
        if count == 0:
            break
    return cleaned


def strip_leaked_image_captions(text: str) -> str:
    """Remove VLM caption lines that appear directly after an image reference."""
    lines = text.splitlines()
    out: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        out.append(line)
        if not _IMAGE_LINE.match(line):
            index += 1
            continue

        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        while index < len(lines):
            candidate = lines[index].strip()
            if not candidate:
                break
            if candidate.startswith(("#", "!", ">", "|", "```", "---")):
                break
            if candidate[0].isdigit() and "." in candidate[:4]:
                break
            if candidate.startswith(("•", "-", "*", "+")):
                break
            if not _VLM_CAPTION.match(candidate):
                break
            index += 1
    return "\n".join(out)


def to_clear_markdown(text: str) -> str:
    """Strip MinerU VLM artifacts while keeping image files referenced in markdown."""
    cleaned = strip_sup_markup(text)
    cleaned = strip_image_description_blocks(cleaned)
    cleaned = _MERMAID_BLOCK.sub("", cleaned)
    cleaned = _SUMMARY_TAG.sub("", cleaned)
    cleaned = strip_image_alt_text(cleaned)
    cleaned = strip_leaked_image_captions(cleaned)
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
