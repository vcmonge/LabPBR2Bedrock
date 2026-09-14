from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSignalBlocker, QSize, Qt
from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.models import (
    SUPPORTED_JSON_VERSIONS,
    ConversionOptions,
    ConversionSummary,
    TextureCapabilities,
)
from src.viewmodels import ConverterViewModel

from .drop_area import DropArea
from .styles import MAIN_WINDOW_STYLES


ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"


class PathLineEdit(QLineEdit):
    """Read-only path field that remains compact and exposes the full value."""

    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setObjectName("outputPath")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setMinimumWidth(0)
        self.setAccessibleName("Output directory")

    def set_full_text(self, text: str) -> None:
        self.setText(text)
        self.setToolTip(text)
        self.setCursorPosition(0)


class MainWindow(QMainWindow):
    """Qt presentation layer for the converter."""

    def __init__(self, viewmodel: ConverterViewModel) -> None:
        super().__init__()
        self._vm = viewmodel
        self.setWindowTitle(
            "LabPBR2Bedrock — LabPBR to Bedrock Converter"
        )
        self.setMinimumSize(860, 560)
        self.resize(1120, 700)

        root = QWidget()
        root.setObjectName("windowRoot")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.drop_area = DropArea()
        self.file_list = self.drop_area.file_list
        layout.addWidget(self.drop_area, stretch=49)

        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)

        right_layout.addWidget(self._build_options_panel())
        right_layout.addWidget(self._build_activity_panel(), stretch=1)
        right_layout.addWidget(self._build_output_panel())
        layout.addWidget(right_panel, stretch=51)

        self.setStyleSheet(MAIN_WINDOW_STYLES)
        self._bind()
        self._render_initial_state()

    @staticmethod
    def _icon(file_name: str) -> QIcon:
        return QIcon(str(ASSETS_DIR / file_name))

    @classmethod
    def _section_title(cls, icon_name: str, text: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(9)

        icon = QLabel()
        icon.setObjectName("sectionIcon")
        icon.setPixmap(cls._icon(icon_name).pixmap(QSize(25, 25)))
        icon.setFixedSize(27, 27)
        icon.setAlignment(Qt.AlignCenter)
        icon.setAttribute(Qt.WA_TransparentForMouseEvents)

        title = QLabel(text)
        title.setObjectName("sectionTitle")
        row.addWidget(icon)
        row.addWidget(title)
        row.addStretch(1)
        return row

    @staticmethod
    def _section_frame(object_name: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName(object_name)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        return frame, layout

    def _build_options_panel(self) -> QFrame:
        panel, panel_layout = self._section_frame("optionsPanel")

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(12)

        self.process_button = QPushButton("Process images")
        self.process_button.setObjectName("primaryButton")
        self.process_button.setIcon(self._icon("process_images_icon.svg"))
        self.process_button.setIconSize(QSize(22, 22))
        self.process_button.setAccessibleName("Process images")

        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setIcon(self._icon("clear-icon.svg"))
        self.clear_button.setIconSize(QSize(22, 22))
        self.clear_button.setAccessibleName("Clear inputs and activity log")

        action_row.addWidget(self.process_button, stretch=6)
        action_row.addWidget(self.clear_button, stretch=5)
        panel_layout.addLayout(action_row)

        divider = QFrame()
        divider.setObjectName("sectionDivider")
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Plain)
        panel_layout.addWidget(divider)

        panel_layout.addLayout(self._section_title("options-icon.svg", "Options"))

        option_rows = QVBoxLayout()
        option_rows.setContentsMargins(4, 2, 4, 4)
        option_rows.setSpacing(8)

        json_row = QHBoxLayout()
        json_row.setContentsMargins(0, 0, 0, 0)
        json_row.setSpacing(12)
        self.generate_json = QCheckBox("Generate JSON")
        self.json_version = QComboBox()
        self.json_version.setObjectName("versionCombo")
        self.json_version.addItems(list(SUPPORTED_JSON_VERSIONS))
        self.json_version.setMinimumWidth(150)
        self.json_version.setMaximumWidth(190)
        json_row.addWidget(self.generate_json)
        json_row.addWidget(self.json_version)
        json_row.addStretch(1)
        option_rows.addLayout(json_row)

        self.sss = QCheckBox("SSS")
        self.pom = QCheckBox("POM")
        option_rows.addWidget(self.sss)
        option_rows.addWidget(self.pom)
        panel_layout.addLayout(option_rows)
        return panel

    def _build_activity_panel(self) -> QFrame:
        panel, panel_layout = self._section_frame("activityPanel")
        panel_layout.addLayout(self._section_title("log_icon.svg", "Activity log"))

        self.console = QPlainTextEdit()
        self.console.setObjectName("consoleInfo")
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(145)
        self.console.setPlaceholderText("")
        self.console.setAccessibleName("Activity log")
        panel_layout.addWidget(self.console, stretch=1)
        return panel

    def _build_output_panel(self) -> QFrame:
        panel, panel_layout = self._section_frame("outputPanel")
        panel_layout.addLayout(
            self._section_title("folder_icon.svg", "Output directory")
        )

        output_row = QHBoxLayout()
        output_row.setContentsMargins(0, 0, 0, 0)
        output_row.setSpacing(12)

        self.output_label = PathLineEdit()
        self.output_button = QPushButton("Change…")
        self.output_button.setObjectName("secondaryButton")
        self.output_button.setIcon(self._icon("folder_icon.svg"))
        self.output_button.setIconSize(QSize(21, 21))
        self.output_button.setToolTip("Change output folder")
        self.output_button.setAccessibleName("Change output folder")

        output_row.addWidget(self.output_label, stretch=1)
        output_row.addWidget(self.output_button)
        panel_layout.addLayout(output_row)
        return panel

    def _bind(self) -> None:
        self._vm.paths_changed.connect(self._on_paths_changed)
        self._vm.capabilities_changed.connect(self._on_capabilities_changed)
        self._vm.options_changed.connect(self._on_options_changed)
        self._vm.output_dir_changed.connect(self._on_output_dir_changed)
        self._vm.status_changed.connect(self._on_status_changed)
        self._vm.processing_changed.connect(self._on_processing_changed)
        self._vm.notification_requested.connect(self._on_notification_requested)

        self.drop_area.paths_dropped.connect(self._vm.add_paths)
        self.drop_area.clicked.connect(self.choose_input_files)
        self.clear_button.clicked.connect(self._vm.clear_all)
        self.process_button.clicked.connect(self._vm.process)
        self.output_button.clicked.connect(self.choose_output_dir)
        self.generate_json.toggled.connect(self._vm.set_generate_json)
        self.pom.toggled.connect(self._vm.set_pom_enabled)
        self.sss.toggled.connect(self._vm.set_sss_enabled)
        self.json_version.currentTextChanged.connect(self._vm.set_json_version)

    def _render_initial_state(self) -> None:
        self._on_paths_changed(self._vm.input_paths)
        self._on_capabilities_changed(self._vm.capabilities)
        self._on_options_changed(self._vm.options)
        self._on_output_dir_changed(
            str(self._vm.output_dir) if self._vm.output_dir is not None else ""
        )
        self._on_status_changed(self._vm.status)

    def _on_paths_changed(self, paths: list[Path]) -> None:
        self.drop_area.set_paths(paths)

    def _on_capabilities_changed(
        self, capabilities: TextureCapabilities
    ) -> None:
        self.pom.setVisible(True)
        self.pom.setEnabled(capabilities.pom_available)
        self.pom.setToolTip(
            (
                "Packs LabPBR height into the normal Blue channel for BetterRTX 1.5 POM. "
                "Vanilla RTX and Vibrant Visuals read Blue as Z; leave POM off to reconstruct Z."
            )
            if capabilities.pom_available
            else (
                "Available when a normal texture contains LabPBR height information. "
                "POM packing targets BetterRTX 1.5, not vanilla RTX or Vibrant Visuals."
            )
        )

        self.sss.setVisible(True)
        self.sss.setEnabled(capabilities.sss_available)
        self.sss.setToolTip(
            (
                "Converts textures containing SSS to 32-bit RGBA MERS TGA maps. "
                "Metalness and SSS are mutually exclusive; the higher value wins and a tie keeps SSS."
            )
            if capabilities.sss_available
            else (
                "Available when an _s texture contains subsurface scattering "
                "after metalness exclusion."
            )
        )

    def _on_options_changed(self, options: ConversionOptions) -> None:
        blockers = [
            QSignalBlocker(self.generate_json),
            QSignalBlocker(self.pom),
            QSignalBlocker(self.sss),
            QSignalBlocker(self.json_version),
        ]
        self.generate_json.setChecked(options.generate_json)
        self.pom.setChecked(options.pom_enabled)
        self.sss.setChecked(options.sss_enabled)
        self.json_version.setCurrentText(options.json_version)
        del blockers

    def _on_output_dir_changed(self, output_dir: str) -> None:
        self.output_label.set_full_text(
            output_dir if output_dir else "invalid default path"
        )

    def _on_status_changed(self, status: str) -> None:
        self.console.setPlainText(status)
        self.console.moveCursor(QTextCursor.Start)

    def _on_processing_changed(self, processing: bool) -> None:
        self.process_button.setEnabled(not processing)
        self.process_button.setText(
            "Processing…" if processing else "Process images"
        )
        if processing:
            QApplication.processEvents()

    def _on_notification_requested(
        self, level: str, title: str, message: str
    ) -> None:
        if level == "information":
            QMessageBox.information(self, title, message)
        elif level == "critical":
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.warning(self, title, message)

    def choose_output_dir(self) -> None:
        start_dir = (
            str(self._vm.output_dir)
            if self._vm.output_dir is not None
            else str(Path.home())
        )
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select output folder",
            start_dir,
        )
        if selected_dir:
            self._vm.change_output_dir(selected_dir)

    def choose_input_files(self) -> None:
        selected_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select texture files",
            str(Path.home()),
            "Texture files (*.png *.tga);;All files (*)",
        )
        if selected_files:
            self._vm.add_paths(selected_files)

    # Small delegation helpers retain a convenient integration-test surface.
    def add_paths(self, paths: list[str]) -> None:
        self._vm.add_paths(paths)

    def clear_paths(self) -> None:
        self._vm.clear_all()

    def process_images(self) -> ConversionSummary | None:
        return self._vm.process()
