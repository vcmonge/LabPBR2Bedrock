from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from src.models import SUPPORTED_IMAGE_EXTENSIONS


def collect_texture_files(paths: Iterable[Path]) -> list[Path]:
    """Collect supported texture files recursively in a stable order."""
    files: list[Path] = []

    for path in paths:
        if path.is_dir():
            for child in path.rglob("*"):
                if (
                    child.is_file()
                    and child.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
                ):
                    files.append(child)
        elif (
            path.is_file()
            and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        ):
            files.append(path)

    return sorted(
        set(files),
        key=lambda file_path: (str(file_path).casefold(), str(file_path)),
    )
