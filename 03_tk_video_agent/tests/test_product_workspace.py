"""Tests for product-level workspace structure helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from helpers.product_workspace import (
    ASSET_DIRS,
    OUTPUT_DIRS,
    PUBLISH_DIRS,
    create_product_workspace,
    existing_global_flow_paths,
    resolve_product_workspace,
)


class ProductWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_product_workspace_generation_function_creates_structure(self) -> None:
        workspace = create_product_workspace(self.repo_root, "pet_nail_trimmer")

        self.assertTrue(workspace.product_brief.exists())
        for name in ASSET_DIRS:
            self.assertTrue((workspace.assets / name / ".gitkeep").exists())
        for name in OUTPUT_DIRS:
            self.assertTrue((workspace.outputs / name / ".gitkeep").exists())
        for name in PUBLISH_DIRS:
            self.assertTrue((workspace.publish / name / ".gitkeep").exists())

    def test_resolves_pet_nail_trimmer_paths(self) -> None:
        workspace = resolve_product_workspace(self.repo_root, "pet_nail_trimmer")

        self.assertEqual(workspace.root, self.repo_root / "products" / "pet_nail_trimmer")
        self.assertEqual(workspace.assets.name, "assets")
        self.assertEqual(workspace.outputs.name, "outputs")
        self.assertEqual(workspace.publish.name, "publish")

    def test_existing_global_inputs_outputs_compatibility_paths_remain(self) -> None:
        agent_root = self.repo_root / "03_tk_video_agent"
        paths = existing_global_flow_paths(agent_root)

        self.assertEqual(paths["inputs"], agent_root / "inputs")
        self.assertEqual(paths["outputs"], agent_root / "outputs")
        self.assertEqual(paths["raw_videos"], agent_root / "inputs" / "raw_videos")
        self.assertEqual(paths["renders"], agent_root / "outputs" / "renders")

    def test_no_external_api_dependency(self) -> None:
        workspace = create_product_workspace(self.repo_root, "dog_bath_hose")

        self.assertTrue(workspace.root.exists())


if __name__ == "__main__":
    unittest.main()
