"""Command line entry point for the TikTok product video agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from helpers.inventory import run_inventory


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok product video agent utilities.")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("inventory", help="Scan local input materials and write inventory reports.")

    args = parser.parse_args()
    if args.command == "inventory":
        result = run_inventory(Path(__file__).resolve().parent)
        inventory = result["inventory"]
        print(f"Material inventory generated: {inventory['file_count']} files")
        print(f"JSON: {result['json_path']}")
        print(f"Markdown: {result['markdown_path']}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
