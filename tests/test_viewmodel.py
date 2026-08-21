from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from PySide6.QtCore import QCoreApplication

from src.services import ConversionService, PreferencesService, TextureAnalysisService
from src.viewmodels import ConverterViewModel


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def save_rgba(path: Path, blue: int = 0) -> None:
    Image.new("RGBA", (1, 1), (128, 128, blue, 37)).save(path)


def create_viewmodel(root: Path) -> ConverterViewModel:
    return ConverterViewModel(
        preferences=PreferencesService(root),
        analysis=TextureAnalysisService(),
        conversion=ConversionService(),
        fallback_output_dir=root / "output",
        template_dir=PROJECT_ROOT / "json",
    )


class ConverterViewModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QCoreApplication.instance() or QCoreApplication([])

    def test_paths_are_deduplicated_and_specular_keeps_pom_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            normal = root / "stone_n.png"
            specular = root / "stone_s.png"
            save_rgba(normal)
            save_rgba(specular)
            vm = create_viewmodel(root)

            vm.add_paths([str(normal), str(normal)])
            self.assertEqual(vm.input_paths, [normal])
            self.assertTrue(vm.capabilities.pom_available)
            vm.set_pom_enabled(True)
            self.assertTrue(vm.options.pom_enabled)

            vm.add_paths([str(specular)])
            self.assertTrue(vm.capabilities.pom_available)
            self.assertTrue(vm.options.pom_enabled)

    def test_generate_json_is_disabled_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vm = create_viewmodel(Path(temp_dir))

            self.assertFalse(vm.options.generate_json)
            self.assertEqual(vm.options.json_version, "1.16.100")
            self.assertEqual(vm.status, "")

    def test_rejects_direct_jpeg_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            jpeg = root / "stone_n.jpg"
            Image.new("RGB", (1, 1), (128, 128, 255)).save(jpeg)
            vm = create_viewmodel(root)

            vm.add_paths([str(jpeg)])

            self.assertEqual(vm.input_paths, [])
            self.assertEqual(
                vm.status,
                "No new supported files were added. Use PNG or TGA.",
            )

    def test_sss_and_json_version_are_kept_in_sync(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            specular = root / "leaves_s.png"
            save_rgba(specular, blue=66)
            vm = create_viewmodel(root)
            vm.add_paths([str(specular)])

            self.assertEqual(vm.options.json_version, "1.16.100")
            vm.set_sss_enabled(True)
            self.assertEqual(vm.options.json_version, "1.21.30")

            vm.set_sss_enabled(False)
            self.assertEqual(vm.options.json_version, "1.16.100")

            vm.set_json_version("1.21.30")
            self.assertTrue(vm.options.sss_enabled)
            self.assertEqual(vm.options.json_version, "1.21.30")

            vm.set_json_version("1.16.100")
            self.assertFalse(vm.options.sss_enabled)
            self.assertEqual(vm.options.json_version, "1.16.100")

    def test_clear_paths_disables_sss(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            specular = root / "leaves_s.png"
            save_rgba(specular, blue=255)
            vm = create_viewmodel(root)
            vm.add_paths([str(specular)])
            vm.set_sss_enabled(True)

            vm.clear_paths()
            self.assertEqual(vm.input_paths, [])
            self.assertFalse(vm.capabilities.sss_available)
            self.assertFalse(vm.options.sss_enabled)
            self.assertEqual(vm.options.json_version, "1.16.100")

    def test_process_without_inputs_requests_information(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vm = create_viewmodel(Path(temp_dir))
            notifications: list[tuple[str, str, str]] = []
            vm.notification_requested.connect(
                lambda level, title, message: notifications.append(
                    (level, title, message)
                )
            )

            self.assertIsNone(vm.process())
            self.assertEqual(notifications[0][0:2], ("information", "No inputs"))

    def test_completed_process_clears_inputs_and_formats_console_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "stone_s.png"
            save_rgba(source)
            vm = create_viewmodel(root)
            vm.add_paths([str(source)])

            summary = vm.process()

            self.assertIsNotNone(summary)
            self.assertEqual(vm.input_paths, [])
            self.assertIn("Converted: 1", vm.status)
            self.assertIn("stone_s.png -> stone_mer.png", vm.status)
            self.assertIn("Ignored: 0", vm.status)
            self.assertIn("Errors: 0", vm.status)
            self.assertIn(f"Output: {root / 'output'}", vm.status)

    def test_partial_conversion_errors_still_clear_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            specular = root / "stone_s.png"
            corrupt_normal = root / "stone_n.png"
            save_rgba(specular)
            corrupt_normal.write_bytes(b"not an image")
            vm = create_viewmodel(root)
            vm.add_paths([str(specular), str(corrupt_normal)])

            summary = vm.process()

            self.assertIsNotNone(summary)
            self.assertEqual(len(summary.errors), 1)
            self.assertEqual(vm.input_paths, [])
            self.assertIn("Errors: 1", vm.status)
            self.assertIn("stone_n.png", vm.status)

    def test_new_conversion_replaces_previous_console_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stone = root / "stone_s.png"
            leaves = root / "leaves_s.png"
            save_rgba(stone)
            save_rgba(leaves)
            vm = create_viewmodel(root)

            vm.add_paths([str(stone)])
            vm.process()
            self.assertIn("stone_s.png", vm.status)

            vm.add_paths([str(leaves)])
            vm.process()

            self.assertIn("leaves_s.png -> leaves_mer.png", vm.status)
            self.assertNotIn("stone_s.png", vm.status)

    def test_fatal_conversion_error_keeps_inputs_for_retry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "stone_s.png"
            save_rgba(source)
            vm = create_viewmodel(root)
            vm.add_paths([str(source)])
            notifications: list[tuple[str, str, str]] = []
            vm.notification_requested.connect(
                lambda level, title, message: notifications.append(
                    (level, title, message)
                )
            )

            with patch.object(
                vm._conversion,
                "convert",
                side_effect=RuntimeError("unexpected failure"),
            ):
                summary = vm.process()

            self.assertIsNone(summary)
            self.assertEqual(vm.input_paths, [source])
            self.assertEqual(notifications[-1][0:2], ("critical", "Conversion error"))

    def test_clear_all_clears_console_and_inputs_but_keeps_json_preference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "stone_s.png"
            save_rgba(source)
            vm = create_viewmodel(root)
            vm.set_generate_json(True)
            vm.add_paths([str(source)])

            vm.clear_all()

            self.assertEqual(vm.input_paths, [])
            self.assertEqual(vm.status, "")
            self.assertTrue(vm.options.generate_json)
            self.assertEqual(vm.options.json_version, "1.16.100")


if __name__ == "__main__":
    unittest.main()
