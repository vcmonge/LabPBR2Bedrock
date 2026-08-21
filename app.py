"""Entry point for LabPBR2Bedrock."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.services import ConversionService, PreferencesService, TextureAnalysisService
from src.viewmodels import ConverterViewModel
from src.views import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LabPBR2Bedrock — LabPBR to Bedrock Converter."
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path.cwd()),
        help="Directory where converted textures and optional JSON files will be saved.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app_dir = Path(__file__).resolve().parent
    fallback_output_dir = Path(args.output_dir).expanduser().resolve()

    app = QApplication(sys.argv)
    app.setApplicationName("LabPBR2Bedrock")
    app.setApplicationDisplayName("LabPBR to Bedrock Converter")
    viewmodel = ConverterViewModel(
        preferences=PreferencesService(app_dir),
        analysis=TextureAnalysisService(),
        conversion=ConversionService(),
        fallback_output_dir=fallback_output_dir,
        template_dir=app_dir / "json",
    )
    window = MainWindow(viewmodel)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
