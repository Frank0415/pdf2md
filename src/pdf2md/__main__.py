"""pdf2md CLI."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from pdf2md import __version__
from pdf2md.convert import convert_pdf
from pdf2md.pipeline import run_scan, should_block, write_security_report
from pdf2md.platform import MANIFEST_PATH, load_platform


def _cmd_scan(args: argparse.Namespace) -> int:
    report = run_scan(
        Path(args.pdf),
        ocr_diff=not args.no_ocr_diff,
        ocr_diff_full=args.ocr_diff_full,
    )
    if args.output:
        write_security_report(report, Path(args.output))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if should_block(report) and not args.force:
        print("Scan severity HIGH — use --force to proceed with conversion.", file=sys.stderr)
        return 2
    return 0


def _cmd_convert(args: argparse.Namespace) -> int:
    pdf_path = Path(args.pdf)
    output_dir = Path(args.output)
    report = run_scan(
        pdf_path,
        ocr_diff=not args.no_ocr_diff,
        ocr_diff_full=args.ocr_diff_full,
    )
    write_security_report(report, output_dir)
    if should_block(report) and not args.force:
        print("Blocked: security scan severity HIGH. Re-run with --force to convert anyway.", file=sys.stderr)
        return 2

    convert_pdf(
        pdf_path,
        output_dir,
        mode=args.mode,
        backend_override=args.backend,
        lang=args.lang,
    )
    print(f"Wrote {output_dir / 'document.md'}")
    return 0


def _cmd_doctor(_args: argparse.Namespace) -> int:
    ok = True
    print(f"pdf2md {__version__}")

    try:
        platform = load_platform()
        print(json.dumps(platform.to_dict(), indent=2))
    except Exception as exc:  # noqa: BLE001
        print(f"platform: ERROR — {exc}")
        ok = False

    if MANIFEST_PATH.is_file():
        print(f"manifest: {MANIFEST_PATH}")
    else:
        print(f"manifest: missing ({MANIFEST_PATH}) — run scripts/install.sh")
        ok = False

    for cmd in ("tesseract", "java", "mineru"):
        if shutil.which(cmd):
            print(f"  ok: {cmd}")
        else:
            print(f"  missing: {cmd}")
            if cmd in ("tesseract", "java"):
                ok = False

    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.check_output(["nvidia-smi", "-L"], text=True)
            print(out.strip())
        except subprocess.CalledProcessError:
            pass

    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pdf2md", description="PDF security scan and markdown conversion")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Run security scan only")
    scan.add_argument("pdf", type=Path)
    scan.add_argument("-o", "--output", type=Path, help="Write security_report.json to directory")
    scan.add_argument("--no-ocr-diff", action="store_true")
    scan.add_argument("--ocr-diff-full", action="store_true")
    scan.add_argument("--force", action="store_true", help="Exit 0 even when severity is HIGH")
    scan.set_defaults(func=_cmd_scan)

    convert = sub.add_parser("convert", help="Scan then convert to markdown")
    convert.add_argument("pdf", type=Path)
    convert.add_argument("-o", "--output", type=Path, required=True)
    convert.add_argument("--mode", choices=["academic", "safe"], default="academic")
    convert.add_argument("--backend", choices=["pipeline", "hybrid-auto-engine"])
    convert.add_argument("--lang", default="en")
    convert.add_argument("--no-ocr-diff", action="store_true")
    convert.add_argument("--ocr-diff-full", action="store_true")
    convert.add_argument("--force", action="store_true")
    convert.set_defaults(func=_cmd_convert)

    doctor = sub.add_parser("doctor", help="Check install and platform")
    doctor.set_defaults(func=_cmd_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
