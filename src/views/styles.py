from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
ARROW_ICON_PATH = (ASSETS_DIR / "chevron_down_icon.svg").as_posix()
CHECK_ICON_PATH = (ASSETS_DIR / "check_icon.svg").as_posix()


MAIN_WINDOW_STYLES = """
#windowRoot,
#rightPanel {
    background: #f8f9fa;
}
QWidget {
    color: #1f1f1f;
    font-size: 10pt;
}

#dropArea {
    border: 2px dashed #c4c6d0;
    border-radius: 16px;
    background: #ffffff;
}
#dropArea:hover {
    border-color: #74777f;
}
#dropArea[dragging="true"] {
    border-color: #0b57d0;
    background: #f0f4fd;
}
#dropTitle {
    color: #1f1f1f;
    font-size: 15pt;
    font-weight: 600;
}
#dropOr {
    color: #44474e;
    font-size: 10.5pt;
}
#dropSubtitle {
    color: #44474e;
    font-size: 9.5pt;
    line-height: 1.4;
}
#dropFileList {
    color: #1f1f1f;
    font-size: 10pt;
    border: 1px solid #c4c6d0;
    border-radius: 8px;
    background: #f1f3f5;
    outline: 0;
    padding: 4px;
}
#dropFileList::item {
    min-height: 26px;
    padding: 2px 8px;
    border-radius: 4px;
    background: transparent;
}
#dropFileList::item:hover {
    background: rgba(31, 31, 31, 0.08);
}

#optionsPanel,
#activityPanel,
#outputPanel {
    border: 1px solid #c4c6d0;
    border-radius: 12px;
    background: #ffffff;
}
#sectionDivider {
    color: #c4c6d0;
    background: #c4c6d0;
    border: 0;
    max-height: 1px;
}
#sectionTitle {
    color: #1f1f1f;
    font-size: 11.5pt;
    font-weight: 600;
}

QPushButton {
    min-height: 38px;
    padding: 0 16px;
    border: 1px solid #74777f;
    border-radius: 19px;
    color: #0b57d0;
    background: #ffffff;
    font-size: 10pt;
    font-weight: 500;
    outline: 0;
}
QPushButton:hover {
    border-color: #0b57d0;
    background: #f0f4fd;
}
QPushButton:pressed {
    background: #d3e3fd;
}
QPushButton:focus {
    border-color: #0b57d0;
}
QPushButton:disabled {
    border-color: rgba(31, 31, 31, 0.12);
    color: rgba(31, 31, 31, 0.38);
    background: transparent;
}

#primaryButton,
#clearButton {
    min-height: 40px;
    font-size: 11pt;
    font-weight: 600;
    border-radius: 20px;
    padding: 0 20px;
}
#primaryButton {
    color: #ffffff;
    border: 0;
    background: #0b57d0;
}
#primaryButton:hover {
    background: #0842a0;
}
#primaryButton:pressed {
    background: #063380;
}
#primaryButton:disabled {
    color: rgba(31, 31, 31, 0.38);
    border: 0;
    background: rgba(31, 31, 31, 0.12);
}

#clearButton {
    color: #ba1a1a;
    border: 1px solid #ba1a1a;
    background: #ffffff;
}
#clearButton:hover {
    border-color: #ba1a1a;
    background: #ffdad6;
}
#clearButton:pressed {
    background: #ffb4ab;
}
#clearButton:focus {
    border-color: #ba1a1a;
}

#browseButton {
    min-width: 180px;
    min-height: 40px;
    border-radius: 20px;
    border: 1px solid #74777f;
    color: #0b57d0;
    background: #ffffff;
    font-size: 10.5pt;
    font-weight: 500;
}
#browseButton:hover {
    border-color: #0b57d0;
    background: #f0f4fd;
}
#browseButton:pressed {
    background: #d3e3fd;
}

#secondaryButton {
    min-height: 38px;
    border-radius: 19px;
    border: 1px solid #74777f;
    color: #0b57d0;
    background: #ffffff;
    padding: 0 16px;
}
#secondaryButton:hover {
    border-color: #0b57d0;
    background: #f0f4fd;
}
#secondaryButton:pressed {
    background: #d3e3fd;
}

QCheckBox {
    min-height: 28px;
    spacing: 10px;
    font-size: 10.5pt;
    color: #1f1f1f;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #74777f;
    border-radius: 3px;
    background: transparent;
}
QCheckBox::indicator:hover {
    border-color: #1f1f1f;
    background: rgba(31, 31, 31, 0.04);
}
QCheckBox::indicator:checked {
    border: 2px solid #0b57d0;
    background-color: #0b57d0;
    image: url("__CHECK_ICON_PATH__");
}
QCheckBox::indicator:checked:hover {
    border-color: #0842a0;
    background-color: #0842a0;
}
QCheckBox::indicator:disabled {
    border-color: rgba(31, 31, 31, 0.12);
    background: transparent;
}
QCheckBox:disabled {
    color: rgba(31, 31, 31, 0.38);
}

#versionCombo {
    min-height: 38px;
    padding: 2px 36px 2px 12px;
    border: 1px solid #74777f;
    border-radius: 8px;
    color: #1f1f1f;
    background: #ffffff;
    font-size: 10pt;
}
#versionCombo:hover {
    border-color: #1f1f1f;
}
#versionCombo:focus {
    border: 2px solid #0b57d0;
}
#versionCombo::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 34px;
    border: 0;
    background: transparent;
}
#versionCombo::down-arrow {
    width: 12px;
    height: 8px;
    image: url("__ARROW_ICON_PATH__");
}
#versionCombo QAbstractItemView {
    padding: 4px;
    border: 1px solid #c4c6d0;
    border-radius: 8px;
    color: #1f1f1f;
    background: #ffffff;
    selection-color: #041e49;
    selection-background-color: #d3e3fd;
    outline: 0;
}

#consoleInfo {
    padding: 10px;
    border: 1px solid #c4c6d0;
    border-radius: 8px;
    color: #1f1f1f;
    background: #f1f3f5;
    selection-color: #041e49;
    selection-background-color: #d3e3fd;
    font-family: Consolas, "Cascadia Code", monospace, "Segoe UI";
    font-size: 9pt;
}

#outputPath {
    min-height: 38px;
    padding: 0 12px;
    border: 1px solid #c4c6d0;
    border-radius: 8px;
    color: #1f1f1f;
    background: #f1f3f5;
    font-size: 10pt;
}
""".replace(
    "__ARROW_ICON_PATH__", ARROW_ICON_PATH
).replace(
    "__CHECK_ICON_PATH__", CHECK_ICON_PATH
)
