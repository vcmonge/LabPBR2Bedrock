from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)


ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"


class DropArea(QFrame):
    paths_dropped = Signal(list)
    clicked = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        self.setMinimumSize(360, 420)
        self.setCursor(Qt.ArrowCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.file_list = QListWidget()
        self.file_list.setObjectName("dropFileList")
        self.file_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.file_list.setFocusPolicy(Qt.NoFocus)
        self.file_list.setAcceptDrops(False)
        self.file_list.viewport().setAcceptDrops(False)
        self.file_list.setMaximumHeight(150)
        self.file_list.hide()
        layout.addWidget(self.file_list)
        layout.addStretch(1)

        self.drop_icon = QLabel()
        self.drop_icon.setObjectName("dropIcon")
        self.drop_icon.setPixmap(
            QIcon(str(ASSETS_DIR / "drag_and_drop_icon.svg")).pixmap(
                QSize(76, 76)
            )
        )
        self.drop_icon.setFixedSize(82, 82)
        self.drop_icon.setAlignment(Qt.AlignCenter)
        self.drop_icon.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.title = QLabel("Drag Java PBR textures here")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("dropTitle")
        self.title.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.or_label = QLabel("or")
        self.or_label.setAlignment(Qt.AlignCenter)
        self.or_label.setObjectName("dropOr")
        self.or_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.browse_button = QPushButton("Browse files…")
        self.browse_button.setObjectName("browseButton")
        self.browse_button.setIcon(QIcon(str(ASSETS_DIR / "folder_icon.svg")))
        self.browse_button.setIconSize(QSize(21, 21))
        self.browse_button.setAccessibleName("Browse texture files")
        self.browse_button.clicked.connect(lambda _checked=False: self.clicked.emit())

        self.subtitle = QLabel(
            "PNG/TGA image files with\n"
            "*_s, *_n, or *_normal suffixes"
        )
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setObjectName("dropSubtitle")
        self.subtitle.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout.addWidget(self.drop_icon, alignment=Qt.AlignHCenter)
        layout.addWidget(self.title)
        layout.addWidget(self.or_label)
        layout.addWidget(self.browse_button, alignment=Qt.AlignHCenter)
        layout.addSpacing(4)
        layout.addWidget(self.subtitle)
        layout.addStretch(1)

    def set_paths(self, paths: list[Path]) -> None:
        self.file_list.clear()
        for path in paths:
            item = QListWidgetItem(path.name or str(path))
            item.setToolTip(str(path))
            self.file_list.addItem(item)
        self.file_list.setVisible(bool(paths))

    def _set_dragging(self, dragging: bool) -> None:
        self.setProperty("dragging", dragging)
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_dragging(True)
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        self._set_dragging(False)
        event.accept()

    def dropEvent(self, event) -> None:  # noqa: N802
        self._set_dragging(False)
        paths = [
            local_path
            for url in event.mimeData().urls()
            if (local_path := url.toLocalFile())
        ]

        if paths:
            self.paths_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            event.ignore()
