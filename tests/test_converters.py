from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

import src.converters.mer_converter as mer_converter
from src.converters.mer_converter import (
    EMISSIVE_LUT,
    METALNESS_LUT,
    ROUGHNESS_LUT,
    SSS_LUT,
    convert_specular_to_mer,
    has_subsurface_scattering,
)
from src.converters.normal_converter import (
    NORMAL_Z_LUT,
    convert_normal_to_bedrock,
    has_parallax_occlusion_mapping,
    is_java_normal,
    normal_texture_base_name,
)
from src.converters.texture_set_converter import create_texture_set_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PROJECT_ROOT / "json"


def save_rgba(
    path: Path,
    pixels: list[tuple[int, int, int, int]] | None = None,
) -> None:
    pixel_values = pixels or [(128, 128, 0, 255)]
    image = Image.new("RGBA", (len(pixel_values), 1))
    image.putdata(pixel_values)
    image.save(path)


class NormalConverterTests(unittest.TestCase):
    def test_normal_z_lut_matches_original_formula_for_all_inputs(self) -> None:
        values = np.arange(256, dtype=np.uint8)
        normal_x, normal_y = np.meshgrid(values, values)
        nx_normalized = (normal_x / 255.0) * 2.0 - 1.0
        ny_normalized = (normal_y / 255.0) * 2.0 - 1.0
        nz_squared = 1.0 - (nx_normalized**2 + ny_normalized**2)
        expected = np.clip(
            np.rint((np.sqrt(np.maximum(0.0, nz_squared)) + 1.0) * 127.5),
            0,
            255,
        ).astype(np.uint8)

        self.assertEqual(NORMAL_Z_LUT.shape, (256, 256))
        self.assertEqual(NORMAL_Z_LUT.dtype, np.uint8)
        np.testing.assert_array_equal(NORMAL_Z_LUT[normal_y, normal_x], expected)

    def test_detects_supported_normal_names_case_insensitively(self) -> None:
        cases = {
            "stone_n.png": "stone",
            "stone_NORMAL.PNG": "stone",
            "sand_n.tga": "sand",
            "oak_NORMAL.TGA": "oak",
        }

        for filename, expected_base in cases.items():
            with self.subTest(filename=filename):
                path = Path(filename)
                self.assertTrue(is_java_normal(path))
                self.assertEqual(normal_texture_base_name(path), expected_base)

        for filename in (
            "stone_s.png",
            "oak_n.jpg",
            "brick_normal.jpeg",
            "stone_normal.gif",
            "normal.png",
        ):
            with self.subTest(filename=filename):
                self.assertFalse(is_java_normal(Path(filename)))

    def test_detects_pom_from_non_opaque_alpha(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            rgb_source = root / "rgb_n.png"
            opaque_source = root / "opaque_n.png"
            pom_source = root / "pom_n.png"
            Image.new("RGB", (1, 1), (128, 128, 0)).save(rgb_source)
            save_rgba(opaque_source, [(128, 128, 0, 255)])
            save_rgba(pom_source, [(128, 128, 0, 254)])

            self.assertFalse(has_parallax_occlusion_mapping(rgb_source))
            self.assertFalse(has_parallax_occlusion_mapping(opaque_source))
            self.assertTrue(has_parallax_occlusion_mapping(pom_source))

    def test_reconstructs_z_and_writes_rgb_png(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "stone_n.png"
            save_rgba(source, [(128, 128, 7, 23), (255, 128, 200, 42)])

            output_path = convert_normal_to_bedrock(source, root / "output")

            self.assertEqual(output_path.name, "stone_normal.png")
            with Image.open(output_path) as converted:
                self.assertEqual(converted.mode, "RGB")
                self.assertEqual(
                    [converted.getpixel((x, 0)) for x in range(converted.width)],
                    [(128, 128, 255), (255, 128, 128)],
                )

    def test_pom_copies_input_alpha_to_output_blue(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "stone_n.png"
            save_rgba(source, [(128, 128, 7, 23), (255, 128, 200, 42)])

            with patch("src.converters.normal_converter.NORMAL_Z_LUT", None):
                output_path = convert_normal_to_bedrock(
                    source,
                    root / "output",
                    pom_enabled=True,
                )

            with Image.open(output_path) as converted:
                self.assertEqual(
                    [converted.getpixel((x, 0)) for x in range(converted.width)],
                    [(128, 128, 23), (255, 128, 42)],
                )

    def test_pom_option_reconstructs_z_when_height_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "stone_n.png"
            save_rgba(source, [(128, 128, 7, 255)])

            output_path = convert_normal_to_bedrock(
                source,
                root / "output",
                pom_enabled=True,
            )

            with Image.open(output_path) as converted:
                self.assertEqual(converted.getpixel((0, 0)), (128, 128, 255))


class SpecularConverterTests(unittest.TestCase):
    def test_mer_luts_match_original_formulas_for_all_inputs(self) -> None:
        values = np.arange(256, dtype=np.uint8)
        expected_roughness = (255 - values).astype(np.uint8)
        expected_metalness = np.zeros(256, dtype=np.uint8)
        expected_metalness[mer_converter.METAL_ID_MIN_VALUE :] = 255
        expected_emissive = np.zeros(256, dtype=np.uint8)
        emission_values = values[: mer_converter.EMISSION_MAX_VALUE + 1]
        expected_emissive[: mer_converter.EMISSION_MAX_VALUE + 1] = np.rint(
            emission_values.astype(np.float64)
            * 255.0
            / mer_converter.EMISSION_MAX_VALUE
        ).astype(np.uint8)
        expected_sss = np.zeros(256, dtype=np.uint8)
        sss_values = values[mer_converter.SSS_MIN_VALUE + 1 :]
        expected_sss[mer_converter.SSS_MIN_VALUE + 1 :] = np.rint(
            (sss_values.astype(np.float64) - mer_converter.SSS_MIN_VALUE)
            * 255.0
            / mer_converter.SSS_VALUE_RANGE
        ).astype(np.uint8)

        for lut, expected in (
            (ROUGHNESS_LUT, expected_roughness),
            (METALNESS_LUT, expected_metalness),
            (EMISSIVE_LUT, expected_emissive),
            (SSS_LUT, expected_sss),
        ):
            with self.subTest(lut=lut):
                self.assertEqual(lut.shape, (256,))
                self.assertEqual(lut.dtype, np.uint8)
                np.testing.assert_array_equal(lut, expected)

    def test_detects_sss_at_blue_channel_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            no_sss_path = root / "stone_s.png"
            sss_path = root / "leaves_s.png"
            save_rgba(no_sss_path, [(0, 0, 65, 255), (0, 230, 255, 255)])
            save_rgba(sss_path, [(0, 0, 65, 255), (0, 229, 66, 255)])

            self.assertFalse(has_subsurface_scattering(no_sss_path))
            self.assertTrue(has_subsurface_scattering(sss_path))

    def test_converts_specular_channels_to_bedrock_ranges(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "stone_s.png"
            save_rgba(
                source,
                [(192, 229, 0, 254), (0, 230, 0, 255), (255, 11, 0, 127)],
            )

            output_path = convert_specular_to_mer(source, root / "output")

            with Image.open(output_path) as converted:
                self.assertEqual(
                    [converted.getpixel((x, 0)) for x in range(converted.width)],
                    [(0, 255, 63), (255, 0, 255), (0, 128, 0)],
                )

    def test_sss_writes_normalized_alpha_to_32_bit_rgba_tga(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "leaves_s.png"
            save_rgba(
                source,
                [(0, 0, 64, 12), (0, 0, 65, 12), (0, 0, 160, 12), (0, 0, 255, 12)],
            )

            output_path = convert_specular_to_mer(
                source,
                root / "output",
                sss_enabled=True,
            )

            self.assertEqual(output_path.name, "leaves_mers.tga")
            self.assertEqual(output_path.read_bytes()[16], 32)
            with Image.open(output_path) as converted:
                self.assertEqual(converted.format, "TGA")
                self.assertEqual(converted.mode, "RGBA")
                self.assertEqual(
                    [converted.getpixel((x, 0)) for x in range(converted.width)],
                    [
                        (0, 12, 255, 0),
                        (0, 12, 255, 0),
                        (0, 12, 255, 128),
                        (0, 12, 255, 255),
                    ],
                )

    def test_sss_is_zero_for_metal_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "mixed_s.png"
            save_rgba(source, [(0, 230, 255, 255), (0, 229, 255, 255)])

            output_path = convert_specular_to_mer(
                source,
                root / "output",
                sss_enabled=True,
            )

            with Image.open(output_path) as converted:
                self.assertEqual(
                    [converted.getpixel((x, 0)) for x in range(converted.width)],
                    [(255, 0, 255, 0), (0, 0, 255, 255)],
                )

    def test_disabled_or_absent_sss_keeps_rgb_png_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sss_source = root / "leaves_s.png"
            no_sss_source = root / "stone_s.png"
            metallic_source = root / "iron_s.png"
            save_rgba(sss_source, [(0, 0, 255, 12)])
            save_rgba(no_sss_source, [(0, 0, 64, 12)])
            save_rgba(metallic_source, [(0, 230, 255, 12)])

            outputs = (
                convert_specular_to_mer(sss_source, root / "disabled"),
                convert_specular_to_mer(
                    no_sss_source,
                    root / "absent",
                    sss_enabled=True,
                ),
                convert_specular_to_mer(
                    metallic_source,
                    root / "metallic",
                    sss_enabled=True,
                ),
            )

            for output_path in outputs:
                with self.subTest(output_path=output_path), Image.open(
                    output_path
                ) as converted:
                    self.assertEqual(output_path.suffix, ".png")
                    self.assertEqual(converted.mode, "RGB")

    def test_alternate_output_extension_is_left_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_dir = root / "output"
            output_dir.mkdir()
            source = root / "leaves_s.png"
            existing_png = output_dir / "leaves_mer.png"
            save_rgba(existing_png, [(1, 2, 3, 4)])
            original_png = existing_png.read_bytes()
            save_rgba(source, [(0, 0, 255, 12)])

            tga_output = convert_specular_to_mer(
                source,
                output_dir,
                sss_enabled=True,
            )

            self.assertEqual(tga_output.suffix, ".tga")
            self.assertEqual(existing_png.read_bytes(), original_png)
            original_tga = tga_output.read_bytes()
            save_rgba(source, [(0, 0, 64, 12)])
            png_output = convert_specular_to_mer(
                source,
                output_dir,
                sss_enabled=True,
            )
            self.assertEqual(png_output.suffix, ".png")
            self.assertEqual(tga_output.read_bytes(), original_tga)


class TextureSetConverterTests(unittest.TestCase):
    def test_renders_and_validates_versioned_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"

            json_path = create_texture_set_json(
                "stone",
                output_dir,
                TEMPLATE_DIR,
                "1.16.100",
            )

            data = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(json_path.name, "stone.texture_set.json")
            self.assertEqual(data["format_version"], "1.16.100")
            self.assertEqual(
                data["minecraft:texture_set"]["normal"],
                "stone_normal",
            )

    def test_rejects_unsupported_version_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"

            with self.assertRaisesRegex(ValueError, "Unsupported texture set version"):
                create_texture_set_json(
                    "stone",
                    output_dir,
                    TEMPLATE_DIR,
                    "invalid",
                )

            self.assertFalse(output_dir.exists())

    def test_rejects_rendered_template_that_is_not_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template_dir = root / "templates"
            template_dir.mkdir()
            (template_dir / "1.16.100.texture_set.json").write_text(
                '{"normal": "{$nombre}_normal"',
                encoding="utf-8",
            )

            with self.assertRaises(json.JSONDecodeError):
                create_texture_set_json(
                    "stone",
                    root / "output",
                    template_dir,
                    "1.16.100",
                )

            self.assertFalse((root / "output").exists())


if __name__ == "__main__":
    unittest.main()
