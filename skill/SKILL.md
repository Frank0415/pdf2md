# pdf2md — PDF Security Scan + Markdown Conversion

Use this skill when ingesting PDFs for RAG, agents, or note-taking pipelines.

## Workflow

1. Run `pdf2md scan <file.pdf>` or `pdf2md convert <file.pdf> -o <out>/`
2. Read `security_report.json` before trusting content
3. Only proceed if `overall_severity` is not `HIGH`/`CRITICAL`, or the user explicitly approved `--force`

## Conversion

MinerU runs with the backend from `.pdf2md/platform.json` (set by `scripts/install.sh`).

| Profile | MinerU engine |
|---|---|
| `mac_arm` | `hybrid-auto-engine` (MLX) |
| `linux_gpu` | `hybrid-auto-engine` (CUDA) |
| `linux_cpu` | `pipeline` (CPU) |

## Output bundle

```
out/
├── document.md
├── security_report.json
├── meta.json
└── images/
```

## References

- [reference.md](reference.md) — CLI flags and report fields
- [examples.md](examples.md) — sample workflows
