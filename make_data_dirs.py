#!/usr/bin/env python3
"""Create the shared data folder layout for the redo.

The expected structure is:

  data/
    countries/
    random/

This script only creates directories; it does not move or copy any files.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def create_layout(root: Path) -> list[Path]:
    created: list[Path] = []
    for name in ["countries", "random"]:
        path = root / "data" / name
        path.mkdir(parents=True, exist_ok=True)
        created.append(path)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create the shared data folder structure for the CSE 327 redo."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory where the folders should be created.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    created = create_layout(root)

    print(f"Created or confirmed {len(created)} data folders under {root / 'data'}")
    for path in created:
        print(path.relative_to(root))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
