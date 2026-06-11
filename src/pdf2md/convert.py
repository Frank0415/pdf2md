"""Stage 2: PDF to markdown conversion."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pdf2md.backends import kdl_frontier, mineru, opendataloader
from pdf2md.markdown_clean import clean_document_markdown
from pdf2md.platform import load_platform

Mode = Literal["academic", "safe", "frontier"]


def convert_pdf(
    pdf_path: Path,
    output_dir: Path,
    *,
    mode: Mode = "academic",
    backend_override: str | None = None,
    lang: str = "en",
) -> dict[str, Any]:
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    platform = load_platform()
    if mode == "safe":
        document_md = opendataloader.convert_pdf(pdf_path, output_dir)
        mineru_backend = None
        kdl_endpoint = None
    elif mode == "frontier":
        document_md = kdl_frontier.convert_pdf(pdf_path, output_dir)
        mineru_backend = None
        kdl_endpoint = os.getenv("KDL_NANO_ENDPOINT_URL")
    else:
        document_md = mineru.convert_pdf(
            pdf_path,
            output_dir,
            mode=mode,
            backend_override=backend_override,
            lang=lang,
        )
        mineru_backend = platform.mineru_backend if backend_override is None else backend_override
        kdl_endpoint = None

    if mode != "frontier":
        clean_document_markdown(document_md)

    meta = {
        "source_pdf": str(pdf_path),
        "mode": mode,
        "converted_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.to_dict(),
        "mineru_backend": mineru_backend,
        "kdl_endpoint": kdl_endpoint,
        "document_md": str(document_md),
    }
    meta_path = output_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return meta
