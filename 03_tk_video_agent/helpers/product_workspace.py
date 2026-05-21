"""Product-level workspace structure helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ASSET_DIRS = (
    "raw_videos",
    "product_images",
    "ai_generated_clips",
    "reference_videos",
    "scripts",
)

OUTPUT_DIRS = (
    "material_inventory",
    "material_pack",
    "edit_strategy",
    "timelines",
    "subtitles",
    "renders",
    "reports",
)

PUBLISH_DIRS = (
    "publish_records",
    "performance_feedback",
)


@dataclass(frozen=True)
class ProductWorkspace:
    """Resolved paths for a product-specific workspace."""

    slug: str
    root: Path
    product_brief: Path
    assets: Path
    outputs: Path
    publish: Path


def repo_root_from_agent_root(agent_root: Path | str) -> Path:
    """Resolve repository root from the 03_tk_video_agent directory."""
    return Path(agent_root).resolve().parent


def resolve_product_workspace(repo_root: Path | str, product_slug: str) -> ProductWorkspace:
    """Resolve product workspace paths without creating files."""
    root = Path(repo_root) / "products" / product_slug
    return ProductWorkspace(
        slug=product_slug,
        root=root,
        product_brief=root / "product_brief.md",
        assets=root / "assets",
        outputs=root / "outputs",
        publish=root / "publish",
    )


def require_product_workspace(repo_root: Path | str, product_slug: str) -> ProductWorkspace:
    """Resolve an existing product workspace or raise a clear error."""
    workspace = resolve_product_workspace(repo_root, product_slug)
    if not workspace.root.exists():
        raise FileNotFoundError(f"Product workspace not found: products/{product_slug}")
    if not workspace.assets.exists():
        raise FileNotFoundError(f"Product assets directory not found: products/{product_slug}/assets")
    return workspace


def create_product_workspace(repo_root: Path | str, product_slug: str) -> ProductWorkspace:
    """Create the standard product-level workspace structure."""
    workspace = resolve_product_workspace(repo_root, product_slug)
    workspace.root.mkdir(parents=True, exist_ok=True)
    if not workspace.product_brief.exists():
        workspace.product_brief.write_text(_default_product_brief(product_slug), encoding="utf-8")

    for name in ASSET_DIRS:
        _ensure_kept_dir(workspace.assets / name)
    for name in OUTPUT_DIRS:
        _ensure_kept_dir(workspace.outputs / name)
    for name in PUBLISH_DIRS:
        _ensure_kept_dir(workspace.publish / name)
    return workspace


def existing_global_flow_paths(agent_root: Path | str) -> dict[str, Path]:
    """Return legacy global paths that remain supported during transition."""
    root = Path(agent_root)
    return {
        "inputs": root / "inputs",
        "outputs": root / "outputs",
        "raw_videos": root / "inputs" / "raw_videos",
        "product_images": root / "inputs" / "product_images",
        "product_briefs": root / "inputs" / "product_briefs",
        "renders": root / "outputs" / "renders",
    }


def _ensure_kept_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    keep = path / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")


def _default_product_brief(product_slug: str) -> str:
    return (
        f"# {product_slug}\n\n"
        "Product-specific brief placeholder. Keep source materials, outputs, publish records, "
        "and feedback data isolated under this product folder.\n"
    )
