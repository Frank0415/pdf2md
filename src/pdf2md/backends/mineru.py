"""MinerU conversion backend."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from pdf2md.platform import load_platform, resolve_mineru_backend


def convert_pdf(
    pdf_path: Path,
    output_dir: Path,
    *,
    mode: str = "academic",
    backend_override: str | None = None,
    lang: str = "en",
) -> Path:
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    platform = load_platform()
    backend = resolve_mineru_backend(mode, override=backend_override, platform=platform)

    mineru_out = output_dir / "_mineru"
    if mineru_out.exists():
        shutil.rmtree(mineru_out)
    mineru_out.mkdir(parents=True, exist_ok=True)

    cmd = [
        "mineru",
        "-p",
        str(pdf_path),
        "-o",
        str(mineru_out),
        "-b",
        backend,
        "-l",
        lang,
    ]
    subprocess.run(cmd, check=True)

    md_path = _find_markdown(mineru_out)
    if md_path is None:
        raise RuntimeError(f"MinerU produced no markdown under {mineru_out}")

    document_md = output_dir / "document.md"
    document_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")

    images_src = md_path.parent / "images"
    images_dst = output_dir / "images"
    if images_src.is_dir():
        if images_dst.exists():
            shutil.rmtree(images_dst)
        shutil.copytree(images_src, images_dst)
    else:
        images_dst.mkdir(exist_ok=True)

    return document_md


def _find_markdown(root: Path) -> Path | None:
    candidates = sorted(root.rglob("*.md"), key=lambda p: len(p.parts))
    for path in candidates:
        if path.name.endswith(".md"):
            return path
    return None
