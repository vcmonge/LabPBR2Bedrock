from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from src.converters.mer_converter import (
    convert_specular_to_mer,
    is_java_specular,
    texture_base_name,
)
from src.converters.normal_converter import (
    convert_normal_to_bedrock,
    is_java_normal,
    java_normal_suffix,
    normal_texture_base_name,
)
from src.converters.texture_set_converter import create_texture_set_json
from src.models import (
    MER_JSON_VERSION,
    MERS_JSON_VERSION,
    SUPPORTED_JSON_VERSIONS,
    ConvertedTexture,
    ConversionOptions,
    ConversionSummary,
)

from .texture_file_collector import collect_texture_files


_TextureType = Literal["specular", "normal"]


@dataclass
class _TextureGroup:
    base_name: str
    specular_candidates: list[Path]
    normal_candidates: list[Path]


class ConversionService:
    """Orchestrate a complete texture conversion."""

    def convert(
        self,
        input_paths: list[Path],
        output_dir: Path,
        template_dir: Path,
        options: ConversionOptions,
    ) -> ConversionSummary:
        texture_files = collect_texture_files(input_paths)
        converted: list[ConvertedTexture] = []
        ignored: list[Path] = []
        errors: list[str] = []
        groups = self._group_textures(texture_files, ignored)

        for group in groups.values():
            selected_paths = self._select_group_paths(group, ignored)
            successful_conversions = self._convert_group(
                selected_paths,
                output_dir,
                options,
                errors,
            )
            if not successful_conversions:
                continue

            json_path = self._create_group_json(
                group,
                successful_conversions,
                output_dir,
                template_dir,
                options,
                errors,
            )
            converted.extend(
                ConvertedTexture(
                    source=source,
                    output_path=output_path,
                    texture_type=texture_type,
                    json_path=json_path,
                )
                for source, output_path, texture_type in successful_conversions
            )

        ignored.sort(key=lambda path: (str(path).casefold(), str(path)))
        return ConversionSummary(
            converted=converted,
            ignored=ignored,
            errors=errors,
        )

    @staticmethod
    def _group_textures(
        texture_files: list[Path],
        ignored: list[Path],
    ) -> dict[str, _TextureGroup]:
        groups: dict[str, _TextureGroup] = {}

        for texture_path in texture_files:
            if is_java_specular(texture_path):
                base_name = texture_base_name(texture_path)
                texture_type: _TextureType = "specular"
            elif is_java_normal(texture_path):
                base_name = normal_texture_base_name(texture_path)
                texture_type = "normal"
            else:
                ignored.append(texture_path)
                continue

            group = groups.setdefault(
                base_name,
                _TextureGroup(
                    base_name=base_name,
                    specular_candidates=[],
                    normal_candidates=[],
                ),
            )
            if texture_type == "specular":
                group.specular_candidates.append(texture_path)
            else:
                group.normal_candidates.append(texture_path)

        return groups

    @staticmethod
    def _select_group_paths(
        group: _TextureGroup,
        ignored: list[Path],
    ) -> list[tuple[Path, _TextureType]]:
        selected_paths: list[tuple[Path, _TextureType]] = []

        if group.specular_candidates:
            selected_paths.append((group.specular_candidates[0], "specular"))
            ignored.extend(group.specular_candidates[1:])

        if group.normal_candidates:
            short_suffix_candidates = [
                path
                for path in group.normal_candidates
                if java_normal_suffix(path) == "_n"
            ]
            selected_normal = (
                short_suffix_candidates[0]
                if short_suffix_candidates
                else group.normal_candidates[0]
            )
            selected_paths.append((selected_normal, "normal"))
            ignored.extend(
                path
                for path in group.normal_candidates
                if path != selected_normal
            )

        return selected_paths

    @staticmethod
    def _convert_group(
        selected_paths: list[tuple[Path, _TextureType]],
        output_dir: Path,
        options: ConversionOptions,
        errors: list[str],
    ) -> list[tuple[Path, Path, _TextureType]]:
        successful_conversions: list[tuple[Path, Path, _TextureType]] = []

        for texture_path, texture_type in selected_paths:
            try:
                if texture_type == "specular":
                    output_path = convert_specular_to_mer(
                        texture_path,
                        output_dir,
                        sss_enabled=options.sss_enabled,
                    )
                else:
                    output_path = convert_normal_to_bedrock(
                        texture_path,
                        output_dir,
                        pom_enabled=options.pom_enabled,
                    )
                successful_conversions.append(
                    (texture_path, output_path, texture_type)
                )
            except Exception as exc:
                errors.append(f"{texture_path}: {exc}")

        return successful_conversions

    @staticmethod
    def _create_group_json(
        group: _TextureGroup,
        successful_conversions: list[tuple[Path, Path, _TextureType]],
        output_dir: Path,
        template_dir: Path,
        options: ConversionOptions,
        errors: list[str],
    ) -> Path | None:
        if not options.generate_json:
            return None

        try:
            uses_mers = any(
                texture_type == "specular"
                and output_path.stem.endswith("_mers")
                for _, output_path, texture_type in successful_conversions
            )
            effective_json_version = options.json_version
            if options.json_version in SUPPORTED_JSON_VERSIONS:
                effective_json_version = (
                    MERS_JSON_VERSION if uses_mers else MER_JSON_VERSION
                )
            return create_texture_set_json(
                group.base_name,
                output_dir,
                template_dir,
                effective_json_version,
            )
        except Exception as exc:
            errors.append(
                f"{group.base_name}: could not create texture set JSON: {exc}"
            )
            return None
