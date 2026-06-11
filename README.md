# pdf2md

PDF security scan + markdown conversion for agents and note pipelines.

Two-stage flow: **scan** (low-contrast + optional OCR diff) → **convert** (`academic` MinerU, `safe` OpenDataLoader, or `frontier` KDL-Frontier-Parser-nano).

## Supported platforms

| Profile | OS | GPU | Academic backend |
|---|---|---|---|
| `mac_arm` | macOS Apple Silicon | MLX | `hybrid-auto-engine` |
| `linux_gpu` | Linux | NVIDIA + CUDA | `hybrid-auto-engine` |
| `linux_cpu` | Linux | CPU | `pipeline` |

macOS Intel and Windows are not supported in v1.

## Install

Requires [uv](https://docs.astral.sh/uv/) and system **tesseract** + **java** (for safe mode).

```bash
git clone <repo> ~/Tools/pdf2md
cd ~/Tools/pdf2md
./scripts/install.sh
pdf2md doctor
```

Linux with NVIDIA but no CUDA: install prompts to add CUDA or re-run with `./scripts/install.sh --cpu`.

## Usage

```bash
# Scan + convert
pdf2md convert paper.pdf -o ./out

# Scan only
pdf2md scan paper.pdf

# Safe mode (OpenDataLoader, Java)
pdf2md convert paper.pdf -o ./out --mode safe

# Frontier mode (KDL-Frontier-Parser-nano via vLLM)
export KDL_NANO_ENDPOINT_URL=http://localhost:8000/v1
pdf2md convert paper.pdf -o ./out --mode frontier
```

Frontier mode expects a running vLLM server:

```bash
vllm serve KDLAI/KDL-Frontier-Parser-nano \
  --served-model-name kdl-frontier-parser-nano \
  --max-model-len 8192 --trust-remote-code \
  --limit-mm-per-prompt '{"image":1}'
```

Output:

```
out/
├── document.md
├── security_report.json
├── meta.json
└── images/
```

## Agent skill

See [`skill/SKILL.md`](skill/SKILL.md) for how agents should read `security_report.json`.

## Development

```bash
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

Local test PDFs belong in `test/` (gitignored).
