# pdf2md

PDF security scan + markdown conversion for agents and note pipelines.

Two-stage flow: **scan** (low-contrast + optional OCR diff) → **convert** (MinerU).

## Supported platforms

| Profile | OS | GPU | MinerU backend |
|---|---|---|---|
| `mac_arm` | macOS Apple Silicon | MLX | `hybrid-auto-engine` |
| `linux_gpu` | Linux | NVIDIA + CUDA | `hybrid-auto-engine` |
| `linux_cpu` | Linux | CPU | `pipeline` |

## Install

Requires [uv](https://docs.astral.sh/uv/) and system **tesseract**.

```bash
git clone <repo> ~/Tools/pdf2md
cd ~/Tools/pdf2md
./scripts/install.sh
pdf2md doctor
```

Linux with NVIDIA but no CUDA: install prompts to add CUDA or re-run with `./scripts/install.sh --cpu`.

## Usage

```bash
pdf2md convert paper.pdf -o ./out
pdf2md scan paper.pdf
pdf2md doctor
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
