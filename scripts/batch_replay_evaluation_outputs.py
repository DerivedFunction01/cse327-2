#!/usr/bin/env python3
"""Replay learned evaluation outputs for every learned-model CSV.

This regenerates console-style output files from saved `ming-*.csv` files
without rerunning inference. It skips standard reasoner CSVs entirely and
reads each folder's sibling `test_queries.txt`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tqdm import tqdm

from replay_evaluation_output import main as replay_main


def _query_file_for_csv(csv_path: Path) -> Path:
    query_file = csv_path.parent / "test_queries.txt"
    if query_file.exists():
        return query_file.resolve()

    kb_root = csv_path.parent.parent
    kb_name = kb_root.name
    if kb_name == "countries":
        fallback = csv_path.parents[2] / "data" / "countries" / "test_queries.txt"
    else:
        fallback = csv_path.parents[2] / "data" / "random" / kb_name / "test_queries.txt"

    if fallback.exists():
        return fallback.resolve()

    raise FileNotFoundError(
        f"Missing test query file next to CSV: {query_file} (and fallback {fallback})"
    )


def _iter_ming_csvs(root: Path) -> list[Path]:
    csvs: list[Path] = []
    for path in sorted(root.rglob("ming-*.csv")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        csvs.append(path)
    return csvs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay every learned-model CSV using the saved query logs."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to scan recursively. Default: current directory.",
    )
    parser.add_argument(
        "--output-suffix",
        default=".replay.txt",
        help="Suffix to append to each replay output file.",
    )
    parser.add_argument(
        "--device-label",
        default="cuda",
        help="Device label to echo in the replay header.",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Skip header lines in the replay output.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    csv_paths = _iter_ming_csvs(root)
    if not csv_paths:
        print(f"No ming CSV files found under {root}")
        return 1

    for csv_path in tqdm(csv_paths, desc="Replaying outputs", unit="file"):
        query_file = _query_file_for_csv(csv_path)

        output_path = csv_path.with_suffix("")
        output_path = output_path.with_name(output_path.name + args.output_suffix)

        replay_args = [
            "--csv",
            str(csv_path),
            "--qfile",
            str(query_file),
            "--output",
            str(output_path),
            "--device-label",
            args.device_label,
        ]
        if args.no_header:
            replay_args.append("--no-header")

        # Call the underlying script entrypoint directly so we don't fork shell
        # logic or duplicate the replay formatting code.
        import sys

        old_argv = sys.argv
        try:
            sys.argv = ["replay_evaluation_output.py", *replay_args]
            rc = replay_main()
            if rc != 0:
                return rc
        finally:
            sys.argv = old_argv

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
