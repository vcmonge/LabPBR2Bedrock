# Portions of the conversion logic in this module were adapted from
# JE2BE Resource Pack Converter.
# Copyright (c) 2025 JE2BE Team
# Licensed under the MIT License.
# See THIRD_PARTY_LICENSES.md.

"""Convert LabPBR normal maps into Bedrock RGB normal/height textures.

LabPBR stores the encoded X and Y normal components in red and green, ambient
occlusion in blue, and optional POM height in alpha. Bedrock instead uses red
and green for X/Y and blue for either the reconstructed Z component or POM
height. Consequently, the source blue channel is intentionally not preserved.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from src.models import SUPPORTED_IMAGE_EXTENSIONS

NORMAL_SUFFIXES = ("_normal", "_n")


def _create_normal_z_lut() -> np.ndarray:
    """Precompute encoded positive-Z values for every uint8 X/Y pair.

    X and Y are decoded from 0..255 to -1..1. For a unit normal, the positive
    hemisphere component is ``z = sqrt(max(0, 1 - x**2 - y**2))``. Clamping
    the radicand handles invalid X/Y pairs outside the unit circle without
    producing NaNs. Z is then encoded back into the 0..255 channel range.

    The returned table is indexed as ``NORMAL_Z_LUT[y, x]``.
    """
    values = np.arange(256, dtype=np.float64)
    normalized = (values / 255.0) * 2.0 - 1.0

    normal_x = normalized[None, :]
    normal_y = normalized[:, None]
    normal_z_squared = 1.0 - (normal_x**2 + normal_y**2)
    normal_z = np.sqrt(np.maximum(0.0, normal_z_squared))
    encoded_z = (normal_z + 1.0) * 127.5

    return np.clip(np.rint(encoded_z), 0, 255).astype(np.uint8)


# Computing all 65,536 X/Y combinations once avoids square roots per image.
NORMAL_Z_LUT = _create_normal_z_lut()


def java_normal_suffix(path: Path) -> str | None:
    """Return a supported Java normal-map suffix, matched case-insensitively."""
    if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        return None

    stem = path.stem.casefold()
    for suffix in NORMAL_SUFFIXES:
        if stem.endswith(suffix):
            return suffix
    return None


def is_java_normal(path: Path) -> bool:
    """Return whether *path* is a supported ``*_n`` or ``*_normal`` texture."""
    return java_normal_suffix(path) is not None


def _alpha_channel_has_pom(alpha_channel: np.ndarray) -> bool:
    """Return whether any alpha value represents POM height information."""
    return bool(np.any(alpha_channel < 255))


def has_parallax_occlusion_mapping(normal_path: Path) -> bool:
    """Return whether a LabPBR normal map contains POM height information.

    Any alpha value below 255 counts as height data. Formats without alpha are
    converted to RGBA, which gives every pixel an opaque alpha of 255 and thus
    correctly reports that POM is absent.
    """
    with Image.open(normal_path) as normal_img:
        if normal_img.mode in ("RGBA", "LA"):
            alpha_channel = normal_img.getchannel("A")
        else:
            alpha_channel = normal_img.convert("RGBA").getchannel("A")

        minimum_alpha, _ = alpha_channel.getextrema()
        return minimum_alpha < 255


def normal_texture_base_name(path: Path) -> str:
    """Return the texture name preceding a valid Java normal-map suffix."""
    suffix = java_normal_suffix(path)
    if suffix is None:
        raise ValueError(f"Texture is not a Java normal map: {path}")
    return path.stem[: -len(suffix)]


def convert_normal_to_bedrock(
    normal_path: Path,
    output_dir: Path,
    pom_enabled: bool = False,
) -> Path:
    """Convert one Java LabPBR normal map to a Bedrock RGB normal map.

    Red and green preserve the encoded X/Y components. When POM is enabled and
    the individual texture has non-opaque alpha, its height values replace the
    output blue channel. Otherwise blue receives a reconstructed positive Z
    component from ``NORMAL_Z_LUT``. This per-texture check lets mixed batches
    use POM only where height data actually exists.
    """
    base_name = normal_texture_base_name(normal_path)
    output_path = output_dir / f"{base_name}_normal.png"

    with Image.open(normal_path) as normal_img:
        if pom_enabled:
            # RGBA conversion also supplies alpha=255 for sources without an
            # alpha channel, making the per-texture POM check uniform.
            converted = normal_img.convert("RGBA")
            normal_array = np.asarray(converted)
            alpha_channel = normal_array[:, :, 3]
            use_pom = _alpha_channel_has_pom(alpha_channel)

            # Start by preserving X/Y. LabPBR blue contains ambient occlusion,
            # but Bedrock blue must contain height or reconstructed normal Z.
            bedrock_normal = normal_array[:, :, :3].copy()
            if use_pom:
                bedrock_normal[:, :, 2] = alpha_channel
            else:
                bedrock_normal[:, :, 2] = NORMAL_Z_LUT[
                    normal_array[:, :, 1],
                    normal_array[:, :, 0],
                ]
        else:
            converted = normal_img.convert("RGB")
            normal_array = np.asarray(converted)
            bedrock_normal = normal_array.copy()
            # The LUT uses [y, x] because rows correspond to green/Y and
            # columns correspond to red/X.
            bedrock_normal[:, :, 2] = NORMAL_Z_LUT[
                normal_array[:, :, 1],
                normal_array[:, :, 0],
            ]

        output_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(bedrock_normal, mode="RGB").save(output_path)

    return output_path
