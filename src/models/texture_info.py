from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_IMAGE_EXTENSIONS = frozenset({".png", ".tga"})


@dataclass(frozen=True)
class TextureCapabilities:
    has_normals: bool = False
    has_speculars: bool = False
    has_sss: bool = False
    pom_available: bool = False
    sss_available: bool = False
    has_pom: bool = False
