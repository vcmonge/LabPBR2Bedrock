from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.models import ConversionOptions, ConversionSummary
from src.services import ConversionService, PreferencesService, TextureAnalysisService
from src.services.preferences_service import decode_options_text, path_from_options_value
from src.services.texture_file_collector import collect_texture_files


def save_rgba(path: Path, blue: int = 0, alpha: int = 37) -> None:
    Image.new("RGBA", (1, 1), (128, 128, blue, alpha)).save(path)


class TextureFileCollectorTests(unittest.TestCase):
    def test_collects_recursively_deduplicates_and_uses_stable_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            nested = root / "nested"
            nested.mkdir()
            paths = [
                root / "B_s.PNG",
                root / "a_n.tga",
                nested / "c_s.png",
            ]
            for path in paths:
                save_rgba(path)
            Image.new("RGB", (1, 1)).save(root / "ignored.jpg")

            collected = collect_texture_files([root, paths[1]])

            self.assertEqual(
                collected,
                sorted(
                    paths,
                    key=lambda path: (str(path).casefold(), str(path)),
                ),
            )


class TextureAnalysisServiceTests(unittest.TestCase):
    def test_accepts_only_png_tga_files_and_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            png_path = root / "stone_n.PNG"
            tga_path = root / "stone_s.TGA"
            jpg_path = root / "stone_n.jpg"
            save_rgba(png_path)
            save_rgba(tga_path)
            Image.new("RGB", (1, 1), (128, 128, 255)).save(jpg_path)
            service = TextureAnalysisService()

            self.assertTrue(service.accepts_input_path(root))
            self.assertTrue(service.accepts_input_path(png_path))
            self.assertTrue(service.accepts_input_path(tga_path))
            self.assertFalse(service.accepts_input_path(jpg_path))
            self.assertEqual(
                set(service.collect_files([root])),
                {png_path, tga_path},
            )

    def test_analyze_reports_pom_and_sss_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            normal = root / "stone_n.png"
            flat_normal = root / "dirt_n.png"
            specular = root / "leaves_s.png"
            save_rgba(normal, alpha=254)
            save_rgba(flat_normal, alpha=255)
            save_rgba(specular, blue=66)
            service = TextureAnalysisService()

            no_pom = service.analyze([flat_normal])
            self.assertTrue(no_pom.has_normals)
            self.assertFalse(no_pom.has_pom)
            self.assertFalse(no_pom.pom_available)

            normal_only = service.analyze([normal])
            self.assertTrue(normal_only.has_pom)
            self.assertTrue(normal_only.pom_available)
            self.assertFalse(normal_only.sss_available)

            combined = service.analyze([flat_normal, normal, specular])
            self.assertTrue(combined.has_normals)
            self.assertTrue(combined.has_speculars)
            self.assertTrue(combined.has_pom)
            self.assertTrue(combined.pom_available)
            self.assertTrue(combined.sss_available)

    def test_corrupt_specular_does_not_enable_sss(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "broken_s.png"
            path.write_bytes(b"not an image")
            capabilities = TextureAnalysisService().analyze([path])
            self.assertTrue(capabilities.has_speculars)
            self.assertFalse(capabilities.sss_available)

    def test_corrupt_normal_does_not_enable_pom(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "broken_n.png"
            path.write_bytes(b"not an image")

            capabilities = TextureAnalysisService().analyze([path])

            self.assertTrue(capabilities.has_normals)
            self.assertFalse(capabilities.has_pom)
            self.assertFalse(capabilities.pom_available)


class PreferencesServiceTests(unittest.TestCase):
    def test_save_and_load_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "salida"
            service = PreferencesService(root)
            service.save_output_dir(output)

            self.assertEqual(service.load_output_dir(root / "fallback"), output.resolve())
            self.assertEqual(
                service.options_path.read_text(encoding="utf-8"),
                f"path: {output}\n",
            )

    def test_load_supports_utf16_and_invalid_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "salida"
            (root / "options.txt").write_bytes(f"path: {output}\n".encode("utf-16"))
            self.assertEqual(
                PreferencesService(root).load_output_dir(root / "fallback"),
                output.resolve(),
            )
        self.assertIsNone(path_from_options_value("\x00invalid"))
        self.assertIn("path:", decode_options_text("path: x".encode("utf-8")))


class ConversionServiceTests(unittest.TestCase):
    def test_convert_empty_batch_returns_empty_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = ConversionService().convert(
                [],
                root / "output",
                root / "json",
                ConversionOptions(True, "1.21.30", True, True),
            )

        self.assertEqual(
            result,
            ConversionSummary(converted=[], ignored=[], errors=[]),
        )


if __name__ == "__main__":
    unittest.main()
