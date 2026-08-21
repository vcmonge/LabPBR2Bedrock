from pathlib import Path


ARROW_ICON_PATH = (
    Path(__file__).resolve().parents[1] / "assets" / "chevron_down_icon.svg"
).as_posix()


MAIN_WINDOW_STYLES = """
#windowRoot,
#rightPanel {
    background: #f8f9fb;
}
QWidget {
    color: #171b24;
    font-size: 10.5pt;
}

#dropArea {
    border: 2px dashed #c8ccd2;
    border-radius: 8px;
    background: #ffffff;
}
#dropArea[dragging="true"] {
    border-color: #4f8fdf;
    background: #f2f7ff;
}
#dropTitle {
    color: #151a24;
    font-size: 15pt;
    font-weight: 700;
}
#dropOr {
    color: #343943;
    font-size: 11pt;
}
#dropSubtitle {
    color: #727782;
    font-size: 9.5pt;
    line-height: 1.3;
}
#dropFileList {
    color: #303640;
    font-size: 10pt;
    border: 1px solid #e0e3e8;
    border-radius: 5px;
    background: #fbfcfd;
    outline: 0;
}
#dropFileList::item {
    min-height: 25px;
    padding: 2px 5px;
    background: transparent;
}

#optionsPanel,
#activityPanel,
#outputPanel {
    border: 1px solid #d9dce1;
    border-radius: 7px;
    background: #ffffff;
}
#sectionDivider {
    color: #e1e3e7;
    background: #e1e3e7;
    border: 0;
    max-height: 1px;
}
#sectionTitle {
    color: #181c24;
    font-size: 11.5pt;
    font-weight: 700;
}

QPushButton {
    min-height: 38px;
    padding: 5px 14px;
    border: 1px solid #cbd0d7;
    border-radius: 6px;
    color: #242933;
    background: #ffffff;
    font-size: 10.5pt;
    font-weight: 500;
}
QPushButton:hover {
    border-color: #9da5b0;
    background: #f7f8fa;
}
QPushButton:pressed {
    background: #eef0f3;
}
#primaryButton,
#clearButton {
    min-height: 44px;
    font-size: 12pt;
    font-weight: 600;
}
#primaryButton {
    color: #2f78d4;
    border-color: #7caeea;
    background: #f5f9ff;
}
#primaryButton:hover {
    border-color: #4f8fdf;
    background: #eaf3ff;
}
#primaryButton:pressed {
    background: #dfeeff;
}
#primaryButton:disabled {
    color: #8aaed8;
    border-color: #b9d0eb;
    background: #f5f8fc;
}
#clearButton {
    color: #ee444b;
    border-color: #f08a8f;
    background: #fff8f8;
}
#clearButton:hover {
    border-color: #ed5f66;
    background: #fff0f1;
}
#clearButton:pressed {
    background: #ffe4e6;
}
#browseButton,
#secondaryButton {
    color: #252a33;
    background: #ffffff;
}
#browseButton {
    min-width: 180px;
}

QCheckBox {
    min-height: 27px;
    spacing: 8px;
    font-size: 10.5pt;
}
QCheckBox:disabled {
    color: #9a9fa8;
}
#versionCombo {
    min-height: 34px;
    padding: 2px 36px 2px 10px;
    border: 1px solid #cbd0d7;
    border-radius: 5px;
    color: #252a33;
    background: #ffffff;
    font-size: 10.5pt;
}
#versionCombo:hover {
    border-color: #9da5b0;
}
#versionCombo::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 34px;
    border: 0;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    background: transparent;
}
#versionCombo::down-arrow {
    width: 12px;
    height: 8px;
    image: url("__ARROW_ICON_PATH__");
}
#versionCombo QAbstractItemView {
    padding: 3px;
    border: 1px solid #cbd0d7;
    border-radius: 4px;
    color: #252a33;
    background: #ffffff;
    selection-color: #ffffff;
    selection-background-color: #4f8fdf;
    outline: 0;
}

#consoleInfo {
    padding: 8px;
    border: 1px solid #d5d9df;
    border-radius: 6px;
    color: #2f3540;
    background: #ffffff;
    selection-color: #ffffff;
    selection-background-color: #4f8fdf;
    font-size: 9pt;
}
#outputPath {
    min-height: 38px;
    padding: 0 10px;
    border: 1px solid #cbd0d7;
    border-radius: 5px;
    color: #252a33;
    background: #ffffff;
    font-size: 10pt;
}
""".replace("__ARROW_ICON_PATH__", ARROW_ICON_PATH)
