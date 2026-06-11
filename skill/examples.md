# pdf2md Examples

## Install (macOS Apple Silicon)

```bash
cd ~/Tools/pdf2md
./scripts/install.sh
pdf2md doctor
```

## Scan only

```bash
pdf2md scan lecture.pdf
pdf2md scan lecture.pdf -o ./scan-out
```

## Convert slides (clear markdown)

```bash
pdf2md convert slides.pdf -o ./out --mode clear
```

## Convert (academic, MLX)

```bash
pdf2md convert paper.pdf -o ./out
```

## Safe mode (no MinerU GPU)

```bash
pdf2md convert untrusted.pdf -o ./out --mode safe
```

## Linux NVIDIA

```bash
./scripts/install.sh    # auto-detects CUDA → cu124/cu126 torch + vllm
pdf2md convert paper.pdf -o ./out
```

## Linux CPU only

```bash
./scripts/install.sh --cpu
pdf2md convert paper.pdf -o ./out --backend pipeline
```
