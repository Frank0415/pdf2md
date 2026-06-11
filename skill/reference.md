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
| `--mode academic\|safe` | Conversion backend (default: academic) |
| `--backend pipeline\|hybrid-auto-engine` | Override MinerU engine |
| `--lang en` | OCR language hint for MinerU |
| `--no-ocr-diff` | Skip OCR diff layer in scan |
| `--ocr-diff-full` | OCR diff all pages (default: sample) |
| `--force` | Convert even when scan severity is HIGH |

### Install

```bash
./scripts/install.sh          # detect platform + uv venv + deps
./scripts/install.sh --cpu    # Linux: force CPU profile
./scripts/install.sh --redetect
```

## platform.json fields

| Field | Meaning |
|---|---|
| `profile` | `mac_arm`, `linux_cpu`, `linux_gpu` |
| `gpu_backend` | `mlx`, `nvidia`, `cpu` |
| `mineru_backend` | Default MinerU `-b` value |
| `cuda_version` | Auto-detected on `linux_gpu` |
| `torch_index` | PyTorch wheel tag (e.g. `cu124`) |

## System dependencies

- **tesseract** — OCR diff scan
- **java 11+** — OpenDataLoader safe mode
- **uv** — Python environment manager
