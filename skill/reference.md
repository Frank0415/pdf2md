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
| `--mode academic\|safe\|frontier` | `academic`=MinerU, `safe`=OpenDataLoader, `frontier`=KDL-Frontier-Parser-nano |
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

## Frontier mode (KDL-Frontier-Parser-nano)

Requires a vLLM OpenAI-compatible endpoint:

| Env | Default | Purpose |
|---|---|---|
| `KDL_NANO_ENDPOINT_URL` | (required) | Base URL ending in `/v1` |
| `KDL_NANO_MODEL` | `kdl-frontier-parser-nano` | Served model name |
| `KDL_NANO_DPI` | `144` | PDF render DPI |
| `KDL_NANO_MAX_CONCURRENT` | `8` | Per-document request concurrency |

## System dependencies

- **tesseract** — OCR diff scan
- **java 11+** — OpenDataLoader safe mode
- **uv** — Python environment manager
- **vLLM + GPU** — Frontier mode (serve `KDLAI/KDL-Frontier-Parser-nano` separately)
