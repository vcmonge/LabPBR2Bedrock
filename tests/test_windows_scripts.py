from __future__ import annotations

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUN_BAT = PROJECT_ROOT / "run.bat"
SETUP_BAT = PROJECT_ROOT / "windows_setup.bat"
SETUP_PS1 = PROJECT_ROOT / "scripts" / "windows_setup.ps1"
ABSOLUTE_PATH = re.compile(r"\b[A-Za-z]:[\\/]")


class WindowsScriptsTests(unittest.TestCase):
    def test_scripts_are_portable_ascii_with_crlf(self) -> None:
        for path in (RUN_BAT, SETUP_BAT, SETUP_PS1):
            with self.subTest(script=path.name):
                content = path.read_bytes()
                self.assertTrue(content.isascii())
                self.assertNotIn(b"\n", content.replace(b"\r\n", b""))
                self.assertIsNone(ABSOLUTE_PATH.search(content.decode("ascii")))

    def test_setup_bat_launches_ps1_from_its_own_folder(self) -> None:
        content = SETUP_BAT.read_text(encoding="ascii")

        self.assertIn(r'set "SETUP_SCRIPT=%APP_DIR%scripts\windows_setup.ps1"', content)
        self.assertIn('set "APP_DIR=%~dp0"', content)
        self.assertIn(
            'powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SETUP_SCRIPT%"',
            content,
        )
        self.assertIn("exit /b %SETUP_EXIT%", content)

    def test_setup_ps1_targets_local_venv_and_python_314(self) -> None:
        content = SETUP_PS1.read_text(encoding="ascii")

        self.assertIn("$AppDir = Split-Path -Parent $PSScriptRoot", content)
        self.assertIn("$PythonVersion = '3.14'", content)
        self.assertIn("'Scripts\\pythonw.exe'", content)
        self.assertIn("@('pip', 'install', '--python', $VenvPython, '-r', $Requirements)", content)
        self.assertIn("import PySide6, PIL, numpy", content)
        self.assertNotIn("Activate.ps1", content)

    def test_run_bat_points_to_setup_without_global_interpreter(self) -> None:
        content = RUN_BAT.read_text(encoding="ascii")

        self.assertIn("windows_setup.bat", content)
        self.assertIn(r"%APP_DIR%.venv\Scripts\pythonw.exe", content)
        self.assertIsNone(re.search(r"\bpy(thon)?(\.exe)?\s", content, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
