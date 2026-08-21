"""Texture conversion primitives."""

from .mer_converter import (
    convert_specular_to_mer,
    has_subsurface_scattering,
    is_java_specular,
)
from .normal_converter import (
    convert_normal_to_bedrock,
    has_parallax_occlusion_mapping,
    is_java_normal,
    normal_texture_base_name,
)
from .texture_set_converter import create_texture_set_json

__all__ = [
    "convert_normal_to_bedrock",
    "convert_specular_to_mer",
    "create_texture_set_json",
    "has_parallax_occlusion_mapping",
    "has_subsurface_scattering",
    "is_java_normal",
    "is_java_specular",
    "normal_texture_base_name",
]
