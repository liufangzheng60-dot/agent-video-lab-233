"""Command line entry point for the TikTok product video agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from helpers.build_material_pack import run_material_pack
from helpers.inventory import run_inventory


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok product video agent utilities.")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("inventory", help="Scan local input materials and write inventory reports.")
    subparsers.add_parser("material-pack", help="Build an Agent-readable material pack from inventory outputs.")

    args = parser.parse_args()
    project_root = Path(__file__).resolve().parent

    if args.command == "inventory":
        result = run_inventory(project_root)
        inventory = result["inventory"]
        print(f"Material inventory generated: {inventory['file_count']} files")
        print(f"JSON: {result['json_path']}")
        print(f"Markdown: {result['markdown_path']}")
        return

    if args.command == "material-pack":
        result = run_material_pack(project_root)
        material_pack = result["material_pack"]
        print(f"Material pack generated: {material_pack['material_count']} materials")
        print(f"JSON: {result['json_path']}")
        print(f"Markdown: {result['markdown_path']}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
