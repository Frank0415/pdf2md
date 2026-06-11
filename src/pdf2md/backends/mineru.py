"""MinerU conversion backend."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from pdf2md.platform import MINERU_CLI_BACKEND, load_platform

DEFAULT_LANG = "en"


def convert_pdf(pdf_path: Path, output_dir: Path) -> Path:
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    load_platform()  # ensure manifest exists before conversion

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
        MINERU_CLI_BACKEND,
        "-l",
        DEFAULT_LANG,
    ]
    env = _mineru_env()
    subprocess.run(cmd, check=True, env=env)

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


def _mineru_env() -> dict[str, str]:
    """Strip SOCKS/HTTP proxy vars that break MinerU's httpx client without socksio."""
    import sys
    env = os.environ.copy()
    for key in list(env):
        if "proxy" in key.lower():
            del env[key]
    
    # Prepend the virtualenv bin directory to PATH so subprocesses can find mineru
    bin_dir = str(Path(sys.executable).parent)
    env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
    return env


def _find_markdown(root: Path) -> Path | None:
    candidates = sorted(root.rglob("*.md"), key=lambda p: len(p.parts))
    for path in candidates:
        if path.name.endswith(".md"):
            return path
    return None
