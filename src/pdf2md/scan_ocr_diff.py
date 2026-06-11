"""OCR-vs-extract diff scan for digital PDFs (layer B)."""

from __future__ import annotations

import re
import random
import shutil
from pathlib import Path
from typing import Any

import fitz  # pymupdf
import pytesseract
from PIL import Image

WORD_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9'\-]{1,}")
MIN_TEXT_CHARS_PER_PAGE = 40
DEFAULT_SAMPLE_COUNT = 3
RENDER_DPI = 150


def _normalize_words(text: str) -> set[str]:
    return {m.group(0).lower() for m in WORD_RE.finditer(text)}


def is_digital_pdf(pdf_path: Path, *, sample_pages: int = 3) -> bool:
    """Heuristic: enough extractable text on sampled pages."""
    doc = fitz.open(pdf_path)
    try:
        if doc.page_count == 0:
            return False
        indices = _sample_page_indices(doc.page_count, sample_pages, full=False)
        chars = 0
        for idx in indices:
            chars += len(doc.load_page(idx).get_text("text").strip())
        return chars >= MIN_TEXT_CHARS_PER_PAGE
    finally:
        doc.close()


def _sample_page_indices(page_count: int, count: int, *, full: bool) -> list[int]:
    if page_count <= 0:
        return []
    if full or page_count <= count:
        return list(range(page_count))
    picks = {0, page_count - 1}
    while len(picks) < min(count, page_count):
        picks.add(random.randrange(page_count))
    return sorted(picks)


def _page_extract_text(doc: fitz.Document, page_index: int) -> str:
    return doc.load_page(page_index).get_text("text")


def _page_ocr_text(doc: fitz.Document, page_index: int) -> str:
    page = doc.load_page(page_index)
    pix = page.get_pixmap(dpi=RENDER_DPI)
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return pytesseract.image_to_string(image)


def ocr_diff_scan(
    pdf_path: Path,
    *,
    full: bool = False,
    sample_count: int = DEFAULT_SAMPLE_COUNT,
) -> dict[str, Any]:
    if not shutil.which("tesseract"):
        return {
            "enabled": False,
            "skipped_reason": "tesseract not found",
            "severity": "NONE",
            "pages_sampled": [],
            "hidden_by_ocr_diff": [],
        }

    pdf_path = Path(pdf_path)
    if not is_digital_pdf(pdf_path):
        return {
            "enabled": False,
            "skipped_reason": "scanned or low text density",
            "severity": "NONE",
            "pages_sampled": [],
            "hidden_by_ocr_diff": [],
        }

    doc = fitz.open(pdf_path)
    hidden_phrases: list[str] = []
    pages_sampled: list[int] = []
    try:
        indices = _sample_page_indices(doc.page_count, sample_count, full=full)
        for idx in indices:
            pages_sampled.append(idx + 1)
            extract_text = _page_extract_text(doc, idx)
            ocr_text = _page_ocr_text(doc, idx)
            extract_words = _normalize_words(extract_text)
            ocr_words = _normalize_words(ocr_text)
            diff = extract_words - ocr_words
            for word in sorted(diff):
                if len(word) >= 4:
                    hidden_phrases.append(word)
    finally:
        doc.close()

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_hidden: list[str] = []
    for item in hidden_phrases:
        if item not in seen:
            seen.add(item)
            unique_hidden.append(item)

    severity = "HIGH" if len(unique_hidden) >= 5 else ("MEDIUM" if unique_hidden else "NONE")
    return {
        "enabled": True,
        "pages_sampled": pages_sampled,
        "hidden_by_ocr_diff": unique_hidden[:100],
        "severity": severity,
    }
