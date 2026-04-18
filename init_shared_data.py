#!/usr/bin/env python3
"""Initialize the shared, non-training data for each KB.

This script performs the notebook steps that should stay consistent across the
default, modified, and embed-size experiments:

* build the vocabulary from the KB
* generate the deductive closure and train/test queries
* generate the scoring-model training examples

It does not train the embedding model, train the scoring model, or run
evaluation.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from tqdm import tqdm


def run_cmd(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def init_dataset(kb_path: Path, out_dir: Path, copy_kb: bool = True) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    if copy_kb:
        shutil.copy2(kb_path, out_dir / kb_path.name)

    vocab_path = out_dir / "vocab.pkl"
    facts_path = out_dir / "all_facts.txt"
    train_queries_path = out_dir / "train_queries.txt"
    test_queries_path = out_dir / "test_queries.txt"
    train_examples_path = out_dir / "mr_train_examples.csv"

    python = sys.executable
    kbencoder = str(Path(__file__).with_name("kbencoder.py"))

    commands = [
        [
            python,
            kbencoder,
            "--kb_path",
            str(kb_path),
            "--vocab_from_kb",
            "--save_vocab",
            "--vocab_file",
            str(vocab_path),
        ],
        [
            python,
            kbencoder,
            "--kb_path",
            str(kb_path),
            "-g",
            "--facts_file",
            str(facts_path),
            "--train_query_path",
            str(train_queries_path),
            "--test_query_path",
            str(test_queries_path),
        ],
        [
            python,
            kbencoder,
            "--kb_path",
            str(kb_path),
            "-p",
            "--train_example_path",
            str(train_examples_path),
            "--train_query_path",
            str(train_queries_path),
        ],
    ]

    for cmd in commands:
        run_cmd(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize the shared KB data files for the redo."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repo root that contains the KB folders. Default: current directory.",
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[200, 300, 400],
        help="Random KB sizes to initialize. Default: 200 300 400",
    )
    parser.add_argument(
        "--no-copy-kb",
        action="store_false",
        dest="copy_kb",
        help="Do not copy the KB text file into the destination folder.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    tasks: list[tuple[str, Path, Path]] = [
        (
            "countries",
            root / "countries" / "countries_kb.txt",
            root / "data" / "countries",
        )
    ]
    tasks.extend(
        (
            f"size{size}",
            root / f"size{size}" / "randomKB.txt",
            root / "data" / "random" / f"size{size}",
        )
        for size in args.sizes
    )

    for label, kb_path, out_dir in tqdm(tasks, desc="Initializing KB data", unit="kb"):
        if not kb_path.exists():
            raise FileNotFoundError(f"Missing KB file: {kb_path} ({label})")
        init_dataset(kb_path, out_dir, copy_kb=args.copy_kb)
        print(f"Initialized {label} -> {out_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
