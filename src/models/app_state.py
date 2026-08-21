from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .conversion_options import MER_JSON_VERSION


@dataclass
class AppState:
    """Mutable state owned by the converter ViewModel."""

    input_paths: list[Path] = field(default_factory=list)
    output_dir: Path | None = None
    generate_json: bool = False
    json_version: str = MER_JSON_VERSION
    pom_enabled: bool = False
    sss_enabled: bool = False
