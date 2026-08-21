from __future__ import annotations

from dataclasses import dataclass


MER_JSON_VERSION = "1.16.100"
MERS_JSON_VERSION = "1.21.30"
SUPPORTED_JSON_VERSIONS = (MER_JSON_VERSION, MERS_JSON_VERSION)


@dataclass(frozen=True)
class ConversionOptions:
    """Options passed to a conversion run."""

    generate_json: bool
    json_version: str
    pom_enabled: bool
    sss_enabled: bool
