from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from src.converters.texture_set_converter import create_texture_set_json
from src.models import ConversionOptions
from src.services import ConversionService


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


class ConversionServiceIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.inputs = self.root / "inputs"
        self.output = self.root / "output"
        self.inputs.mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def convert(
        self,
        generate_json: bool = True,
        version: str = "1.16.100",
        pom_enabled: bool = False,
        sss_enabled: bool = False,
    ):
        return ConversionService().convert(
            [self.inputs],
            self.output,
            TEMPLATE_DIR,
            ConversionOptions(
                generate_json=generate_json,
                json_version=version,
                pom_enabled=pom_enabled,
                sss_enabled=sss_enabled,
            ),
        )

    def test_matching_specular_and_short_normal_share_one_json(self) -> None:
        save_rgba(self.inputs / "stone_s.png", [(0, 230, 0, 12)])
        save_rgba(self.inputs / "stone_n.png")

        with patch(
            "src.services.conversion_service.create_texture_set_json",
            wraps=create_texture_set_json,
        ) as create_json:
            summary = self.convert()

        self.assertEqual(len(summary.converted), 2)
        self.assertEqual(summary.ignored, [])
        self.assertEqual(summary.errors, [])
        self.assertEqual(create_json.call_count, 1)
        self.assertEqual(
            {item.output_path.name for item in summary.converted},
            {"stone_mer.png", "stone_normal.png"},
        )
        self.assertEqual(
            {item.texture_type for item in summary.converted},
            {"specular", "normal"},
        )
        self.assertEqual(
            {item.json_path for item in summary.converted},
            {self.output / "stone.texture_set.json"},
        )

    def test_matching_long_normal_suffix_uses_canonical_output_name(self) -> None:
        save_rgba(self.inputs / "stone_s.png")
        save_rgba(self.inputs / "stone_normal.png")

        summary = self.convert(generate_json=False)

        self.assertEqual(summary.errors, [])
        self.assertEqual(
            {item.output_path.name for item in summary.converted},
            {"stone_mer.png", "stone_normal.png"},
        )

    def test_pom_is_applied_to_unpaired_normal(self) -> None:
        save_rgba(self.inputs / "stone_n.png", [(128, 128, 0, 37)])

        summary = self.convert(generate_json=False, pom_enabled=True)

        self.assertEqual(summary.errors, [])
        with Image.open(self.output / "stone_normal.png") as converted:
            self.assertEqual(converted.getpixel((0, 0)), (128, 128, 37))

    def test_specular_input_does_not_prevent_pom_from_being_applied(self) -> None:
        save_rgba(self.inputs / "stone_s.png", [(0, 0, 66, 12)])
        save_rgba(self.inputs / "stone_n.png", [(128, 128, 0, 37)])

        summary = self.convert(
            generate_json=False,
            pom_enabled=True,
            sss_enabled=True,
        )

        self.assertEqual(summary.errors, [])
        self.assertTrue((self.output / "stone_mers.tga").exists())
        with Image.open(self.output / "stone_normal.png") as converted:
            self.assertEqual(converted.getpixel((0, 0)), (128, 128, 37))

    def test_mixed_pom_batch_selects_normal_flow_per_texture(self) -> None:
        save_rgba(self.inputs / "brick_n.png", [(128, 128, 0, 37)])
        save_rgba(self.inputs / "stone_n.png", [(128, 128, 0, 255)])

        summary = self.convert(generate_json=False, pom_enabled=True)

        self.assertEqual(summary.errors, [])
        with Image.open(self.output / "brick_normal.png") as converted:
            self.assertEqual(converted.getpixel((0, 0)), (128, 128, 37))
        with Image.open(self.output / "stone_normal.png") as converted:
            self.assertEqual(converted.getpixel((0, 0)), (128, 128, 255))

    def test_different_bases_form_independent_groups(self) -> None:
        save_rgba(self.inputs / "stone_s.png")
        save_rgba(self.inputs / "dirt_n.png")

        with patch(
            "src.services.conversion_service.create_texture_set_json",
            wraps=create_texture_set_json,
        ) as create_json:
            summary = self.convert()

        self.assertEqual(len(summary.converted), 2)
        self.assertEqual(summary.errors, [])
        self.assertEqual(create_json.call_count, 2)
        self.assertTrue((self.output / "stone.texture_set.json").exists())
        self.assertTrue((self.output / "dirt.texture_set.json").exists())

    def test_short_normal_suffix_wins_over_long_suffix(self) -> None:
        save_rgba(self.inputs / "stone_n.png", [(128, 128, 0, 255)])
        save_rgba(self.inputs / "stone_normal.png", [(255, 128, 0, 255)])

        summary = self.convert(generate_json=False)

        self.assertEqual(len(summary.converted), 1)
        self.assertEqual(summary.converted[0].source.name, "stone_n.png")
        self.assertEqual(
            [path.name for path in summary.ignored],
            ["stone_normal.png"],
        )
        with Image.open(self.output / "stone_normal.png") as converted:
            self.assertEqual(converted.getpixel((0, 0))[:2], (128, 128))

    def test_corrupt_member_does_not_block_other_member_or_json(self) -> None:
        save_rgba(self.inputs / "stone_s.png")
        (self.inputs / "stone_n.png").write_bytes(b"not an image")

        summary = self.convert()

        self.assertEqual(len(summary.converted), 1)
        self.assertEqual(summary.converted[0].texture_type, "specular")
        self.assertEqual(len(summary.errors), 1)
        self.assertTrue((self.output / "stone_mer.png").exists())
        self.assertTrue((self.output / "stone.texture_set.json").exists())

    def test_json_failure_keeps_successful_image_conversions(self) -> None:
        save_rgba(self.inputs / "stone_s.png")
        save_rgba(self.inputs / "stone_n.png")

        with patch(
            "src.services.conversion_service.create_texture_set_json",
            side_effect=OSError("read-only template"),
        ):
            summary = self.convert()

        self.assertEqual(len(summary.converted), 2)
        self.assertTrue(all(item.json_path is None for item in summary.converted))
        self.assertEqual(len(summary.errors), 1)
        self.assertTrue((self.output / "stone_mer.png").exists())
        self.assertTrue((self.output / "stone_normal.png").exists())

    def test_specular_conversion_regression(self) -> None:
        save_rgba(self.inputs / "stone_s.png", [(0, 230, 99, 12)])

        summary = self.convert(generate_json=False)

        self.assertEqual(summary.errors, [])
        with Image.open(self.output / "stone_mer.png") as converted:
            self.assertEqual(converted.mode, "RGB")
            self.assertEqual(converted.getpixel((0, 0)), (255, 12, 255))

    def test_mixed_sss_batch_selects_output_format_and_json_per_texture(self) -> None:
        save_rgba(self.inputs / "leaves_s.png", [(0, 0, 66, 12)])
        save_rgba(self.inputs / "stone_s.png", [(0, 0, 64, 12)])

        summary = self.convert(version="1.21.30", sss_enabled=True)

        self.assertEqual(summary.errors, [])
        self.assertEqual(
            {item.output_path.name for item in summary.converted},
            {"leaves_mers.tga", "stone_mer.png"},
        )
        leaves_data = json.loads(
            (self.output / "leaves.texture_set.json").read_text(encoding="utf-8")
        )
        stone_data = json.loads(
            (self.output / "stone.texture_set.json").read_text(encoding="utf-8")
        )
        self.assertEqual(leaves_data["format_version"], "1.21.30")
        self.assertEqual(
            leaves_data["minecraft:texture_set"]
            ["metalness_emissive_roughness_subsurface"],
            "leaves_mers",
        )
        self.assertEqual(stone_data["format_version"], "1.16.100")
        self.assertEqual(
            stone_data["minecraft:texture_set"]
            ["metalness_emissive_roughness"],
            "stone_mer",
        )

    def test_metal_sss_tie_writes_mers_and_clears_metalness(self) -> None:
        save_rgba(self.inputs / "wax_s.png", [(0, 230, 255, 12)])

        summary = self.convert(version="1.21.30", sss_enabled=True)

        self.assertEqual(summary.errors, [])
        self.assertEqual(summary.converted[0].output_path.name, "wax_mers.tga")
        with Image.open(self.output / "wax_mers.tga") as converted:
            self.assertEqual(converted.getpixel((0, 0)), (0, 12, 255, 255))
        data = json.loads(
            (self.output / "wax.texture_set.json").read_text(encoding="utf-8")
        )
        self.assertEqual(data["format_version"], "1.21.30")

    def test_sss_uses_mers_name_in_output_and_121_json(self) -> None:
        save_rgba(self.inputs / "leaves_s.png", [(0, 0, 66, 12)])

        summary = self.convert(version="1.21.30", sss_enabled=True)

        self.assertEqual(summary.errors, [])
        self.assertEqual(summary.converted[0].output_path.name, "leaves_mers.tga")
        data = json.loads(
            (self.output / "leaves.texture_set.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            data["minecraft:texture_set"]
            ["metalness_emissive_roughness_subsurface"],
            "leaves_mers",
        )

    def test_unpaired_normal_uses_116_mer_json(self) -> None:
        save_rgba(self.inputs / "stone_n.png")

        summary = self.convert(version="1.21.30")

        self.assertEqual(summary.errors, [])
        json_path = self.output / "stone.texture_set.json"
        data = json.loads(json_path.read_text(encoding="utf-8"))
        texture_set = data["minecraft:texture_set"]
        self.assertEqual(data["format_version"], "1.16.100")
        self.assertEqual(
            texture_set["metalness_emissive_roughness"],
            "stone_mer",
        )
        self.assertEqual(texture_set["normal"], "stone_normal")


if __name__ == "__main__":
    unittest.main()
