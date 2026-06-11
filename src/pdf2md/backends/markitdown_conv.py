"""MarkItDown clear-text conversion backend (pdfplumber/pdfminer)."""

from __future__ import annotations

from pathlib import Path

from markitdown import MarkItDown


def convert_pdf(pdf_path: Path, output_dir: Path) -> Path:
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    result = MarkItDown().convert(str(pdf_path))
    text = (result.text_content or "").strip()
    if not text:
        raise RuntimeError(f"MarkItDown produced empty output for {pdf_path}")

    document_md = output_dir / "document.md"
    document_md.write_text(text + "\n", encoding="utf-8")
    (output_dir / "images").mkdir(exist_ok=True)
    return document_md
