# pdf2md Reference

## CLI

```bash
pdf2md convert paper.pdf -o ./out
pdf2md scan paper.pdf
pdf2md doctor
```

### convert flags

| Flag | Description |
|---|---|
| `-o, --output` | Output directory (required) |
| `--no-ocr-diff` | Skip OCR diff layer in scan |
| `--ocr-diff-full` | OCR diff all pages (default: sample) |
| `--force` | Convert even when scan severity is HIGH |

### scan flags

| Flag | Description |
|---|---|
| `-o, --output` | Write `security_report.json` to directory |
| `--no-ocr-diff` | Skip OCR diff layer |
| `--ocr-diff-full` | OCR diff all pages (default: sample) |
| `--force` | Exit 0 even when severity is HIGH |

### Install

```bash
./scripts/install.sh          # detect platform + uv venv + MinerU
./scripts/install.sh --cpu    # Linux: force CPU profile
```

## System dependencies

- **tesseract** — OCR diff scan
- **uv** — Python environment manager
- **mineru** — installed by `scripts/install.sh`
