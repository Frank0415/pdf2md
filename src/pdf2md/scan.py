"""Structural PDF injection scan (layer A)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pdfplumber
from pdf_injection_scanner.scanner import Finding, scan_page

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


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
    """Run pdf-injection-scanner heuristics over all pages."""
    pdf_path = Path(pdf_path)
    findings: list[Finding] = []
    page_count = 0
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        for index, page in enumerate(pdf.pages):
            findings.extend(scan_page(page, index + 1))

    serialized = [_finding_to_dict(f) for f in findings]
    severity = _max_severity(serialized) if serialized else "NONE"
    return {
        "severity": severity,
        "findings": serialized,
        "pages_scanned": page_count,
    }
