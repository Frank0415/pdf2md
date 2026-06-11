"""Load platform manifest written at install time."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _find_repo_root() -> Path:
    """Locate project root (pyproject.toml) for editable and src installs."""
    starts = [Path.cwd(), Path(__file__).resolve().parent]
    seen: set[Path] = set()
    for start in starts:
        path = start.resolve()
        for _ in range(8):
            if path in seen:
                break
            seen.add(path)
            if (path / "pyproject.toml").is_file() and (path / "src" / "pdf2md").is_dir():
                return path
            if (path / ".pdf2md" / "platform.json").is_file():
                return path
            if path.parent == path:
                break
            path = path.parent
    fallback = Path(__file__).resolve().parents[2]
    if (fallback / "pyproject.toml").is_file():
        return fallback
    return Path.cwd()


REPO_ROOT = _find_repo_root()
MANIFEST_PATH = REPO_ROOT / ".pdf2md" / "platform.json"

VALID_PROFILES = frozenset({"mac_arm", "linux_cpu", "linux_gpu"})
VALID_BACKENDS = frozenset({"pipeline", "hybrid-auto-engine"})


@dataclass(frozen=True)
class PlatformInfo:
    profile: str
    os: str
    arch: str
    gpu_backend: str
    mineru_backend: str
    mineru_extras: list[str]
    cuda_detected: bool = False
    cuda_version: str | None = None
    torch_index: str | None = None
    detected_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "profile": self.profile,
            "os": self.os,
            "arch": self.arch,
            "gpu_backend": self.gpu_backend,
            "mineru_backend": self.mineru_backend,
            "mineru_extras": self.mineru_extras,
            "cuda_detected": self.cuda_detected,
        }
        if self.cuda_version:
            data["cuda_version"] = self.cuda_version
        if self.torch_index:
            data["torch_index"] = self.torch_index
        if self.detected_at:
            data["detected_at"] = self.detected_at
        return data


def _parse_manifest(data: dict[str, Any]) -> PlatformInfo:
    profile = data["profile"]
    if profile not in VALID_PROFILES:
        raise ValueError(f"Unknown profile in manifest: {profile}")
    backend = data.get("mineru_backend", "pipeline")
    if backend not in VALID_BACKENDS:
        raise ValueError(f"Unknown mineru_backend in manifest: {backend}")
    return PlatformInfo(
        profile=profile,
        os=data["os"],
        arch=data["arch"],
        gpu_backend=data.get("gpu_backend", "cpu"),
        mineru_backend=backend,
        mineru_extras=list(data.get("mineru_extras", ["core"])),
        cuda_detected=bool(data.get("cuda_detected", False)),
        cuda_version=data.get("cuda_version"),
        torch_index=data.get("torch_index"),
        detected_at=data.get("detected_at"),
    )


def _probe_runtime() -> PlatformInfo:
    """Lightweight fallback when manifest is missing."""
    import platform
    import sys

    system = sys.platform
    machine = platform.machine()
    arch = "arm64" if machine in {"arm64", "aarch64"} else machine

    if system == "darwin" and arch == "arm64":
        return PlatformInfo(
            profile="mac_arm",
            os="darwin",
            arch="arm64",
            gpu_backend="mlx",
            mineru_backend="hybrid-auto-engine",
            mineru_extras=["core", "mlx"],
            detected_at=datetime.now(timezone.utc).isoformat(),
        )

    has_nvidia = False
    try:
        subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        has_nvidia = True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    if system == "linux" and has_nvidia:
        return PlatformInfo(
            profile="linux_gpu",
            os="linux",
            arch=arch,
            gpu_backend="nvidia",
            mineru_backend="hybrid-auto-engine",
            mineru_extras=["core", "vllm"],
            cuda_detected=True,
            detected_at=datetime.now(timezone.utc).isoformat(),
        )

    return PlatformInfo(
        profile="linux_cpu",
        os="linux" if system.startswith("linux") else system,
        arch=arch,
        gpu_backend="cpu",
        mineru_backend="pipeline",
        mineru_extras=["core"],
        detected_at=datetime.now(timezone.utc).isoformat(),
    )


def load_platform(*, allow_probe: bool = True) -> PlatformInfo:
    if MANIFEST_PATH.is_file():
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return _parse_manifest(data)
    if allow_probe:
        return _probe_runtime()
    raise FileNotFoundError(
        f"Platform manifest not found at {MANIFEST_PATH}. Run scripts/install.sh first."
    )


def resolve_mineru_backend(
    mode: str,
    *,
    override: str | None = None,
    platform: PlatformInfo | None = None,
) -> str:
    if override:
        if override not in VALID_BACKENDS:
            raise ValueError(f"Invalid backend override: {override}")
        return override
    info = platform or load_platform()
    if mode == "safe":
        return "pipeline"
    return info.mineru_backend
