#!/usr/bin/env python3
"""Create the submission folder layout for the redo.

The expected structure is:

  countries/
    default/
    mod/
    embed/

  size200/
    default/
    mod/
    embed/

  size300/
    default/
    mod/
    embed/

  size400/
    default/
    mod/
    embed/

This script only creates directories; it does not move or copy any files.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def create_layout(root: Path, sizes: list[int]) -> list[Path]:
    created: list[Path] = []

    groups = ["countries", *[f"size{size}" for size in sizes]]
    variants = ["default", "mod", "embed"]

    for group in groups:
        group_dir = root / group
        group_dir.mkdir(parents=True, exist_ok=True)
        for variant in variants:
            variant_dir = group_dir / variant
            variant_dir.mkdir(parents=True, exist_ok=True)
            created.append(variant_dir)

    return created


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create the folder structure for the CSE 327 redo."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory where the folders should be created.",
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[200, 300, 400],
        help="Numeric size folders to create. Default: 200 300 400",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    created = create_layout(root, args.sizes)

    print(f"Created or confirmed {len(created)} variant folders under {root}")
    for path in created:
        print(path.relative_to(root))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
