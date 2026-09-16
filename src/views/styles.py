from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
ARROW_ICON_PATH = (ASSETS_DIR / "chevron_down_icon.svg").as_posix()
CHECK_ICON_PATH = (ASSETS_DIR / "check_icon.svg").as_posix()


MAIN_WINDOW_STYLES = """
#windowRoot,
#rightPanel {
    background: #f7f5f0;
}
QWidget {
    color: #141413;
    font-size: 10pt;
}

#dropArea {
    border: 1.5px dashed #ded8cf;
    border-radius: 12px;
    background: #fdfcf9;
}
#dropArea:hover {
    border-color: #8e8b82;
}
#dropArea[dragging="true"] {
    border-color: #cc785c;
    background: #f5f0e8;
}
#dropTitle {
    color: #141413;
    font-size: 14pt;
    font-weight: 600;
}
#dropOr {
    color: #6c6a64;
    font-size: 10pt;
}
#dropSubtitle {
    color: #8e8b82;
    font-size: 9.5pt;
    line-height: 1.4;
}
#dropFileList {
    color: #141413;
    font-size: 10pt;
    border: 1px solid #e8e2d8;
    border-radius: 8px;
    background: #ffffff;
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
    background: rgba(20, 20, 19, 0.06);
}

#optionsPanel,
#activityPanel,
#outputPanel {
    border: 1px solid #e8e2d8;
    border-radius: 12px;
    background: #fdfcf9;
}
#sectionDivider {
    color: #e8e2d8;
    background: #e8e2d8;
    border: 0;
    max-height: 1px;
}
#sectionTitle {
    color: #141413;
    font-size: 11.5pt;
    font-weight: 600;
}

QPushButton {
    min-height: 38px;
    padding: 0 16px;
    border: 1px solid #e8e2d8;
    border-radius: 8px;
    color: #141413;
    background: #ffffff;
    font-size: 10pt;
    font-weight: 500;
    outline: 0;
}
QPushButton:hover {
    border-color: #8e8b82;
    background: #f7f4ed;
}
QPushButton:pressed {
    background: #f0eae0;
}
QPushButton:focus {
    border-color: #cc785c;
}
QPushButton:disabled {
    border-color: #e8e2d8;
    color: #8e8b82;
    background: transparent;
}

#primaryButton,
#clearButton {
    min-height: 40px;
    font-size: 10.5pt;
    font-weight: 500;
    border-radius: 8px;
    padding: 0 20px;
}
#primaryButton {
    color: #ffffff;
    border: 0;
    background: #cc785c;
}
#primaryButton:hover {
    background: #bd6d52;
}
#primaryButton:pressed {
    background: #a9583e;
}
#primaryButton:disabled {
    color: #8e8b82;
    border: 0;
    background: #e8e2d8;
}

#clearButton {
    color: #3d3d3a;
    border: 1px solid #e8e2d8;
    background: #ffffff;
}
#clearButton:hover {
    border-color: #c64545;
    color: #c64545;
    background: #fdf5f5;
}
#clearButton:pressed {
    background: #fbe5e5;
}
#clearButton:focus {
    border-color: #c64545;
}
#clearButton:disabled {
    color: #8e8b82;
    border-color: #e8e2d8;
    background: transparent;
}

#browseButton {
    min-width: 160px;
    min-height: 38px;
    border-radius: 8px;
    border: 1px solid #e8e2d8;
    color: #141413;
    background: #ffffff;
    font-size: 10pt;
    font-weight: 500;
}
#browseButton:hover {
    border-color: #8e8b82;
    background: #f7f4ed;
}
#browseButton:pressed {
    background: #f0eae0;
}

#secondaryButton {
    min-height: 38px;
    border-radius: 8px;
    border: 1px solid #e8e2d8;
    color: #141413;
    background: #ffffff;
    padding: 0 16px;
}
#secondaryButton:hover {
    border-color: #8e8b82;
    background: #f7f4ed;
}
#secondaryButton:pressed {
    background: #f0eae0;
}

QCheckBox {
    min-height: 28px;
    spacing: 10px;
    font-size: 10pt;
    color: #3d3d3a;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1.5px solid #8e8b82;
    border-radius: 4px;
    background: #ffffff;
}
QCheckBox::indicator:hover {
    border-color: #141413;
    background: #f7f4ed;
}
QCheckBox::indicator:checked {
    border: 1.5px solid #cc785c;
    background-color: #cc785c;
    image: url("__CHECK_ICON_PATH__");
}
QCheckBox::indicator:checked:hover {
    border-color: #a9583e;
    background-color: #a9583e;
}
QCheckBox::indicator:disabled {
    border-color: #e8e2d8;
    background: #f2eee6;
}
QCheckBox:disabled {
    color: #8e8b82;
}

#versionCombo {
    min-height: 38px;
    padding: 2px 36px 2px 12px;
    border: 1px solid #e8e2d8;
    border-radius: 8px;
    color: #141413;
    background: #ffffff;
    font-size: 10pt;
}
#versionCombo:hover {
    border-color: #8e8b82;
}
#versionCombo:focus {
    border: 1.5px solid #cc785c;
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
    border: 1px solid #e8e2d8;
    border-radius: 8px;
    color: #141413;
    background: #ffffff;
    selection-color: #141413;
    selection-background-color: #f2eee6;
    outline: 0;
}

#consoleInfo {
    padding: 10px;
    border: 1px solid #ded7cb;
    border-radius: 8px;
    color: #1e1e1c;
    background: #f2eee6;
    selection-color: #141413;
    selection-background-color: #dfd5c4;
    font-family: Consolas, "Cascadia Code", monospace;
    font-size: 9pt;
}

#outputPath {
    min-height: 38px;
    padding: 0 12px;
    border: 1px solid #e8e2d8;
    border-radius: 8px;
    color: #141413;
    background: #f2eee6;
    font-size: 10pt;
}
""".replace(
    "__ARROW_ICON_PATH__", ARROW_ICON_PATH
).replace(
    "__CHECK_ICON_PATH__", CHECK_ICON_PATH
)
