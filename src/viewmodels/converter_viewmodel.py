from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from src.models import (
    MER_JSON_VERSION,
    MERS_JSON_VERSION,
    SUPPORTED_JSON_VERSIONS,
    AppState,
    ConversionOptions,
    ConversionSummary,
    TextureCapabilities,
)
from src.services import (
    ConversionService,
    PreferencesService,
    TextureAnalysisService,
)


class ConverterViewModel(QObject):
    """Observable application state and presentation-independent rules."""

    paths_changed = Signal(object)
    capabilities_changed = Signal(object)
    options_changed = Signal(object)
    output_dir_changed = Signal(str)
    status_changed = Signal(str)
    processing_changed = Signal(bool)
    conversion_completed = Signal(object)
    notification_requested = Signal(str, str, str)

    def __init__(
        self,
        preferences: PreferencesService,
        analysis: TextureAnalysisService,
        conversion: ConversionService,
        fallback_output_dir: Path,
        template_dir: Path,
    ) -> None:
        super().__init__()
        self._preferences = preferences
        self._analysis = analysis
        self._conversion = conversion
        self._template_dir = template_dir
        self._state = AppState(
            output_dir=preferences.load_output_dir(fallback_output_dir),
        )
        self._capabilities = TextureCapabilities()
        self._status = ""

    @property
    def input_paths(self) -> list[Path]:
        return list(self._state.input_paths)

    @property
    def capabilities(self) -> TextureCapabilities:
        return self._capabilities

    @property
    def output_dir(self) -> Path | None:
        return self._state.output_dir

    @property
    def options(self) -> ConversionOptions:
        return ConversionOptions(
            generate_json=self._state.generate_json,
            json_version=self._state.json_version,
            pom_enabled=self._state.pom_enabled,
            sss_enabled=self._state.sss_enabled,
        )

    @property
    def status(self) -> str:
        return self._status

    def _set_status(self, status: str) -> None:
        self._status = status
        self.status_changed.emit(status)

    @staticmethod
    def _path_key(path: Path) -> str:
        try:
            resolved = path.expanduser().resolve(strict=False)
        except (OSError, RuntimeError, ValueError):
            resolved = path
        return str(resolved).casefold()

    def add_paths(self, paths: list[str]) -> None:
        known = {self._path_key(path) for path in self._state.input_paths}
        added = 0
        rejected = 0

        for raw_path in paths:
            path = Path(raw_path)
            if not self._analysis.accepts_input_path(path):
                rejected += 1
                continue
            key = self._path_key(path)
            if key in known:
                continue
            self._state.input_paths.append(path)
            known.add(key)
            added += 1

        if added:
            self.paths_changed.emit(self.input_paths)
        self._reanalyze()

        if added == 0 and paths:
            if rejected:
                self._set_status(
                    "No new supported files were added. Use PNG or TGA."
                )
            else:
                self._set_status("The inputs were already in the list.")
        else:
            status = (
                f"{len(self._state.input_paths)} input(s) ready to process."
            )
            if rejected:
                status += f" Skipped due to format: {rejected}."
            self._set_status(status)

    def _clear_input_paths(self) -> None:
        self._state.input_paths.clear()
        self.paths_changed.emit(self.input_paths)
        self._reanalyze()

    def clear_paths(self) -> None:
        self._clear_input_paths()
        self._set_status("List cleared.")

    def clear_all(self) -> None:
        """Clear pending inputs and the console without resetting user preferences."""
        self._clear_input_paths()
        self._set_status("")

    def _reanalyze(self) -> None:
        self._capabilities = self._analysis.analyze(self._state.input_paths)
        options_changed = False

        if not self._capabilities.pom_available and self._state.pom_enabled:
            self._state.pom_enabled = False
            options_changed = True
        if not self._capabilities.sss_available and self._state.sss_enabled:
            self._state.sss_enabled = False
            options_changed = True

        expected_version = self._json_version_for_sss()
        if self._state.json_version != expected_version:
            self._state.json_version = expected_version
            options_changed = True

        self.capabilities_changed.emit(self._capabilities)
        if options_changed:
            self.options_changed.emit(self.options)

    def set_generate_json(self, enabled: bool) -> None:
        self._state.generate_json = bool(enabled)
        self.options_changed.emit(self.options)

    def set_json_version(self, version: str) -> None:
        if version == MERS_JSON_VERSION and self._capabilities.sss_available:
            self._state.sss_enabled = True
        elif version == MER_JSON_VERSION:
            self._state.sss_enabled = False
        self._state.json_version = self._json_version_for_sss()
        self.options_changed.emit(self.options)

    def set_pom_enabled(self, enabled: bool) -> None:
        self._state.pom_enabled = bool(enabled) and self._capabilities.pom_available
        self.options_changed.emit(self.options)

    def set_sss_enabled(self, enabled: bool) -> None:
        self._state.sss_enabled = bool(enabled) and self._capabilities.sss_available
        self._state.json_version = self._json_version_for_sss()
        self.options_changed.emit(self.options)

    def _json_version_for_sss(self) -> str:
        return (
            MERS_JSON_VERSION
            if self._state.sss_enabled
            else MER_JSON_VERSION
        )

    @staticmethod
    def _format_summary(summary: ConversionSummary, output_dir: Path) -> str:
        lines = [f"Converted: {len(summary.converted)}"]
        lines.extend(
            (
                f"- {item.source.name} -> {item.output_path.name}"
                + (
                    f" (JSON: {item.json_path.name})"
                    if item.json_path is not None
                    else ""
                )
            )
            for item in summary.converted
        )

        lines.append(f"Ignored: {len(summary.ignored)}")
        lines.extend(f"- {path.name}" for path in summary.ignored)

        lines.append(f"Errors: {len(summary.errors)}")
        lines.extend(f"- {error}" for error in summary.errors)
        lines.append(f"Output: {output_dir}")
        return "\n".join(lines)

    def change_output_dir(self, dir_path: str) -> bool:
        output_dir = self._preferences.parse_output_path(dir_path)
        if output_dir is None:
            self.notification_requested.emit(
                "warning",
                "Invalid output path",
                "The selected folder could not be interpreted as a valid Windows path.",
            )
            return False

        self._state.output_dir = output_dir
        self.output_dir_changed.emit(str(output_dir))
        try:
            self._preferences.save_output_dir(output_dir)
        except OSError as exc:
            self.notification_requested.emit(
                "warning",
                "Could not save the path",
                (
                    "The selected output will be used for this session, but "
                    f"options.txt could not be written.\n\n{exc}"
                ),
            )
            self._set_status("Output path updated for this session only.")
            return True

        self._set_status("Default output path saved.")
        return True

    def process(self) -> ConversionSummary | None:
        if not self._state.input_paths:
            self.notification_requested.emit(
                "information",
                "No inputs",
                "Drag files or folders here before processing.",
            )
            return None

        self._reanalyze()
        output_dir = self._state.output_dir
        if output_dir is None:
            self.notification_requested.emit(
                "warning",
                "Invalid output path",
                (
                    "The path saved in options.txt is empty or could not be interpreted. "
                    "Select a valid output folder."
                ),
            )
            return None

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.notification_requested.emit(
                "warning",
                "Invalid output path",
                f"The output path cannot be used:\n{output_dir}\n\n{exc}",
            )
            return None

        options = self.options
        if (
            options.generate_json
            and options.json_version not in SUPPORTED_JSON_VERSIONS
        ):
            self.notification_requested.emit(
                "warning",
                "Invalid version",
                "Select a valid JSON version.",
            )
            return None

        self.processing_changed.emit(True)
        self._set_status("Processing images...")
        try:
            summary = self._conversion.convert(
                self.input_paths,
                output_dir,
                self._template_dir,
                options,
            )
        except Exception as exc:
            self._set_status("The conversion could not be completed.")
            self.notification_requested.emit(
                "critical",
                "Conversion error",
                str(exc),
            )
            return None
        finally:
            self.processing_changed.emit(False)

        self._clear_input_paths()
        self._set_status(self._format_summary(summary, output_dir))
        self.conversion_completed.emit(summary)
        return summary
