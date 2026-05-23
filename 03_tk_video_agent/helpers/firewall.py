"""Standalone path firewall helpers.

This module does not integrate with business generation commands yet. It offers
small validation primitives and report generation for preflight checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any


DEFAULT_PROTECTED_PATHS = (
    "control_console",
    "00_references",
)

DEFAULT_PROTECTED_PATTERNS = (
    "products/*/assets",
    "products/*/assets/*",
    "products/*/product_brief.md",
)


@dataclass(frozen=True)
class FirewallViolation:
    """Structured description of a blocked path operation."""

    path: str
    rule: str
    reason: str
    suggested_action: str


class FirewallViolationError(RuntimeError):
    """Raised when a path violates the code-level firewall."""

    def __init__(self, violation: FirewallViolation) -> None:
        super().__init__(violation.reason)
        self.violation = violation


def validate_product_path(repo_root: Path | str, product_slug: str, candidate_path: Path | str) -> Path:
    """Validate that candidate_path stays under products/product_slug."""
    root = Path(repo_root).resolve()
    target = _resolve_under_root(root, candidate_path)
    _assert_inside_repo(root, target)
    expected_root = root / "products" / product_slug
    if _is_relative_to(target, expected_root):
        return target

    raise FirewallViolationError(
        FirewallViolation(
            path=_display_path(target, root),
            rule="product_path_scope",
            reason=f"Path is outside products/{product_slug}.",
            suggested_action=f"Write only under products/{product_slug}/outputs/ for this product.",
        )
    )


def validate_experiment_path(
    repo_root: Path | str,
    product_slug: str,
    sku_slug: str,
    batch_id: str,
    candidate_path: Path | str,
) -> Path:
    """Validate that candidate_path stays under one product/SKU/batch experiment."""
    root = Path(repo_root).resolve()
    target = _resolve_under_root(root, candidate_path)
    _assert_inside_repo(root, target)
    expected_root = root / "experiments" / product_slug / sku_slug / batch_id
    if _is_relative_to(target, expected_root):
        return target

    raise FirewallViolationError(
        FirewallViolation(
            path=_display_path(target, root),
            rule="experiment_batch_scope",
            reason=f"Path is outside experiments/{product_slug}/{sku_slug}/{batch_id}.",
            suggested_action="Write experiment records only inside the active product/SKU/batch directory.",
        )
    )


def assert_allowed_write_path(
    repo_root: Path | str,
    candidate_path: Path | str,
    allowed_roots: list[Path | str],
) -> Path:
    """Assert candidate_path is inside one of the explicit allowlist roots."""
    root = Path(repo_root).resolve()
    target = _resolve_under_root(root, candidate_path)
    _assert_inside_repo(root, target)
    resolved_allowed = [_resolve_under_root(root, allowed) for allowed in allowed_roots]
    if any(_is_relative_to(target, allowed) for allowed in resolved_allowed):
        return target

    raise FirewallViolationError(
        FirewallViolation(
            path=_display_path(target, root),
            rule="allowed_write_path",
            reason="Path is not inside any allowed write root.",
            suggested_action="Choose a module-approved output directory before writing.",
        )
    )


def assert_do_not_touch_path(
    repo_root: Path | str,
    candidate_path: Path | str,
    protected_roots: list[Path | str] | None = None,
) -> Path:
    """Block writes to protected roots such as control_console."""
    root = Path(repo_root).resolve()
    target = _resolve_under_root(root, candidate_path)
    _assert_inside_repo(root, target)
    protected_pattern = _matching_protected_pattern(target, root)
    if protected_pattern:
        rule = "do_not_touch_product_assets" if "assets" in protected_pattern else "do_not_touch_product_brief"
        raise FirewallViolationError(
            FirewallViolation(
                path=_display_path(target, root),
                rule=rule,
                reason=f"Path matches protected pattern: {protected_pattern}.",
                suggested_action="Request explicit user approval before changing product source assets or briefs.",
            )
        )
    protected = list(protected_roots or DEFAULT_PROTECTED_PATHS)
    resolved_protected = [_resolve_under_root(root, item) for item in protected]
    for protected_root in resolved_protected:
        if _is_relative_to(target, protected_root):
            raise FirewallViolationError(
                FirewallViolation(
                    path=_display_path(target, root),
                    rule="do_not_touch_path",
                    reason=f"Path is protected: {_display_path(protected_root, root)}.",
                    suggested_action="Request explicit user approval before modifying protected strategy or source paths.",
                )
            )
    return target


def generate_preflight_report(
    repo_root: Path | str,
    product_slug: str,
    sku_slug: str,
    batch_id: str,
    output_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Generate a preflight Markdown report for the current product/SKU/batch."""
    root = Path(repo_root).resolve()
    destination = _resolve_under_root(root, output_dir or "project_journal/errors")
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / f"firewall_preflight_{product_slug}_{sku_slug}_{batch_id}.md"

    allowlist = [
        root / "products" / product_slug / "outputs",
        root / "experiments" / product_slug / sku_slug / batch_id,
        root / "project_journal" / "errors",
    ]
    denylist = [
        root / "control_console",
        root / "00_references",
        root / "products" / product_slug / "assets",
        root / "products" / product_slug / "product_brief.md",
    ]

    lines = [
        "# Firewall Preflight Report",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Product: `{product_slug}`",
        f"- SKU: `{sku_slug}`",
        f"- Batch: `{batch_id}`",
        "",
        "## Allowlist",
        "",
    ]
    lines.extend(f"- `{_display_path(path, root)}`" for path in allowlist)
    lines.extend(["", "## Denylist", ""])
    lines.extend(f"- `{_display_path(path, root)}`" for path in denylist)
    lines.extend(
        [
            "",
            "## Result",
            "",
            "- Preflight-only report generated. The firewall is not yet integrated into production business commands.",
            "- This command does not execute business generation steps.",
            "- Any future write should call the firewall assertion helpers before creating files.",
        ]
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "report_path": report_path,
        "allowlist": [_display_path(path, root) for path in allowlist],
        "denylist": [_display_path(path, root) for path in denylist],
    }


def generate_firewall_violation_report(
    repo_root: Path | str,
    violation: FirewallViolation,
    output_dir: Path | str | None = None,
) -> Path:
    """Write a Markdown report for one firewall violation."""
    root = Path(repo_root).resolve()
    destination = _resolve_under_root(root, output_dir or "project_journal/errors")
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / "firewall_violation_report.md"
    lines = [
        "# Firewall Violation Report",
        "",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Violating path: `{violation.path}`",
        f"- Triggered rule: `{violation.rule}`",
        f"- Reason: {violation.reason}",
        f"- Suggested action: {violation.suggested_action}",
        "",
        "## Boundary",
        "",
        "- Dangerous writes were not executed.",
        "- This report is written under `project_journal/errors/`, not `control_console/`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def run_firewall_check(repo_root: Path | str, product_slug: str, sku_slug: str, batch_id: str) -> dict[str, Any]:
    """Run a standalone firewall preflight check."""
    root = Path(repo_root).resolve()
    allowed_paths = [
        root / "products" / product_slug / "outputs" / "material_inventory" / "material_inventory.json",
        root / "experiments" / product_slug / sku_slug / batch_id / "01_variants.csv",
    ]
    protected_probe = root / "control_console" / "00_MASTER_CONTROL.md"

    try:
        for path in allowed_paths:
            assert_do_not_touch_path(root, path)
        validate_product_path(root, product_slug, allowed_paths[0])
        validate_experiment_path(root, product_slug, sku_slug, batch_id, allowed_paths[1])
        assert_allowed_write_path(
            root,
            allowed_paths[0],
            [root / "products" / product_slug / "outputs"],
        )
        assert_allowed_write_path(
            root,
            allowed_paths[1],
            [root / "experiments" / product_slug / sku_slug / batch_id],
        )
        try:
            assert_do_not_touch_path(root, protected_probe)
        except FirewallViolationError:
            pass
        else:
            raise FirewallViolationError(
                FirewallViolation(
                    path=_display_path(protected_probe, root),
                    rule="do_not_touch_probe_failed",
                    reason="Protected control_console path was not blocked.",
                    suggested_action="Review assert_do_not_touch_path protected roots.",
                )
            )
        preflight = generate_preflight_report(root, product_slug, sku_slug, batch_id)
        return {"status": "pass", "preflight_report": preflight["report_path"], "violation_report": None}
    except FirewallViolationError as exc:
        violation_report = generate_firewall_violation_report(root, exc.violation)
        return {"status": "failed", "preflight_report": None, "violation_report": violation_report, "violation": exc.violation}


def _resolve_under_root(repo_root: Path, path: Path | str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return candidate.resolve()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _assert_inside_repo(repo_root: Path, target: Path) -> None:
    if not _is_relative_to(target, repo_root):
        raise FirewallViolationError(
            FirewallViolation(
                path=_display_path(target, repo_root),
                rule="outside_repo_root",
                reason="Path resolves outside the repository root.",
                suggested_action="Use a path inside the current workspace.",
            )
        )


def _matching_protected_pattern(path: Path, root: Path) -> str | None:
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError:
        return None
    for pattern in DEFAULT_PROTECTED_PATTERNS:
        if fnmatchcase(relative, pattern):
            return pattern
    return None


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()

