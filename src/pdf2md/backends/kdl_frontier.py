"""KDL-Frontier-Parser-nano conversion backend (vLLM endpoint)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from pdf2md.backends.kdl_frontier_engine import (
    KdlFrontierConfigError,
    KdlFrontierError,
    load_page_images,
    parse_document,
)


def convert_pdf(
    pdf_path: Path,
    output_dir: Path,
    *,
    endpoint_url: str | None = None,
    model: str | None = None,
    dpi: int | None = None,
) -> Path:
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    endpoint = (
        endpoint_url
        or os.getenv("KDL_NANO_ENDPOINT_URL")
        or ""
    ).rstrip("/")
    if not endpoint:
        raise KdlFrontierConfigError(
            "KDL_NANO_ENDPOINT_URL is required. Serve KDLAI/KDL-Frontier-Parser-nano "
            "with vLLM and set the OpenAI-compatible base URL (e.g. http://localhost:8000/v1)."
        )

    page_images = load_page_images(pdf_path, dpi=dpi)
    if not page_images:
        raise KdlFrontierError(f"Failed to render pages from {pdf_path}")

    markdown = parse_document(
        page_images,
        endpoint_url=endpoint,
        model=model,
    )

    document_md = output_dir / "document.md"
    document_md.write_text(markdown, encoding="utf-8")
    (output_dir / "images").mkdir(exist_ok=True)

    meta = {
        "backend": "kdl_frontier_nano",
        "endpoint_url": endpoint,
        "model": model or os.getenv("KDL_NANO_MODEL", "kdl-frontier-parser-nano"),
        "dpi": int(dpi or os.getenv("KDL_NANO_DPI", "144")),
        "page_count": len(page_images),
    }
    (output_dir / "kdl_frontier_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n",
        encoding="utf-8",
    )
    return document_md
