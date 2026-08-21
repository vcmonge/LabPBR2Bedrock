from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class ConvertedTexture:
    source: Path
    output_path: Path
    texture_type: Literal["specular", "normal"]
    json_path: Path | None


@dataclass(frozen=True)
class ConversionSummary:
    converted: list[ConvertedTexture]
    ignored: list[Path]
    errors: list[str]
