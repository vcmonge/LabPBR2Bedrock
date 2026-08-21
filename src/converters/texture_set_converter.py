from __future__ import annotations

import json
from pathlib import Path

from src.models import MER_JSON_VERSION, MERS_JSON_VERSION


JSON_TEMPLATE_NAMES = {
    MER_JSON_VERSION: "1.16.100.texture_set.json",
    MERS_JSON_VERSION: "1.21.30.texture_set.json",
}


def create_texture_set_json(
    texture_name: str,
    output_dir: Path,
    template_dir: Path,
    version: str,
) -> Path:
    """Create a validated Bedrock texture set from a versioned template."""
    template_name = JSON_TEMPLATE_NAMES.get(version)
    if template_name is None:
        supported = ", ".join(sorted(JSON_TEMPLATE_NAMES))
        raise ValueError(
            f"Unsupported texture set version '{version}'. Use one of: {supported}"
        )

    template_path = template_dir / template_name
    template_text = template_path.read_text(encoding="utf-8")
    rendered_text = template_text.replace("{$nombre}", texture_name)
    json.loads(rendered_text)

    json_path = output_dir / f"{texture_name}.texture_set.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path.write_text(rendered_text, encoding="utf-8")
    return json_path
