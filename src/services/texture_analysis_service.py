from __future__ import annotations

from pathlib import Path

from src.converters.mer_converter import (
    has_subsurface_scattering,
    is_java_specular,
)
from src.converters.normal_converter import (
    has_parallax_occlusion_mapping,
    is_java_normal,
)
from src.models import SUPPORTED_IMAGE_EXTENSIONS, TextureCapabilities

from .texture_file_collector import collect_texture_files


class TextureAnalysisService:
    """Determine which conversion features are available for a set of inputs."""

    def accepts_input_path(self, path: Path) -> bool:
        return path.is_dir() or (
            path.is_file()
            and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        )

    def collect_files(self, paths: list[Path]) -> list[Path]:
        return collect_texture_files(paths)

    def analyze(self, paths: list[Path]) -> TextureCapabilities:
        texture_files = self.collect_files(paths)
        normals = [path for path in texture_files if is_java_normal(path)]
        has_normals = bool(normals)
        speculars = [path for path in texture_files if is_java_specular(path)]
        has_speculars = bool(speculars)
        has_pom = False
        has_sss = False

        for texture_path in normals:
            try:
                if has_parallax_occlusion_mapping(texture_path):
                    has_pom = True
                    break
            except Exception:
                # Corrupt or unsupported images do not expose the POM option.
                continue

        for texture_path in speculars:
            try:
                if has_subsurface_scattering(texture_path):
                    has_sss = True
                    break
            except Exception:
                # Corrupt or unsupported images do not expose the SSS option.
                continue

        return TextureCapabilities(
            has_normals=has_normals,
            has_speculars=has_speculars,
            has_pom=has_pom,
            has_sss=has_sss,
            pom_available=has_pom,
            sss_available=has_sss,
        )
