"""Pipeline orchestration for scan stage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pdf2md.scan import SEVERITY_ORDER, structural_scan
from pdf2md.scan_ocr_diff import ocr_diff_scan

BLOCKING_SEVERITIES = frozenset({"HIGH", "CRITICAL"})


def _overall_severity(*parts: str) -> str:
    best = 0
    label = "NONE"
    for part in parts:
        key = part.upper()
        score = SEVERITY_ORDER.get(key.lower(), 0)
        if score > best:
            best = score
            label = key if key != "NONE" else "NONE"
    return label if best > 0 else "NONE"


def run_scan(
    pdf_path: Path,
    *,
    ocr_diff: bool = True,
    ocr_diff_full: bool = False,
) -> dict[str, Any]:
    pdf_path = Path(pdf_path)
    structural = structural_scan(pdf_path)

    if ocr_diff:
        ocr_diff_result = ocr_diff_scan(pdf_path, full=ocr_diff_full)
    else:
        ocr_diff_result = {
            "enabled": False,
            "skipped_reason": "disabled by flag",
            "severity": "NONE",
            "pages_sampled": [],
            "hidden_by_ocr_diff": [],
        }

    overall = _overall_severity(structural.get("severity", "NONE"), ocr_diff_result.get("severity", "NONE"))
    return {
        "structural": structural,
        "ocr_diff": ocr_diff_result,
        "overall_severity": overall,
    }


def should_block(report: dict[str, Any]) -> bool:
    return report.get("overall_severity", "NONE").upper() in BLOCKING_SEVERITIES


def write_security_report(report: dict[str, Any], output_dir: Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "security_report.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
