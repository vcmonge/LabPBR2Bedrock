# LabPBR2Bedrock

[![Español](https://img.shields.io/badge/lang-Español-blue)](README_ES.md)

**LabPBR to Bedrock Converter**

LabPBR2Bedrock is a desktop application for converting Minecraft Java PBR textures in LabPBR format into the PBR format supported by Minecraft Bedrock.

## Screenshot

![LabPBR2Bedrock](https://ik.imagekit.io/dmNtb25nZQ/LabPBR2Bedrock/LabPBR2Bedrockv3.webp?updatedAt=1789529312137)

It converts:

- Specular maps named `*_s.png` into MER maps named `*_mer.png`.
- Specular maps with subsurface scattering (SSS) into MERS maps named `*_mers.tga` when that option is enabled (the option becomes available when SSS is detected in the input texture).
- Normal maps named `*_n` into maps named `*_normal.png`.
- Optionally, it generates `*.texture_set.json` files for Minecraft Bedrock.

## Requirements

- Windows 10 or 11.
- Python 3.14 (the automatic setup downloads it if it is missing).

## Installation

### Automatic setup (recommended)

Double-click `windows_setup.bat`. The script:

1. Installs [uv](https://docs.astral.sh/uv/) if it is not available.
2. Downloads Python 3.14 with `uv` if it is not installed.
3. Creates the `.venv` virtual environment, or recreates it if it is incomplete or uses another Python version.
4. Installs the dependencies from `requirements.txt` and verifies that they can be imported.

When it finishes, start the application with `run.bat`. Running the setup again is safe: it only repeats the steps that are still missing.

### Manual setup

If you prefer to install everything yourself, choose one of the following methods. Run the commands in PowerShell from the project folder.

#### Option A: Python from python.org

1. Download and install Python 3.14 from [python.org](https://www.python.org/downloads/windows/). Make sure Python Launcher (`py`) is included in the installation.
2. Open a new PowerShell window and confirm that Python 3.14 is available:

   ```powershell
   py -3.14 --version
   ```

3. Create the virtual environment and install the dependencies:

   ```powershell
   py -3.14 -m venv .venv

   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

#### Option B: uv

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) :

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Open a new PowerShell window and confirm that uv is available:

   ```powershell
   uv --version
   ```

3. Download Python 3.14 if you do not have it yet:

   ```powershell
   uv python install 3.14
   ```

4. Create the virtual environment and install the dependencies:

   ```powershell
   uv venv --python 3.14 .venv

   uv pip install -r requirements.txt
   ```

#### Verify the installation

Both methods create the `.venv` virtual environment and install PySide6, Pillow, and NumPy. To confirm that the dependencies are available, run:

```powershell
.\.venv\Scripts\python.exe -c "import PySide6, PIL, numpy"
```

If the command finishes without errors, start the application with `run.bat`.

## Running the Application

### Option 1: Double-click

Double-click `run.bat`.

The script automatically locates `app.py` and the `.venv` environment relative to its own location. It does not launch the application if the virtual environment does not exist; in that case, run `windows_setup.bat` first.

### Option 2: PowerShell

```powershell
.\.venv\Scripts\python.exe app.py
```

## Usage

1. Drag files or folders into the main box, or use `Browse files...`.
2. Enable `Generate JSON` if you need `*.texture_set.json` files.
3. If the input contains SSS and you want to preserve it, enable `SSS`.
4. If a normal map contains height information and you want to preserve it, enable `POM`.
5. Select the output folder using `Change...` if necessary.
6. Click `Process images`.

When processing finishes, the console lists the converted and ignored files, along with any batch errors. The `Clear` button clears the pending inputs and the console.

## Supported Files

The application only accepts PNG and TGA images. Suffix matching is case-insensitive:

```text
stone_s.png
stone_n.png
stone_normal.png
```

Files that do not follow these patterns are listed as ignored. If both `stone_n` and `stone_normal` exist for the same texture, `stone_n` is used.

## PBR Options

- **SSS:** Becomes available when a specular map contains subsurface scattering after metalness exclusion. When enabled, textures that actually contain SSS are saved as MERS TGA files and, if JSON generation is enabled, use format `1.21.30`; all others remain in MER PNG format. Bedrock keeps the higher of metalness and SSS per pixel; a tie favors SSS.
- **POM:** Becomes available when a normal map contains height information in its alpha channel. When enabled, that height is copied into the Blue channel of `*_normal.png` for BetterRTX 1.5. Vanilla RTX and Vibrant Visuals treat Blue as the normal Z component; leave POM off to reconstruct Z instead.
- **Generate JSON:** Creates one `*.texture_set.json` file for each converted base name. Images with SSS use format `1.21.30`; all others use `1.16.100`.

## Output Folder

The folder selected using `Change...` is remembered between runs. The saved preference takes precedence over `--output-dir`.

## Example

Input files:

```text
stone_s.png
stone_n.png
```

Output files:

```text
stone_mer.png
stone_normal.png
stone.texture_set.json (optional)
```

Specular and normal maps that share the same base name are processed as a single texture and generate a single JSON file. Unpaired maps are also supported. For example:

Input:

```text
stone_s.png
dirt_n.png
cherry_leaves_s.png
```

Output:

```text
stone_mer.png
dirt_normal.png
cherry_leaves.tga

# (If the "Generate JSON" option was enabled)
stone.texture_set.json
dirt.texture_set.json
cherry_leaves.texture_set.json
```

## Notes

- The original input files are not modified or deleted.

## Acknowledgements

The LabPBR-to-Bedrock PBR conversion logic in `mer_converter.py` and `normal_converter.py` was was adapted from portions of [JE2BE Resource Pack Converter](https://github.com/Seraphic-Studio/JE2BE-Resource-Pack-Converter) by the JE2BE Team.

The implementation in this project has since been substantially modified and
extended.

JE2BE Resource Pack Converter is licensed under the MIT License.
See `THIRD_PARTY_LICENSES.md` for the original copyright notice and license.
