from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QLabel,
    QPushButton,
    QStatusBar,
)

from src.services import (  # noqa: E402
    ConversionService,
    PreferencesService,
    TextureAnalysisService,
)
from src.viewmodels import ConverterViewModel  # noqa: E402
from src.views import MainWindow  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def save_rgba(path: Path, blue: int = 0, alpha: int = 37) -> None:
    Image.new("RGBA", (1, 1), (128, 128, blue, alpha)).save(path)


def create_window(root: Path) -> MainWindow:
    viewmodel = ConverterViewModel(
        preferences=PreferencesService(root),
        analysis=TextureAnalysisService(),
        conversion=ConversionService(),
        fallback_output_dir=root / "output",
        template_dir=PROJECT_ROOT / "json",
    )
    return MainWindow(viewmodel)


class MainWindowIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def test_controls_follow_viewmodel_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            flat_normal_path = root / "dirt_n.png"
            pom_normal_path = root / "stone_n.png"
            specular_path = root / "stone_s.png"
            save_rgba(flat_normal_path, alpha=255)
            save_rgba(pom_normal_path, alpha=254)
            save_rgba(specular_path, blue=66)
            window = create_window(root)

            self.assertFalse(window.pom.isHidden())
            self.assertFalse(window.pom.isEnabled())
            self.assertFalse(window.sss.isEnabled())

            window.add_paths([str(flat_normal_path)])
            self.assertFalse(window.pom.isHidden())
            self.assertFalse(window.pom.isEnabled())

            window.add_paths([str(pom_normal_path)])
            self.assertFalse(window.pom.isHidden())
            self.assertTrue(window.pom.isEnabled())

            window.pom.setChecked(True)
            window.add_paths([str(specular_path)])
            self.assertTrue(window.pom.isEnabled())
            self.assertTrue(window.pom.isChecked())
            self.assertTrue(window.sss.isEnabled())

            window.clear_paths()
            self.assertFalse(window.pom.isHidden())
            self.assertFalse(window.pom.isEnabled())
            self.assertFalse(window.pom.isChecked())
            window.close()

    def test_initial_json_controls_match_new_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            window = create_window(Path(temp_dir))

            self.assertEqual(
                window.windowTitle(),
                "LabPBR2Bedrock — LabPBR to Bedrock Converter",
            )
            self.assertFalse(window.generate_json.isChecked())
            self.assertTrue(window.json_version.isEnabled())
            self.assertEqual(window.json_version.currentText(), "1.16.100")
            self.assertFalse(window.sss.isEnabled())
            self.assertFalse(window.pom.isEnabled())
            self.assertEqual(window.console.toPlainText(), "")
            self.assertEqual(window.output_button.text(), "Change…")
            self.assertTrue(window.output_label.isReadOnly())
            self.assertIsNone(window.findChild(QStatusBar))
            self.assertFalse(window.process_button.icon().isNull())
            self.assertFalse(window.clear_button.icon().isNull())
            self.assertFalse(window.drop_area.browse_button.icon().isNull())
            self.assertFalse(window.drop_area.drop_icon.pixmap().isNull())
            self.assertEqual(
                window.drop_area.subtitle.text(),
                "PNG/TGA image files with\n*_s, *_n, or *_normal suffixes",
            )
            self.assertNotIn("folders", window.drop_area.subtitle.text())
            self.assertFalse(window.output_button.icon().isNull())
            section_icons = window.findChildren(QLabel, "sectionIcon")
            self.assertEqual(len(section_icons), 3)
            self.assertTrue(
                all(not icon.pixmap().isNull() for icon in section_icons)
            )
            self.assertNotIn(
                "Clear log",
                [button.text() for button in window.findChildren(QPushButton)],
            )
            window.close()

    def test_browse_button_opens_file_picker_and_adds_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            texture_path = root / "stone_s.png"
            save_rgba(texture_path)
            window = create_window(root)
            window.show()

            with patch(
                "src.views.main_window.QFileDialog.getOpenFileNames",
                return_value=([str(texture_path)], "Texture files (*.png *.tga)"),
            ) as file_picker:
                QTest.mouseClick(window.drop_area.browse_button, Qt.LeftButton)

            file_picker.assert_called_once()
            self.assertEqual(window.file_list.count(), 1)
            self.assertEqual(window.file_list.item(0).text(), texture_path.name)
            self.assertEqual(
                window.file_list.item(0).toolTip(), str(texture_path)
            )
            window.close()

    def test_clicking_drop_area_does_not_open_file_picker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            window = create_window(Path(temp_dir))
            window.show()

            with patch(
                "src.views.main_window.QFileDialog.getOpenFileNames",
            ) as file_picker:
                QTest.mouseClick(window.drop_area, Qt.LeftButton)

            file_picker.assert_not_called()
            window.close()

    def test_json_version_and_sss_stay_synced_when_json_is_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            texture_path = root / "leaves_s.png"
            save_rgba(texture_path, blue=255)
            window = create_window(root)
            window.add_paths([str(texture_path)])

            self.assertFalse(window.generate_json.isChecked())
            window.json_version.setCurrentText("1.21.30")
            self.assertTrue(window.sss.isChecked())

            window.json_version.setCurrentText("1.16.100")
            self.assertFalse(window.sss.isChecked())

            window.sss.setChecked(True)
            self.assertEqual(window.json_version.currentText(), "1.21.30")
            window.close()

    def test_processing_with_sss_checked_writes_tga(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sss_path = root / "leaves_s.png"
            save_rgba(sss_path, blue=255)
            window = create_window(root)

            window.add_paths([str(sss_path)])
            window.generate_json.setChecked(False)
            window.sss.setChecked(True)
            summary = window.process_images()

            self.assertIsNotNone(summary)
            self.assertTrue((root / "output" / "leaves_mers.tga").exists())
            self.assertFalse(
                (root / "output" / "leaves.texture_set.json").exists()
            )
            self.assertEqual(window.file_list.count(), 0)
            self.assertFalse(window.sss.isEnabled())
            self.assertFalse(window.sss.isChecked())
            self.assertEqual(window.json_version.currentText(), "1.16.100")
            self.assertIn(
                "leaves_s.png -> leaves_mers.tga",
                window.console.toPlainText(),
            )
            self.assertTrue(window.process_button.isEnabled())
            window.close()

    def test_clear_button_clears_inputs_and_console_but_keeps_json_preference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            texture_path = root / "stone_s.png"
            save_rgba(texture_path)
            window = create_window(root)
            window.generate_json.setChecked(True)
            window.add_paths([str(texture_path)])

            window.clear_button.click()

            self.assertEqual(window.file_list.count(), 0)
            self.assertEqual(window.console.toPlainText(), "")
            self.assertTrue(window.generate_json.isChecked())
            self.assertEqual(window.json_version.currentText(), "1.16.100")
            window.close()

    def test_change_button_is_the_output_folder_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            selected_output = root / "custom-output"
            window = create_window(root)

            with patch(
                "src.views.main_window.QFileDialog.getExistingDirectory",
                return_value=str(selected_output),
            ) as folder_picker:
                window.output_button.click()

            folder_picker.assert_called_once()
            self.assertEqual(window.output_label.text(), str(selected_output))
            self.assertEqual(window.output_label.toolTip(), str(selected_output))
            self.assertIn(str(selected_output), (root / "options.txt").read_text())
            window.close()

    def test_canceling_output_picker_keeps_current_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            window = create_window(root)
            original_path = window.output_label.text()

            with patch(
                "src.views.main_window.QFileDialog.getExistingDirectory",
                return_value="",
            ) as folder_picker:
                window.output_button.click()

            folder_picker.assert_called_once()
            self.assertEqual(window.output_label.text(), original_path)
            self.assertFalse((root / "options.txt").exists())
            window.close()

    def test_long_output_path_stays_read_only_and_does_not_expand_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            window = create_window(Path(temp_dir))
            long_path = "C:\\" + "very-long-folder-name\\" * 30
            window.output_label.set_full_text(long_path)
            window.show()
            window.resize(860, 560)
            self.application.processEvents()

            self.assertEqual(window.output_label.toolTip(), long_path)
            self.assertEqual(window.output_label.text(), long_path)
            self.assertTrue(window.output_label.isReadOnly())
            self.assertGreater(window.output_label.width(), 50)
            self.assertLess(window.output_label.width(), window.width())
            self.assertGreater(window.console.height(), 100)
            window.close()


if __name__ == "__main__":
    unittest.main()
