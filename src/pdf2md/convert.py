"""Stage 2: PDF to markdown conversion."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pdf2md.backends import mineru
from pdf2md.markdown_clean import clean_document_markdown
from pdf2md.platform import load_platform


def convert_pdf(pdf_path: Path, output_dir: Path) -> dict[str, Any]:
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    platform = load_platform()

    document_md = mineru.convert_pdf(pdf_path, output_dir)
    clean_document_markdown(document_md)

    meta = {
        "source_pdf": str(pdf_path),
        "converted_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.to_dict(),
        "inference": platform.inference,
        "document_md": str(document_md),
    }
    meta_path = output_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return meta
