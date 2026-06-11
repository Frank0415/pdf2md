"""Structural PDF injection scan (layer A)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import fitz
import pdfplumber
from pdf_injection_scanner.scanner import (
    Finding,
    scan_offpage_text,
    scan_suspicious_patterns,
    scan_tiny_text,
)

from pdf2md.scan_contrast import scan_low_contrast_text

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
CONTRAST_RENDER_DPI = 120


def _finding_to_dict(f: Finding) -> dict[str, Any]:
    return {
        "page": f.page,
        "type": f.finding_type,
        "description": f.description,
        "content": f.content,
        "location": f.location,
        "severity": f.severity,
    }


def _max_severity(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "NONE"
    best = max(findings, key=lambda x: SEVERITY_ORDER.get(str(x.get("severity", "low")).lower(), 0))
    return str(best.get("severity", "low")).upper()


def structural_scan(pdf_path: Path) -> dict[str, Any]:
    """Structural heuristics: low-contrast, tiny, off-page, injection patterns."""
    pdf_path = Path(pdf_path)
    findings: list[Finding] = []
    page_count = 0

    doc = fitz.open(pdf_path)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            for index, page in enumerate(pdf.pages):
                page_num = index + 1
                chars = page.chars
                if not chars:
                    continue

                fitz_page = doc[index]
                pixmap = fitz_page.get_pixmap(dpi=CONTRAST_RENDER_DPI)
                findings.extend(scan_low_contrast_text(chars, page_num, pixmap, fitz_page.rect))
                findings.extend(scan_tiny_text(chars, page_num, set()))
                findings.extend(scan_offpage_text(chars, page_num, page.width, page.height))

                full_text = page.extract_text() or ""
                findings.extend(scan_suspicious_patterns(full_text, page_num))
    finally:
        doc.close()

    serialized = [_finding_to_dict(f) for f in findings]
    severity = _max_severity(serialized) if serialized else "NONE"
    return {
        "severity": severity,
        "findings": serialized,
        "pages_scanned": page_count,
    }
