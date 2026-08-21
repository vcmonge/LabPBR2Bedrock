from __future__ import annotations

from pathlib import Path


OPTIONS_FILE_NAME = "options.txt"
OPTIONS_PATH_PREFIX = "path:"
OPTIONS_ENCODINGS = ("utf-8-sig", "mbcs", "cp1252")


def decode_options_text(data: bytes) -> str:
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return data.decode("utf-16")
        except UnicodeError:
            pass

    for encoding in OPTIONS_ENCODINGS:
        try:
            return data.decode(encoding)
        except (LookupError, UnicodeError):
            continue

    return data.decode("utf-8", errors="replace")


def path_from_options_value(raw_path: str) -> Path | None:
    if not raw_path or not raw_path.strip() or "\x00" in raw_path:
        return None

    try:
        path = Path(raw_path).expanduser()
        return path.resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        try:
            return Path(raw_path).expanduser()
        except (OSError, RuntimeError, ValueError):
            return None


class PreferencesService:
    """Load and persist local application preferences."""

    def __init__(self, app_dir: Path) -> None:
        self._app_dir = app_dir

    @property
    def options_path(self) -> Path:
        return self._app_dir / OPTIONS_FILE_NAME

    @staticmethod
    def parse_output_path(raw_path: str) -> Path | None:
        return path_from_options_value(raw_path)

    def load_output_dir(self, fallback: Path) -> Path | None:
        if not self.options_path.exists():
            return fallback

        try:
            options_text = decode_options_text(self.options_path.read_bytes())
        except OSError:
            return fallback

        for line in options_text.splitlines():
            option_line = line.removeprefix("\ufeff").lstrip(" \t")
            if option_line.casefold().startswith(OPTIONS_PATH_PREFIX):
                raw_path = option_line[len(OPTIONS_PATH_PREFIX) :].lstrip(" \t")
                return path_from_options_value(raw_path)

        return fallback

    def save_output_dir(self, output_dir: Path) -> None:
        temp_path = self.options_path.with_name(f"{OPTIONS_FILE_NAME}.tmp")
        options_text = f"{OPTIONS_PATH_PREFIX} {output_dir}\n"

        try:
            temp_path.write_text(options_text, encoding="utf-8", newline="\n")
            temp_path.replace(self.options_path)
        except OSError:
            try:
                temp_path.unlink()
            except OSError:
                pass
            raise
