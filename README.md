# LabPBR2Bedrock

[![Español](https://img.shields.io/badge/lang-Español-blue)](README_ES.md)

**LabPBR to Bedrock Converter**

LabPBR2Bedrock is a desktop application for converting Minecraft Java PBR textures in LabPBR format into the PBR format supported by Minecraft Bedrock.

## Screenshot

![LabPBR2Bedrock](https://ik.imagekit.io/dmNtb25nZQ/LabPBR2Bedrock/LabPBR2Bedrock_2.webp?updatedAt=1789085586859)

It converts:

- Specular maps named `*_s.png` into MER maps named `*_mer.png`.
- Specular maps with subsurface scattering (SSS) into MERS maps named `*_mers.tga` when that option is enabled (the option becomes available when SSS is detected in the input texture).
- Normal maps named `*_n` into maps named `*_normal.png`.
- Optionally, it generates `*.texture_set.json` files for Minecraft Bedrock.

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

## Requirements

- Windows 10 or 11.
- Python 3.14.

## Installation

Open PowerShell in the project folder and choose one of the following methods.

### Using Python Launcher

If you installed Python from python.org and have Python Launcher (`py`) available, run:

```powershell
py -3.14 -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Using uv

Alternatively, if you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed, run:

```powershell
uv venv --python 3.14 .venv

uv pip install -r requirements.txt
```

`uv` can download Python 3.14 automatically if it is not already installed. Both methods create the `.venv` virtual environment and install PySide6, Pillow, and NumPy.

## Running the Application

### Option 1: Double-click

Double-click `run.bat`.

The script automatically locates `app.py` and the `.venv` environment relative to its own location. It does not launch the application if the virtual environment does not exist.

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

- **SSS:** Becomes available when a specular map contains subsurface scattering. When enabled, textures that actually contain SSS are saved as MERS TGA files and, if JSON generation is enabled, use format `1.21.30`; all others remain in MER PNG format.
- **POM:** Becomes available when a normal map contains height information in its alpha channel.
- **Generate JSON:** Creates one `*.texture_set.json` file for each converted base name. Images with SSS use format `1.21.30`; all others use `1.16.100`.

## Output Folder

The folder selected using `Change...` is remembered between runs. The saved preference takes precedence over `--output-dir`.

## Notes

- The original input files are not modified or deleted.

## Acknowledgements

The LabPBR-to-Bedrock PBR conversion logic in `mer_converter.py` and `normal_converter.py` was was adapted from portions of [JE2BE Resource Pack Converter](https://github.com/Seraphic-Studio/JE2BE-Resource-Pack-Converter) by the JE2BE Team.

The implementation in this project has since been substantially modified and
extended.

JE2BE Resource Pack Converter is licensed under the MIT License.
See `THIRD_PARTY_LICENSES.md` for the original copyright notice and license.
