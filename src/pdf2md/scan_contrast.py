"""Low-contrast text detection (replaces naive white-text heuristics)."""

from __future__ import annotations

import statistics
from typing import Any

import fitz
from pdf_injection_scanner.scanner import (
    Finding,
    group_chars_into_segments,
    segment_location,
    segment_text,
)

# Camouflage threshold: only flag near-invisible text (not WCAG accessibility failures).
MIN_CONTRAST_RATIO = 1.15


def _channel_linear(value: float) -> float:
    if value <= 0.03928:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def _relative_luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = (_channel_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground: tuple[float, float, float], background: tuple[float, float, float]) -> float:
    l1 = _relative_luminance(foreground)
    l2 = _relative_luminance(background)
    lighter = max(l1, l2) + 0.05
    darker = min(l1, l2) + 0.05
    return lighter / darker


def normalize_color(color: Any) -> tuple[float, float, float] | None:
    if color is None:
        return None
    if isinstance(color, (int, float)):
        value = float(color)
        return (value, value, value)
    if isinstance(color, (list, tuple)):
        if len(color) == 1:
            value = float(color[0])
            return (value, value, value)
        if len(color) == 3:
            return tuple(float(c) for c in color)  # type: ignore[return-value]
        if len(color) == 4:
            c, m, y, k = (float(v) for v in color)
            return ((1.0 - c) * (1.0 - k), (1.0 - m) * (1.0 - k), (1.0 - y) * (1.0 - k))
    return None


def _sample_background(
    pixmap: fitz.Pixmap,
    x_pdf: float,
    y_pdf: float,
    page_rect: fitz.Rect,
) -> tuple[float, float, float]:
    width = max(page_rect.width, 1.0)
    height = max(page_rect.height, 1.0)
    px = int(x_pdf * pixmap.width / width)
    py = int(y_pdf * pixmap.height / height)
    reds: list[float] = []
    greens: list[float] = []
    blues: list[float] = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ix = min(max(px + dx, 0), pixmap.width - 1)
            iy = min(max(py + dy, 0), pixmap.height - 1)
            idx = (iy * pixmap.width + ix) * 3
            reds.append(pixmap.samples[idx] / 255.0)
            greens.append(pixmap.samples[idx + 1] / 255.0)
            blues.append(pixmap.samples[idx + 2] / 255.0)
    return (statistics.median(reds), statistics.median(greens), statistics.median(blues))


def _segment_foreground(segment: list[dict[str, Any]]) -> tuple[float, float, float] | None:
    colors = [normalize_color(char.get("non_stroking_color")) for char in segment]
    colors = [color for color in colors if color is not None]
    if not colors:
        return None
    return (
        statistics.median([c[0] for c in colors]),
        statistics.median([c[1] for c in colors]),
        statistics.median([c[2] for c in colors]),
    )


def _segment_bounds(segment: list[dict[str, Any]]) -> tuple[float, float, float, float]:
    x0 = min(char.get("x0", 0.0) for char in segment)
    x1 = max(char.get("x1", 0.0) for char in segment)
    top = min(char.get("top", 0.0) for char in segment)
    bottom = max(char.get("bottom", 0.0) for char in segment)
    return x0, x1, top, bottom


def _segment_sample_points(segment: list[dict[str, Any]]) -> list[tuple[float, float]]:
    x0, x1, top, bottom = _segment_bounds(segment)
    width = max(x1 - x0, 1.0)
    height = max(bottom - top, 1.0)
    mid_x = (x0 + x1) / 2.0
    mid_y = (top + bottom) / 2.0
    return [
        (mid_x, mid_y),
        (mid_x, top - height * 0.35),
        (mid_x, bottom + height * 0.35),
        (x0 - width * 0.15, mid_y),
        (x1 + width * 0.15, mid_y),
    ]


def scan_low_contrast_text(
    chars: list[dict[str, Any]],
    page_num: int,
    pixmap: fitz.Pixmap,
    page_rect: fitz.Rect,
    *,
    min_contrast: float = MIN_CONTRAST_RATIO,
) -> list[Finding]:
    """Flag text segments whose fill color is too close to the rendered background."""
    if not chars:
        return []

    findings: list[Finding] = []
    for segment in group_chars_into_segments(chars):
        text = segment_text(segment)
        if len(text) <= 2:
            continue
        foreground = _segment_foreground(segment)
        if foreground is None:
            continue
        ratios = [
            contrast_ratio(foreground, _sample_background(pixmap, x, y, page_rect))
            for x, y in _segment_sample_points(segment)
        ]
        ratio = max(ratios)
        if ratio >= min_contrast:
            continue
        findings.append(
            Finding(
                page=page_num,
                finding_type="Low Contrast Text",
                description=(
                    f"Text/background contrast {ratio:.2f}:1 "
                    f"(below {min_contrast:.2f}:1) — likely invisible to readers"
                ),
                content=text,
                location=segment_location(segment),
                severity="high",
            )
        )
    return findings
