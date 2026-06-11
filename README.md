# pdf2md

PDF security scan + markdown conversion for agents and note pipelines.

**Scan** (low-contrast + optional OCR diff) → **convert** (MinerU) → **polish** (agent, full skill mode).

---

## For humans

You are reading this README. **Ask your coding agent to install pdf2md** — paste:

> Install pdf2md from this repository. Deploy the agent skills to `~/.agents/skills/`, run the install scripts, and adapt for my platform (macOS Apple Silicon, Linux CPU, or Linux CUDA). Follow the **For agents** section in README.md exactly.

The agent handles clone, skill copy, MinerU weights, and `pdf2md doctor`.

---

## For agents

You are installing pdf2md. Execute these steps in order.

### 1. Clone (if needed)

```bash
git clone https://github.com/Frank0415/pdf2md.git ~/Tools/pdf2md
export PDF2MD_REPO=~/Tools/pdf2md
```

### 2. Deploy skills

Copy both skill packages into the agent skills directory:

```bash
bash "$PDF2MD_REPO/skill/pdf2md/scripts/deploy-skills.sh"
```

This installs:

| Destination | Source |
|---|---|
| `~/.agents/skills/pdf2md/` | `skill/pdf2md/` |
| `~/.agents/skills/pdf2md-safety/` | `skill/pdf2md-safety/` |

Each skill is self-contained: `SKILL.md`, `references/`, and `scripts/` (install, validate, platform detect, model download).

### 3. Install toolchain

**Conversion (MinerU + models)** — pick platform profile automatically:

```bash
~/.agents/skills/pdf2md/scripts/install.sh --repo "$PDF2MD_REPO"
```

| Profile | When | MinerU backend |
|---|---|---|
| `mac_arm` | macOS Apple Silicon | `hybrid-auto-engine` (MLX) |
| `linux_gpu` | Linux + NVIDIA + CUDA | `hybrid-auto-engine` (vLLM) |
| `linux_cpu` | Linux, no CUDA | `pipeline` |

Force CPU on Linux: `.../install.sh --repo "$PDF2MD_REPO" --cpu`

**Scan-only** (no MinerU, no model download):

```bash
~/.agents/skills/pdf2md-safety/scripts/install.sh --repo "$PDF2MD_REPO"
```

If full install already ran, scan-only is satisfied — skip unless you need a lightweight venv without MinerU.

### 4. Verify

```bash
pdf2md doctor
```

### 5. Use skills

| Skill | Command | Post-CLI |
|---|---|---|
| `pdf2md` (default **full**) | `pdf2md convert file.pdf -o ./out` | Agent polishes `document.md` |
| `pdf2md` **lite** (`/pdf2md lite`) | same CLI | Use `document.md` as-is |
| `pdf2md-safety` | `pdf2md scan file.pdf -o ./scan-out` | Report only |

Read each skill's `SKILL.md` under `~/.agents/skills/` before running workflows.

---

## Usage

```bash
pdf2md convert paper.pdf -o ./out
pdf2md scan paper.pdf -o ./scan-out
pdf2md doctor
```

Output (convert):

```
out/
├── document.md
├── security_report.json
├── meta.json
└── images/
```

## Skill layout

```
skill/pdf2md/
├── SKILL.md
├── references/
└── scripts/
    ├── install.sh           # full install + MinerU weights
    ├── detect-platform.sh   # mac_arm | linux_cpu | linux_gpu
    ├── download-models.sh
    ├── deploy-skills.sh
    └── validate_bundle.py

skill/pdf2md-safety/
├── SKILL.md
├── references/
└── scripts/
    ├── install.sh           # scan-only CLI
    └── validate_report.py
```

## Development

```bash
cd "$PDF2MD_REPO"
./scripts/install.sh
uv pip install -e ".[dev]"
pytest
```

Local test PDFs live in `test/` (gitignored).
