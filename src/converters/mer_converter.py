# Portions of the conversion logic in this module were adapted from
# JE2BE Resource Pack Converter.
# Copyright (c) 2025 JE2BE Team
# Licensed under the MIT License.
# See THIRD_PARTY_LICENSES.md.

"""Convert LabPBR specular maps into Bedrock MER or MERS textures.

LabPBR packs smoothness, F0/metal ID, subsurface scattering, and emission into
the R, G, B, and A channels of an ``*_s`` texture. Bedrock expects metalness,
emission, and roughness in RGB. texture-set format 1.21.30 can additionally
store subsurface scattering in alpha (MERS).

The conversion tables in this module precompute every possible uint8 mapping.
Applying those tables to whole NumPy channel arrays keeps the pixel conversion
both fast and numerically consistent.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from src.models import SUPPORTED_IMAGE_EXTENSIONS

# LabPBR values 0..65 in the blue channel are reserved for porosity. Values
# above 65 represent SSS and are remapped to Bedrock's full 0..255 range.
SSS_MIN_VALUE = 65
SSS_VALUE_RANGE = 255 - SSS_MIN_VALUE

# LabPBR uses green values 0..229 for dielectric F0 and 230..255 for metal IDs.
# Bedrock only needs a binary metalness channel for this conversion.
METAL_ID_MIN_VALUE = 230

# Alpha 255 means "no emission" in LabPBR. The remaining 0..254 values span
# the emission range and therefore need normalization to Bedrock's 0..255.
EMISSION_MAX_VALUE = 254


def _create_roughness_lut() -> np.ndarray:
    """Map all LabPBR smoothness values to perceptual Bedrock roughness.

    LabPBR stores perceptual smoothness, while Bedrock stores roughness. The
    conversion is ``roughness = (1 - smoothness / 255) ** 2 * 255``.
    ``np.rint`` preserves the converter's defined nearest-integer behavior.
    """
    smoothness = np.arange(256, dtype=np.float64)
    roughness_linear = (1.0 - smoothness / 255.0) ** 2
    return np.clip(np.rint(roughness_linear * 255.0), 0, 255).astype(np.uint8)


def _create_emissive_lut() -> np.ndarray:
    """Map LabPBR emission values 0..254 to Bedrock's full uint8 range.

    Index 255 remains zero because LabPBR reserves it as the no-emission value.
    """
    emissive = np.zeros(256, dtype=np.uint8)
    emission = np.arange(EMISSION_MAX_VALUE + 1, dtype=np.float64)
    emissive[: EMISSION_MAX_VALUE + 1] = np.rint(
        emission * 255.0 / EMISSION_MAX_VALUE
    ).astype(np.uint8)
    return emissive


def _create_sss_lut() -> np.ndarray:
    """Map LabPBR SSS values 66..255 to Bedrock alpha values 1..255.

    Values through 65 remain zero because they belong to LabPBR's porosity
    range rather than its subsurface-scattering range.
    """
    sss = np.zeros(256, dtype=np.uint8)
    subsurface = np.arange(SSS_MIN_VALUE + 1, 256, dtype=np.float64)
    sss[SSS_MIN_VALUE + 1 :] = np.rint(
        (subsurface - SSS_MIN_VALUE) * 255.0 / SSS_VALUE_RANGE
    ).astype(np.uint8)
    return sss


# These shared lookup tables are built once at import time, treated as
# read-only, and then indexed by complete image channels during conversion.
ROUGHNESS_LUT = _create_roughness_lut()
METALNESS_LUT = np.zeros(256, dtype=np.uint8)
METALNESS_LUT[METAL_ID_MIN_VALUE:] = 255
EMISSIVE_LUT = _create_emissive_lut()
SSS_LUT = _create_sss_lut()


def is_java_specular(path: Path) -> bool:
    """Return whether *path* has a supported extension and an ``_s`` suffix."""
    return (
        path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        and path.stem.lower().endswith("_s")
    )


def texture_base_name(path: Path) -> str:
    """Return the texture name preceding a valid Java ``_s`` suffix."""
    if not is_java_specular(path):
        raise ValueError(f"Texture is not a Java specular map: {path}")
    return path.stem[:-2]


def _channels_have_sss(
    blue_channel: np.ndarray,
    f0_metal_channel: np.ndarray,
) -> bool:
    """Return whether any non-metal pixel carries an effective SSS value."""
    return bool(
        np.any(
            (blue_channel > SSS_MIN_VALUE)
            & (f0_metal_channel < METAL_ID_MIN_VALUE)
        )
    )


def has_subsurface_scattering(specular_path: Path) -> bool:
    """Inspect a LabPBR specular map for effective subsurface scattering.

    Metal pixels cannot carry SSS, and blue values through 65 encode porosity,
    so neither makes SSS available to the converter.
    """
    with Image.open(specular_path) as specular_img:
        spec_array = np.asarray(specular_img.convert("RGB"))
        return _channels_have_sss(
            spec_array[:, :, 2],
            spec_array[:, :, 1],
        )


def convert_specular_to_mer(
    specular_path: Path,
    output_dir: Path,
    sss_enabled: bool = False,
) -> Path:
    """Convert one LabPBR ``*_s`` texture to a Bedrock MER or MERS map.

    The output channel mapping is:

    * R: binary metalness derived from the LabPBR green-channel metal IDs.
    * G: normalized emission derived from LabPBR alpha.
    * B: roughness derived from LabPBR red-channel smoothness.
    * A: normalized SSS from LabPBR blue, only when enabled and present.

    Effective SSS produces a 32-bit RGBA ``*_mers.tga``. Otherwise the result
    is an RGB ``*_mer.png``, even when SSS was enabled for the surrounding
    batch. The decision is deliberately made for each individual texture.
    """
    base_name = texture_base_name(specular_path)

    with Image.open(specular_path) as specular_img:
        if specular_img.mode != "RGBA":
            specular_img = specular_img.convert("RGBA")

        spec_array = np.array(specular_img)
        # Name the LabPBR source channels by meaning before repacking them into
        # Bedrock's different channel layout.
        smoothness = spec_array[:, :, 0]
        f0_metal = spec_array[:, :, 1]
        subsurface = spec_array[:, :, 2]
        emission = spec_array[:, :, 3]

        # LUT indexing returns a new array, so zeroing SSS on metal pixels does
        # not mutate the shared lookup table.
        sss_alpha = None
        if sss_enabled:
            sss_alpha = SSS_LUT[subsurface]
            sss_alpha[f0_metal >= METAL_ID_MIN_VALUE] = 0

        # Do not emit an RGBA MERS file merely because the option is enabled;
        # the source texture must contain at least one effective SSS pixel.
        use_sss = sss_alpha is not None and bool(np.any(sss_alpha))
        channel_count = 4 if use_sss else 3

        mer_array = np.empty(
            (spec_array.shape[0], spec_array.shape[1], channel_count),
            dtype=np.uint8,
        )

        mer_array[:, :, 0] = METALNESS_LUT[f0_metal]
        mer_array[:, :, 1] = EMISSIVE_LUT[emission]
        mer_array[:, :, 2] = ROUGHNESS_LUT[smoothness]

        if use_sss:
            mer_array[:, :, 3] = sss_alpha
            mer_path = output_dir / f"{base_name}_mers.tga"
            output_format = "TGA"
        else:
            mer_path = output_dir / f"{base_name}_mer.png"
            output_format = "PNG"

        output_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(mer_array).save(mer_path, format=output_format)

    return mer_path
