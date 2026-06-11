"""OpenDataLoader safe-mode conversion backend."""

from __future__ import annotations

import shutil
from pathlib import Path

import opendataloader_pdf


def convert_pdf(pdf_path: Path, output_dir: Path) -> Path:
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    work_dir = output_dir / "_opendataloader"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    opendataloader_pdf.convert(
        input_path=[str(pdf_path)],
        output_dir=str(work_dir),
        format="markdown",
        quiet=True,
    )

    stem = pdf_path.stem
    candidates = [
        work_dir / f"{stem}.md",
        work_dir / f"{pdf_path.name}.md",
    ]
    candidates.extend(work_dir.glob("*.md"))

    md_src = next((p for p in candidates if p.is_file()), None)
    if md_src is None:
        raise RuntimeError(f"OpenDataLoader produced no markdown under {work_dir}")

    document_md = output_dir / "document.md"
    document_md.write_text(md_src.read_text(encoding="utf-8"), encoding="utf-8")
    (output_dir / "images").mkdir(exist_ok=True)
    return document_md
